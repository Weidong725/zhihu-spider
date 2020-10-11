# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from paper.items import PaperItem
import json
import copy
import re
import time
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class ComSpider(Spider):
    name = 'comments'
    # allowed_domains = ['zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'paper.middlewares.ProcessAllExceptionMiddleware': 544, }
    }

    def start_requests(self):
        q_list = [298688205, 370426732, 22895671, 415358912, 29129310, 280348701, 25023570, 33511209, 35781319, 423266051, 21263953, 271011718, 263813215, 347347700, 50343728, 22238159, 31524027, 47429276, 270455074, 61163759, 33634376, 339284544, 411897686, 20883403, 24245141, 26637304, 49126610, 21028329, 53613628, 66519221, 33267404, 30173526, 26980862, 63569860, 33831407, 25867086,
                  34977654, 65976645, 269939406, 35173498, 26013806, 63167728, 401446227, 268995396, 364045623, 423320051, 422360109, 360686748, 411600345, 366072657, 20826084, 293238864, 28997957, 37936013, 27673968, 46653135, 29066512, 33198609, 20122925, 21446695, 356250441, 49910951, 416181991, 48110658, 423270990, 423034327, 415813610, 423251980, 419449683, 345516318, 353317828]
        for id in q_list:
            question_id = id
            include = 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics'
            url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers?include={include}&limit=5&offset=0&platform=desktop&sort_by=default'
            yield Request(
                url.format(question_id=question_id, include=include),
                callback=self.parse, dont_filter=True
            )

    def parse(self, response):
        response = json.loads(response.text)
        item = PaperItem()
        for data in response['data']:
            item['author_id'] = data['id']
            item['author_name'] = data['author']['name']
            item['q_id'] = data['question']['id']
            comment_url = 'https://www.zhihu.com/api/v4/answers/' + \
                str(item['author_id']) + \
                '/root_comments?order=normal&limit=10&offset=0&status=open'

            if item['author_id'] is not None:
                yield Request(comment_url, callback=self.comments, meta={"item": copy.deepcopy(item)})

        if response['paging']['is_end'] == False:
            next_url = response['paging']['next']
            yield Request(next_url, callback=self.parse)
        else:
            print('■'*10+'爬取完毕'+'■'*10)

    def comments(self, response):
        item = response.meta['item']
        com_list = json.loads(response.text)
        for com in com_list.get('data'):
            content = com['content']
            item["com_content"] = re.sub("<.*?>|\s", "", content)
            item['reviewer_token'] = com['author']['member']['url_token']
            print(item)
            print('■'*50)
            yield item
        if com_list['paging']['is_end'] == False:
            next_url = com_list['paging']['next']
            yield Request(next_url, callback=self.comments, meta={"item": copy.deepcopy(item)})
        else:
            print('✦'*10+'该条答案下评论爬取完毕'+'✦'*10)

    def errback(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

        elif failure.check(ConnectionRefusedError):
            request = failure.request
            self.logger.error('ConnectionRefusedError on %s', request.url)
