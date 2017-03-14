# -*- coding: utf-8 -*-
import re
import json
import scrapy
from isetan.items import IsetanItem
from datetime import date

class IsetanSpiderSpider(scrapy.Spider):
    name = "radar"
    allowed_domains = ["isetan.mistore.jp"]
    start_urls = ['http://isetan.mistore.jp']

    def parse(self, response):
        for menu in response.xpath('//div[@class="nav-global"]/ul/li'):
            gender = menu.xpath('@class').extract()
            for href in menu.xpath('div/div/ul/li/a/@href'):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse_items_page, meta={'gender' : gender})
    def parse_items_page(self, response):
        for item in response.xpath('//div[@class="inner"]/p[@class="text"]'):
            product = IsetanItem()
            prod_url = item.xpath('a/@href').extract_first()
            product["product_code"] = re.search('/(\d+).html', prod_url).groups(0)[0]
            product["gender"] = response.meta["gender"]
            product["full_price"] = 0
            product["price"] = item.xpath('a/span[contains(@class, "price")]/text()').extract_first().replace(u'\u5186', '')
            product["currency"] = "YEN"
            product["country"] = "JAPAN"
            product["item_url"] = prod_url
            product["brand"] = item.xpath('a/span[@class="brandName"]/text()').extract()
            product["website"] = "ISETAN ONLINE STORE"
            product["date"] = date.today().strftime('%Y%m%d')
            product["price_max"] = 0
            yield product
        next_page = response.xpath('//li[@class="next"][1]/a/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback=self.parse_items_page, meta=response.meta)