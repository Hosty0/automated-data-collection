import json
from pathlib import Path
import scrapy
from quotes_crawler.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        """Уровень 1: цитаты и пагинация; группируем цитаты по автору."""
        grouped = {}
        for card in response.css("div.quote"):
            quote = card.css("span.text::text").get()
            author = card.css("small.author::text").get()
            author_href = card.css("span a[href*='/author/']::attr(href)").get()
            tags = card.css("div.tags a.tag::text").getall()
            if not (quote and author and author_href):
                self.crawler.stats.inc_value("parse/list_cards_incomplete")
                continue
            author_url = response.urljoin(author_href)
            grouped.setdefault(author_url, []).append({
                "quote": quote,
                "author": author,
                "tags": tags,
                "source_url": response.url,
            })

        for author_url, quote_rows in grouped.items():
            # Передаём все цитаты автора одним контекстом, чтобы Scheduler
            # не отбросил повторные запросы к одной странице автора.
            yield response.follow(
                author_url,
                callback=self.parse_author,
                cb_kwargs={"quotes": quote_rows, "author_url": author_url},
                errback=self.request_failed,
            )

        next_href = response.css("li.next a::attr(href)").get()
        if next_href:
            yield response.follow(next_href, callback=self.parse, errback=self.request_failed)

    def parse_author(self, response, quotes, author_url):
        """Уровень 2: детальная страница автора."""
        birth_date = response.css(".author-born-date::text").get()
        birth_location = response.css(".author-born-location::text").get()
        bio = response.css(".author-description::text").get()

        for row in quotes:
            yield QuoteItem(
                quote=row.get("quote"),
                author=row.get("author"),
                tags=row.get("tags", []),
                author_birth_date=birth_date,
                author_birth_location=birth_location,
                author_bio=bio,
                author_url=author_url,
                source_url=row.get("source_url"),
            )

    def request_failed(self, failure):
        self.crawler.stats.inc_value("network/errback_failures")
        self.logger.warning("Ошибка запроса: %s", failure)

    def closed(self, reason):
        """Сохраняет статистику каждого прогона в отдельный JSON."""
        stats = self.crawler.stats.get_stats()
        out_dir = Path("data")
        out_dir.mkdir(exist_ok=True)
        existing = list(out_dir.glob("stats_*.json"))
        run_no = len(existing) + 1
        path = out_dir / f"stats_{run_no:03d}.json"
        serializable = {str(k): v for k, v in stats.items()}
        serializable["spider/close_reason"] = reason
        path.write_text(
            json.dumps(
                serializable,
                ensure_ascii=False,
                indent=2,
                default=str
            ),
            encoding="utf-8"
        )
