import json
import sqlite3
from pathlib import Path
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ValidationPipeline:
    """100: проверяет обязательные поля и учитывает потери."""
    required = ("quote", "author", "tags", "author_url")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        missing = [name for name in self.required if adapter.get(name) in (None, "", [])]
        if missing:
            spider.crawler.stats.inc_value("dropped/missing_fields")
            raise DropItem(f"Не заполнены обязательные поля: {', '.join(missing)}")
        return item


class CleanPipeline:
    """200: очищает текст и приводит коллекцию тегов к нормальной форме."""
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for field in ("quote", "author", "author_birth_date",
                      "author_birth_location", "author_bio", "author_url", "source_url"):
            value = adapter.get(field)
            if value is not None:
                adapter[field] = " ".join(str(value).split())
        adapter["tags"] = sorted({
            " ".join(str(tag).split()).lower()
            for tag in (adapter.get("tags") or []) if str(tag).strip()
        })
        # Дата на учебном сайте представлена текстом вида "January 1, 1900".
        # Неизвестный/пустой формат не подменяем выдуманной датой.
        return item


class DeduplicationPipeline:
    """300: бизнес-ключ — пара автор + текст цитаты, а не URL."""
    def open_spider(self, spider):
        self.seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        key = (adapter["author"].casefold(), adapter["quote"].casefold())
        if key in self.seen:
            spider.crawler.stats.inc_value("dropped/duplicates")
            raise DropItem("Повтор пары автор + цитата")
        self.seen.add(key)
        return item


class SQLitePipeline:
    """400: одно соединение на паук и пакетная запись executemany."""
    def open_spider(self, spider):
        db_path = Path(spider.settings.get("SQLITE_PATH", "data/crawl.db"))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.buffer = []
        self.batch_size = spider.settings.getint("SQLITE_BATCH_SIZE", 50)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL,
                author TEXT NOT NULL,
                tags TEXT NOT NULL,
                author_birth_date TEXT,
                author_birth_location TEXT,
                author_bio TEXT,
                author_url TEXT NOT NULL,
                source_url TEXT,
                UNIQUE(author, quote)
            )
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        self.buffer.append((
            a.get("quote"), a.get("author"), json.dumps(a.get("tags") or [], ensure_ascii=False),
            a.get("author_birth_date"), a.get("author_birth_location"), a.get("author_bio"),
            a.get("author_url"), a.get("source_url")
        ))
        spider.crawler.stats.inc_value("db/queued")
        if len(self.buffer) >= self.batch_size:
            self._flush(spider)
        return item

    def _flush(self, spider):
        if not self.buffer:
            return
        before = self.conn.total_changes
        self.conn.executemany("""
            INSERT OR IGNORE INTO quotes
            (quote, author, tags, author_birth_date, author_birth_location,
             author_bio, author_url, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, self.buffer)
        self.conn.commit()
        inserted = self.conn.total_changes - before
        spider.crawler.stats.inc_value("db/rows_written", inserted)
        self.buffer.clear()

    def close_spider(self, spider):
        self._flush(spider)
        self.conn.close()
