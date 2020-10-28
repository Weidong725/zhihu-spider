from scrapy import Spider, Request
from paper.items import PaperItem
from pprint import pprint
import json


class QIdSpider(Spider):
    name = 'q_id'
    # allowed_domains = ['zhihu.com']
    start_urls = [
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/science?limit=50&desktop=true',
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/digital?limit=50&desktop=true',
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/sport?limit=50&desktop=true',
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/fashion?limit=50&desktop=true',
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/school?limit=50&desktop=true',
        'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true'
    ]

    def parse(self, response):
        response = json.loads(response.text)
        item = PaperItem()
        for i in response['data']:
            item['q_id'] = i['target']['id']
            print(item)
            print('✦'*20)
            yield item
