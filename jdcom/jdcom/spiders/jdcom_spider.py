# -*- coding: utf-8 -*-
import re
import json
import scrapy
from jdcom.items import JdcomItem
from datetime import date

class JdcomSpiderSpider(scrapy.Spider):
    name = "radar"
    allowed_domains = ["jd.com", "p.3.cn"]
    start_urls = ['http://www.jd.com/']

    def parse(self, response):
        for link in response.xpath('//ul[contains(@class, "JS_navCtn")]/li/a/@href'):
            url = response.urljoin(link.extract())
            yield scrapy.Request(url, callback=self.parse_sublist_page)
    def parse_sublist_page(self, response):
        if response.xpath('//div[@class="title"]'):
            for link in response.xpath('//div[@class="title"]/dl/dt/a/@href'):
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_items_page)
        elif response.xpath('//div[@class="menu"]'):
            for link in response.xpath('//div[@class="menu"]/div/h3/a/@href'):
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_items_page)
        elif response.xpath('//div[@class="mc"]'):
            for link in response.xpath('//div[@class="mc"]/div//a/@href'):
                url = response.urljoin(link.extract())
                yield scrapy.Request(url, callback=self.parse_items_page)
    def parse_items_page(self, response):
        if 'mall' in response.url:
            for item in response.xpath('//ul[@class="clearfloat"]/li/div[@class="jItem"]'):
                item_url = response.urljoin(item.xpath('div[@class="jPic"]/a/@href').extract_first())
                yield scrapy.Request(item_url, callback=self.parse_product_page)
        else:
            for item in response.xpath('//ul[contains(@class, "gl-warp")]/li[@class="gl-item"]'):
                item_url = response.urljoin(item.xpath('div/div[@class="p-img"]/a/@href').extract_first())
                yield scrapy.Request(item_url, callback=self.parse_product_page)
        next_page = response.xpath('//a[@class="fp-next"]/@href')
        if next_page:
            url = response.urljoin(next_page.extract_first())
            yield scrapy.Request(url, callback=self.parse_items_page)
    def parse_product_page(self, response):
        product = JdcomItem()
        product["product_code"] = response.url.split('/')[3].replace('.html', '')
        product["currency"] = 'RMB'
        product["country"] = 'CHINA'
        product["item_url"] = response.url
        product["website"] = "JD.COM"
        gender = response.xpath('//div[@class="w"]/div/div[3]/a/text()').extract()
        if '男装' in gender:
            product["gender"] = 'Men'
        elif '女装' in gender:
            product["gender"] = 'Women'
        else:
            product["gender"] = 'Unisex'
        product["brand"] = response.xpath('//div[@class="w"]/div/div[7]/a/text()').extract()
        product["date"] = date.today().strftime('%Y%m%d')
        price_url = "http://p.3.cn/prices/mgets?skuIds=J_" + product["product_code"]
        yield scrapy.Request(price_url, callback=self.parse_product_price, meta={'product' : product})
    def parse_product_price(self, response):
        price_data = json.loads(response.body)
        product = response.meta["product"]
        product["price"] = price_data[0]["p"]
        product["price_max"] = price_data[0]["op"]
        product["full_price"] = price_data[0]["op"]
        yield product