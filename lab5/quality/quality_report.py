"""Формирует сводку качества по SQLite без сторонних библиотек."""
import sqlite3
from pathlib import Path

db = Path("data/crawl.db")
con = sqlite3.connect(db)
total = con.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
print("Всего записей:", total)
for field in ["quote", "author", "tags", "author_birth_date", "author_birth_location", "author_bio"]:
    n = con.execute(f"SELECT COUNT(*) FROM quotes WHERE {field} IS NOT NULL AND trim({field}) != ''").fetchone()[0]
    print(f"Полнота {field}: {n}/{total} ({(100*n/total if total else 0):.1f}%)")
print("\\nТоп авторов:")
for author, n in con.execute("SELECT author, COUNT(*) FROM quotes GROUP BY author ORDER BY 2 DESC LIMIT 10"):
    print(f"{author}: {n}")
print("\\nТоп тегов:")
rows = con.execute("SELECT tags FROM quotes").fetchall()
from collections import Counter
counter = Counter()
import json
for (raw,) in rows:
    counter.update(json.loads(raw or "[]"))
for tag, n in counter.most_common(10):
    print(f"{tag}: {n}")
con.close()
