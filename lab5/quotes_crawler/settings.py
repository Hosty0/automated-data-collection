BOT_NAME = "quotes_crawler"
SPIDER_MODULES = ["quotes_crawler.spiders"]
NEWSPIDER_MODULE = "quotes_crawler.spiders"

# Соблюдаем robots.txt; User-Agent честно сообщает учебное назначение.
ROBOTSTXT_OBEY = True
USER_AGENT = "EducationalQuotesCrawler/1.0 (student lab; contact: student@example.invalid)"

# Умеренная нагрузка на учебный домен.
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 0.75
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

DOWNLOAD_TIMEOUT = 25
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

DEPTH_LIMIT = 20
CLOSESPIDER_ITEMCOUNT = 300
CLOSESPIDER_PAGECOUNT = 1000
CLOSESPIDER_ERRORCOUNT = 30

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [429, 500, 502, 503, 504]

ITEM_PIPELINES = {
    "quotes_crawler.pipelines.ValidationPipeline": 100,
    "quotes_crawler.pipelines.CleanPipeline": 200,
    "quotes_crawler.pipelines.DeduplicationPipeline": 300,
    "quotes_crawler.pipelines.SQLitePipeline": 400,
}

SQLITE_PATH = "data/crawl.db"
SQLITE_BATCH_SIZE = 50

FEEDS = {
    "data/items.jsonl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": False,
    }
}
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
TELNETCONSOLE_ENABLED = False
