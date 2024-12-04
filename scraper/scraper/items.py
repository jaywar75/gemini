# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class QuoteItem(scrapy.Item):
    """
    Represents a single quote scraped from the website.
    """
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()