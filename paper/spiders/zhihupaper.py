# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from paper.items import PaperItem
from pprint import pprint
from datetime import datetime
import json
import re
import time
import copy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from twisted.internet.error import ConnectionRefusedError
import pygame
import time


class ZhihupaperSpider(Spider):
    name = 'zhihupaper'

    start_urls = ['http://www.zhihu.com/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'paper.middlewares.ProcessAllExceptionMiddleware': 544,
        }
    }

    def start_requests(self):
        # question_id = str(341910651)
        question_id = input("请输入问题编号：")
        include = 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics'
        url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers?include={include}&limit=5&offset=0&platform=desktop&sort_by=default'
        # cookies = '_zap=0e9a1227-2310-4881-86fb-88389f6600ff; d_c0="AHClr_HslxCPTo_Rh6lMGnTD9ox_d8dc3rE=|1577853458"; _ga=GA1.2.1140736772.1584584324; __utmv=51854390.100--|2=registration_date=20161120=1^3=entry_date=20161120=1; _xsrf=CAHcdJpWgZ4AqYAdo1ZH1xBzEmzmUVlF; q_c1=cb84721714fd4d97b5ca67282ff6ea53|1596980905000|1578645063000; capsion_ticket="2|1:0|10:1598281628|14:capsion_ticket|44:NDE1Zjg4NjI5NjFiNDI2ZWIyNGU0MzU3YjkxODNhZjM=|d3c473abcf57bc9ed55dd2affed9f852a61cf28d6028399b95ea788375a0630c"; z_c0="2|1:0|10:1598281630|4:z_c0|92:Mi4xd3FhMkF3QUFBQUFBY0tXdjhleVhFQ1lBQUFCZ0FsVk5uaVV4WUFEME5nRlpZelRmbmR6QUlZVUR0TUM4ams1Um1B|77f233463541c4b9fc31a6a9b42b5f88163ef18b4303fd70456f44a1eca16e97"; tst=h; _gid=GA1.2.1510045404.1599306524; tshl=; __utma=51854390.1140736772.1584584324.1598528992.1599375982.6; __utmz=51854390.1599375982.6.3.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/313964070; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1599486275,1599488570,1599488736,1599535405; SESSIONID=5pwuaHLszXu6pXNArIfJUYI3GLZSMQVw4Omdvj3KhDc; JOID=VlkSA0g7TLr2FYwxTT9Oa5wP3aNfCzrKgHPBezlGEcnHZtN6CvlG6a0XjzBJX6eB65Banw7InWfausewzI_Fmqo=; osd=UFsUBEM9TrzxHoozSzhFbZ4J2qhZCTzNi3XDfT5NF8vBYdh8CP9B4qsViTdCWaWH7JtcnQjPlmHYvMC7yo3DnaE=; _gat_gtag_UA_149949619_1=1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1599541707; KLBRSID=af132c66e9ed2b57686ff5c489976b91|1599541720|1599535403'
        # cookies = {i.split("=")[0]:i.split("=")[1] for i in cookies.split("; ")}
        yield Request(
            url.format(question_id=question_id, include=include), callback=self.parse, headers={'referer': 'https://www.zhihu.com/question/'+question_id}
        )

    def parse(self, response):
        """问答对页面"""
        response = json.loads(response.text)
        item = PaperItem()  # 实例化item类型对象
        for data in response['data']:
            item['author_name'] = data['author']['name']
            item['author_id'] = data['id']
            item['gender'] = data['author']['gender']

            content = data['content']
            if content is not None:
                img_url = re.findall(
                    "data-default-watermark-src=\"(.*?)\"", content)  # 回答内容中包含的图片链接列表
                hyper_links = re.findall(
                    "a href=\"(.*?)\"", content)  # 回答内容中包含的超链接地址列表
                item["img_counts"] = len(img_url)  # 显示图片数量
                item["link_counts"] = len(hyper_links)  # 显示超链接数量
                item["content"] = re.sub(
                    "<.*?>|\s|--|=", "", content)  # 提出html标签的纯净答案文本
                item["word_counts"] = len(item["content"])

            item['voteup_count'] = data['voteup_count']  # 答案获得赞同数
            item['com_count'] = data['comment_count']  # 答案评论数
            item['q_title'] = data['question']['title']  # 答案标题
            item['q_id'] = data['question']['id']  # 答案标题
            item['q_created_time'] = data['question']['created']  # 问题创建时间戳
            item['created_time'] = data['created_time']  # 答案发布时间时间戳
            item['updated_time'] = data['updated_time']  # 答案修改时间时间戳
            can_comment = data['can_comment']['reason']  # 是否设置评论权限
            item['can_comment'] = can_comment if can_comment != '' else 0
            item['url_token'] = data['author']['url_token']  # 访问回答者详情页所需

            pprint(item)
            print('■'*50)
            yield item

        # ——————请求下一页—————— #
        if response['paging']['is_end'] == False:
            next_url = response['paging']['next']
            yield Request(next_url, callback=self.parse, errback=self.errback)
        else:
            print('■'*10+'爬取完毕'+'■'*10)
            self.play_music(r'C:\Users\WD\Desktop\yinxiao.mp3')

    def play_music(self, file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        time.sleep(2)
        pygame.mixer.music.stop()

    def errback(self, failure):
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

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
