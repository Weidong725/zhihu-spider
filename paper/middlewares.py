# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

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
from scrapy import signals
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet.error import ConnectionDone, ConnectionLost, DNSLookupError, TCPTimedOutError


# 代理ip
class IpProxyDownloadMiddleware(object):

    def __init__(self):
        self.url = 'http://api.xdaili.cn/xdaili-api//newExclusive/getIp?spiderId=db855665f15644c694c19125bd4eb158&orderno=DX20209283916R7Gb5k&returnType=2&count=1&machineArea='
        self.proxy = ''
        self.expire_datetime = datetime.datetime.now() - datetime.timedelta(seconds=15)

    def _get_proxyip(self):
        response = requests.get(self.url)
        info = json.loads(response.text)
        for item in info['RESULT']:
            IP = item['ip']
            PORT = item['port']
            proxy = IP + ':' + PORT
            self.proxy = proxy
            self.expire_datetime = datetime.datetime.now() + datetime.timedelta(seconds=15)

    def _check_expire(self):
        if datetime.datetime.now() >= self.expire_datetime:
            self._get_proxyip()
            print('=====================', "切换代理IP：" + self.proxy)

    def process_request(self, spider, request):
        self._check_expire()
        request.meta['proxy'] = "http://"+self.proxy


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    # def process_response(self, request, response, spider):
    #     # 捕获状态码为40x/50x的response
    #     if str(response.status).startswith('4') or str(response.status).startswith('5'):
    #         # 随意封装，直接返回response，spider代码中根据url==''来处理response
    #         response = HtmlResponse(url='')
    #         return response
    #     # 其他状态码不处理
    #     return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s' % (exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response
        # 打印出未捕获到的异常
