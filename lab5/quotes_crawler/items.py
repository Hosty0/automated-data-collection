import scrapy


class QuoteItem(scrapy.Item):
    quote = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    author_birth_date = scrapy.Field()
    author_birth_location = scrapy.Field()
    author_bio = scrapy.Field()
    author_url = scrapy.Field()
    source_url = scrapy.Field()
