# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy

class DangdangSpider(scrapy.Spider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    start_urls = ['http://book.dangdang.com/']

    def parse(self, response):
        #获取大分类
        blist = response.xpath("//div[@class='con flq_body']/div[position()>1]")
        for div in blist:
            item = {}
            item['b_name'] = div.xpath("./dl/dt//text()").extract()
            item['b_name'] = [i.strip() for i in item['b_name'] if len(i.strip())>0]
            #获取中分类
            mlist = div.xpath("./div//dl[@class='inner_dl']")
            for dl in mlist:
                item['m_name'] = dl.xpath("./dt//text()").extract()
                item['m_name'] = [i.strip() for i in item['m_name'] if len(i.strip())>0]
                #获取小分类
                slist = dl.xpath("./dd/a")
                for a in slist:
                    item['s_name'] = a.xpath("./@title").extract_first()
                    item['s_href'] = a.xpath("./@href").extract_first()
                    if item['s_href'] is not None:
                        yield scrapy.Request(
                            item['s_href'],
                            callback=self.parse_list,
                            meta={'item':deepcopy(item)}
                        )
     # 解析图书列表页
    def parse_list(self,response):
        item = response.meta['item']
        book_list = response.xpath("//ul[@class='bigimg']/li")
        for li in book_list:
            item['book_name'] = li.xpath("./a/@title").extract_first()
            item['publish_company'] = li.xpath(".//p[@class='search_book_author']/span[3]/a/text()").extract_first()
            item['publish_date'] = li.xpath(".//p[@class='search_book_author']/span[2]/text()").extract_first()
            item['author'] = li.xpath(".//p[@class='search_book_author']/span[1]/a/text()").extract()
            item['price'] = li.xpath(".//span[@class='search_now_price']/text()").extract_first()
            print(item)
            yield item
        # 翻页
        next_page = response.xpath("//li[@class='next']/a/@href").extract_first()
        if next_page is not None:
            next_page = 'http://category.dangdang.com' + next_page
            yield scrapy.Request(
                next_page,
                callback=self.parse_list,
                meta={'item':item} #此处容易忘掉传递item

            )

