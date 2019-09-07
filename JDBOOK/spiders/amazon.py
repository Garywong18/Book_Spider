# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import html

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    start_urls = ['https://www.amazon.cn/gp/book/all_category/ref=sv_b_0']

    def parse(self, response):
        blist = response.xpath("//div[@id='content']/div[@class='a-row a-size-base']")
        for div in blist:
            item = {}
            item['blist_name'] = div.xpath(".//a[@class='a-link-nav-icon']/@title").extract_first()
            tr_list = div.xpath(".//div[@class='a-column a-span9 a-text-center']/table/tr")
            for tr in tr_list:
                slist = tr.xpath("./td")
                for td in slist:
                    item['slist_name'] = td.xpath("./a/@title").extract_first()
                    slist_href = td.xpath("./a/@href").extract_first()
                    if slist_href is not None:
                        yield scrapy.Request(
                            slist_href,
                            callback=self.parse_list,
                            meta={'item':deepcopy(item)}
                        )

    def parse_list(self,response):
        item = response.meta['item']
        book_list = response.xpath("//div[@id='mainResults']/ul/li")
        for li in book_list:
            item['book_name'] = li.xpath(".//div[@class='a-fixed-left-grid-col a-col-right']/div/div/a/@title").extract_first()
            # 源码中将title进行了特殊的Unicode编码，所以此处要进行解码
            item['book_name'] = html.unescape(item['book_name'])
            item['book_author'] = li.xpath(".//div[@class='a-row a-spacing-small']/div[2]//text()").extract()
            item['book_price'] = li.xpath(".//div[@class='a-column a-span7']/div[2]/a/span[2]/text()").extract_first()
            yield item
        next_page = response.xpath("//a[@id='pagnNextLink']/@href").extract_first()
        if next_page is not None:
            next_page = 'https://www.amazon.cn' + next_page
            yield scrapy.Request(
                next_page,
                callback=self.parse_list,
                meta={'item':item}
            )