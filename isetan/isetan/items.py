# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IsetanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_code = scrapy.Field()
    gender = scrapy.Field()
    full_price = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    country = scrapy.Field()
    item_url = scrapy.Field()
    brand = scrapy.Field()
    website = scrapy.Field()
    date = scrapy.Field(serializer = str)
    price_max = scrapy.Field()