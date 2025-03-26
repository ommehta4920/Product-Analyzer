# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class MyScraperItem(scrapy.Item):
#     title = scrapy.Field()
#     price = scrapy.Field()
#     url = scrapy.Field()

class ProductDetails(scrapy.Item):
    p_id = scrapy.Field()
    p_name = scrapy.Field()
    p_price = scrapy.Field()
    p_currency = scrapy.Field()
    p_rating = scrapy.Field()
    p_details = scrapy.Field()
    p_available = scrapy.Field()
    p_url = scrapy.Field()
    p_images = scrapy.Field()
    c_name = scrapy.Field()
    w_name = scrapy.Field()
    w_url = scrapy.Field()