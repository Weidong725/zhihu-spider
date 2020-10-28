# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from fake_useragent import UserAgent
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.web.client import ResponseFailed
from scrapy.http import HtmlResponse
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.internet import defer
import json
import requests
import datetime
from requests.api import request
from requests.models import Response
from scrapy import signals, Spider, Request
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet.error import ConnectionDone, ConnectionLost, DNSLookupError, TCPTimedOutError
import random
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import paper.settings as settings
import time
# 代理ip


class IpProxyDownloadMiddleware(object):
    def __init__(self):
        proxy_info = get_proxyip()
        settings.CURRENT_PROXY = proxy_info

    def process_request(self, request, spider):
        if settings.CURRENT_PROXY:
            request.meta['proxy'] = settings.CURRENT_PROXY
        else:
            # 切换代理
            switch_proxy()

    def process_response(self, request, response, spider):
        if response.status != 200:
            # 切换代理
            proxy_result = switch_proxy()
            return request

        return response


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 请求异常，切换代理
            switch_proxy()
            new_request = request.copy()
            new_request_l = new_request.replace(url=request.url)
            return new_request_l


def switch_proxy():
    """切换代理"""
    proxy_info = get_proxyip()
    print('=====================', "切换代理IP：" + proxy_info)
    settings.CURRENT_PROXY = proxy_info


def get_proxyip():
    """获取代理ip"""
    ip_info = requests.get(
        url='http://api.wandoudl.com/api/ip?app_key=7831924116933cfce80669d32325e2e3&pack=0&num=1&xy=1&type=2&lb=\r\n&mr=2&')
    try:
        info = json.loads(ip_info.text)
        for item in info['data']:
            IP = item['ip']
            PORT = item['port']
            proxy = IP + ':' + PORT
            return "http://" + proxy
    except:
        print("代理为空")
# class IpProxyDownloadMiddleware(object):
#     ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
#                       ConnectionRefusedError, ConnectionDone, ConnectError,
#                       ConnectionLost, TCPTimedOutError, ResponseFailed,
#                       IOError, TunnelError)

#     def __init__(self):
#         self.url = 'https://proxyapi.horocn.com/api/v2/proxies?order_id=RZUX1681426582323011&num=1&format=json&line_separator=win&can_repeat=yes&user_token=d2b6063241a92dd7f566b5084aa3b77a'
#         self.proxy = ''
#         self.information = self.information_func()

#     def information_func(self):
#         return time.time() + 1.5

#     def _get_proxyip(self):
#         response = requests.get(self.url)
#         try:
#             info = json.loads(response.text)
#             for item in info['data']:
#                 IP = item['host']
#                 PORT = item['port']
#                 proxy = IP + ':' + PORT
#                 self.proxy = proxy
#         except:
#             print("代理为空")

#     def _check_expire(self):
#         if time.time() > self.information:
#             self._get_proxyip()
#             self.information = self.information_func()
#             print('=====================', "切换代理IP：" + self.proxy)

#     def process_request(self, spider, request):
#         self._check_expire()
#         request.meta['proxy'] = "http://"+self.proxy

#     def process_response(self, request, response, spider):
#         if len(response.text) < 3000 or response.status in [403, 400, 405, 301, 302]:
#             spider.logger.info("[此代理报错]   {}".format(self.proxy))
#             new_proxy = self._get_proxyip()
#             self.proxy = new_proxy
#             spider.logger.info("[更的的新代理为]   {}".format(self.proxy))
#             new_request = request.copy()
#             new_request_l = new_request.replace(url=request.url)
#             return new_request_l
#         return response

#     def process_exception(self, request, exception, spider):
#         # 捕获几乎所有的异常
#         if isinstance(exception, self.ALL_EXCEPTIONS):
#             # 在日志中打印异常类型
#             source = request.meta.get("source", "xxx")
#             spider.logger.info("[Got exception]   {}".format(exception))
#             spider.logger.info("[需要更换代理重试]   {}".format(self.proxy))
#             new_proxy = self._get_proxyip()
#             self.proxy = new_proxy

#             spider.logger.info("[更换后的代理为]   {}".format(self.proxy))
#             new_request = request.copy()
#             new_request_l = new_request.replace(url=request.url)
#             return new_request_l

#         # 打印出未捕获到的异常
#         spider.logger.info("[not contained exception]   {}".format(exception))


class UserAgentDownloadMiddleware(object):

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    UA = random.choice(user_agent_list)

    def process_request(self, request, spider):
        UA = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = UA
