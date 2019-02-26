# -*- coding: utf-8 -*-
import scrapy
from JDBOOK.items import JdbookItem
import json
from copy import deepcopy

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        # 获取大分类列表
        blist = response.xpath("//div[@class='mc']/dl/dt")
        for dt in blist:
            item = JdbookItem()
            # 获取大分类名字
            item['b_name'] = dt.xpath("./a/text()").extract_first()
            # 获取小分类列表
            slist = dt.xpath("./following-sibling::dd[1]/em")
            for em in slist:
                # 获取小分类名字和链接
                item['s_href'] = em.xpath("./a/@href").extract_first()
                item['s_name'] = em.xpath("./a/text()").extract_first()
                if item['s_href'] is not None:
                    item['s_href'] = 'https:' + item['s_href']
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_list,
                        meta={'item':deepcopy(item)}
                    )

    def parse_list(self,response):
        item = response.meta["item"]
        book_list = response.xpath("//ul[@class='gl-warp clearfix']/li")
        for li in book_list:
            item['book_sku'] = li.xpath("./div/@data-sku").extract_first()
            item['book_page'] = li.xpath(".//div[@class='p-img']/a/img/@src").extract_first()
            if item['book_page'] is not None:
                item['book_page'] = 'https:'+ item['book_page']
            item['book_author'] = li.xpath(".//span[@class='author_type_1']/a/text()").extract()
            item['publish_company'] = li.xpath(".//span[@class='p-bi-store']/a/@title").extract_first()
            item['book_name'] = li.xpath(".//div[@class='p-name']/a/em/text()").extract_first().strip()
            # 价格是通过发送新的请求得到的json数据
            price_url = 'https://p.3.cn/prices/mgets?skuIds=%2CJ_{}'.format(item['book_sku'])
            yield scrapy.Request(
                price_url, #注意要将此处的新域名添加到allowed_domains
                callback=self.parse_price,
                meta={'item':deepcopy(item)}
            )
        # 翻页
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            next_url = 'https://list.jd.com' + next_url
            yield scrapy.Request(
                next_url,
                callback=self.parse_list,
                meta={'item':item}
            )
    # 获取价格
    def parse_price(self,response):
        item = response.meta['item']
        dict_price = json.loads(response.text)[0]
        item['book_price'] = dict_price['p']
        print(item)