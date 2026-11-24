# Лабораторная работа № 5 — вариант 3

## Запуск
```bash
scrapy crawl quotes -s JOBDIR=jobstate/job_demo -s CLOSESPIDER_ITEMCOUNT=10 -s LOG_LEVEL=INFO
Get-ChildItem jobstate/job_demo -Recurse
```

Возобновление после остановки:
```bash
scrapy crawl quotes -s JOBDIR=jobstate/job_demo -s LOG_LEVEL=INFO -O data/job_resume.
Get-ChildItem jobstate/job_demo -Recurse
```

Повторное использование HTTP-кэша

Подготовка каталога кэша и логов
```bash
New-Item -ItemType Directory -Force data, logs, jobstate
Remove-Item data/httpcache -Recurse -Force -ErrorAction SilentlyContinue
```
Первый запуск
```bash
Measure-Command {
    scrapy crawl quotes `
        -O data/cache_first.jsonl `
        -s JOBDIR=jobstate/cache_run1 `
        -s HTTPCACHE_ENABLED=True `
        -s HTTPCACHE_DIR=data/httpcache `
        -s HTTPCACHE_POLICY=scrapy.extensions.httpcache.DummyPolicy `
        -s HTTPCACHE_EXPIRATION_SECS=86400 `
        -s LOG_LEVEL=INFO 2>&1 | Tee-Object logs/cache_first.log
}
```

Второй запуск
```bash
Measure-Command {
    scrapy crawl quotes `
        -O data/cache_second.jsonl `
        -s JOBDIR=jobstate/cache_run2 `
        -s HTTPCACHE_ENABLED=True `
        -s HTTPCACHE_DIR=data/httpcache `
        -s HTTPCACHE_POLICY=scrapy.extensions.httpcache.DummyPolicy `
        -s HTTPCACHE_EXPIRATION_SECS=86400 `
        -s LOG_LEVEL=INFO 2>&1 | Tee-Object logs/cache_second.log
}
```

Сравнение
```bash
Select-String -Path logs/cache_first.log, logs/cache_second.log -Pattern "httpcache/store|httpcache/hit|item_scraped_count"
```

Анализ:
```bash
python quality/quality_report.py
python quality/smoke_check.py data/stats_001.json data/stats_002.json
```

Для отладки селекторов:
```bash
scrapy shell https://quotes.toscrape.com/
```