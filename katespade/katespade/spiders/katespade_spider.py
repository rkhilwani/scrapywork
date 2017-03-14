# -*- coding: utf-8 -*-
import re
import json
import scrapy
from katespade.items import KatespadeItem
from lxml import etree
from datetime import date
from urlparse import urljoin
import urllib

class KatespadeSpiderSpider(scrapy.Spider):
    name = "radar"
    allowed_domains = ["katespade.co.uk", "fsm.attraqt.com"]
    
    def start_requests(self):
        locations = {
            'United Kingdom' : {'url' : 'http://www.katespade.co.uk/', 'currency' : 'GBP'},
            'Germany' : {'url' : 'http://www.katespade.co.uk/eur/', 'currency' : 'EUR'},
            'France' : {'url' : 'http://www.katespade.co.uk/fra', 'currency' : 'EUR'}
        }
        for loc, data in locations.iteritems():
            yield scrapy.Request(data['url'], callback=self.parse, meta={'base_url' : data['url'], 'country' : loc, 'currency' : data['currency']})

    def create_items_url(self, category, url, currency):
        base_url  = 'http://fsm.attraqt.com/zones-js.aspx?version=16.6.15'
        base_url += '&siteId=481af397-d4d4-4fc2-9523-5d6ebd636e29&UID=c2faae37-4d5f-8d4b-b38a-82c4b1ebf28d&SID=af76bbd2-6695-bf56-e01a-37ee3e07d053'
        base_url += '&pageurl=' + url
        base_url += '&zone0=category&facetmode=data&mergehash=true'
        base_url += '&currency='+currency+'&config_categorytree=shop%2F'+category+'&config_category='+category
        return base_url
    def parse(self, response):
        for href in response.xpath('//ul[@id="mm_ul"]/li'):
            sub_url = href.xpath('a/@href').extract_first()
            category = re.sub('nav', '', href.xpath('@id').extract_first())
            currency = response.meta["currency"]
            url = self.create_items_url(category, sub_url, currency)
            response.meta['category'] = category
            yield scrapy.Request(url, callback=self.parse_items_page, meta=response.meta)
    def parse_items_page(self, response):
        data = re.search('.+"html":"(.+)",.+', response.body)
        if data:
            da = data.groups()[0].replace('\\r\\n', '')
            da = da.replace('\\', '')
            html_doc = etree.HTML(da)
            for item in html_doc.xpath('//ul[@id="js-list-scroll"]/li'):
                product = KatespadeItem()
                product["product_code"] = item.xpath('@data-sku')
                product["gender"] = 'WOMEN'
                old_price = item.xpath('div[@class="prod-details"]/div[@class="prod-pricedetails"]/p/span[@id="atrwas"]/text()')
                if old_price:
                    product["full_price"] = re.search('(\d+[,\.]\d+)', old_price[0]).groups(0)
                    product["price"] = re.search('(\d+[,\.]\d+)', item.xpath('div[@class="prod-details"]/div[@class="prod-pricedetails"]/p/span[@id="price"]/text()')[0]).groups(0)
                    product["price_max"] = re.search('(\d+[,\.]\d+)', old_price[0]).groups(0)
                else:
                    product["price"] = re.search('(\d+[,\.]\d+)', item.xpath('div[@class="prod-details"]/div[@class="prod-pricedetails"]/p/span/span/text()')[0]).groups(0)
                    product["full_price"] = 0
                    product["price_max"] = 0
                product["currency"] = response.meta["currency"]
                product["country"] = response.meta["country"]
                product["item_url"] = item.xpath('div[@class="prod-details"]/h3/a/@href')
                product["brand"] = 'KATE SPADE'
                product["website"] = 'KATE SPADE'
                product["date"] = date.today().strftime('%Y%m%d')
                yield product
            for next in html_doc.xpath('//div[@class="hidden"]/a'):
                if 'Next' in next.xpath('text()'):
                    next_page = next.xpath('@href')[0]
                    
                    sub_url = urllib.quote(urljoin(response.meta["base_url"], next_page))
                    category = response.meta["category"]
                    currency = response.meta["currency"]
                    url = self.create_items_url(category, sub_url, currency)
                    yield scrapy.Request(url, callback=self.parse_items_page, meta=response.meta)