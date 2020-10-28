from scrapy import Spider, Request
from pprint import pprint
import execjs
import hashlib
import json
import re
from scrapy.http import headers
from paper.items import PaperItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from twisted.internet.error import ConnectionRefusedError
import pandas as pd
import datetime


class HIndexSpider(Spider):
    name = 'h-index'
    # allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'paper.middlewares.IpProxyDownloadMiddleware': 543,
            'paper.middlewares.UserAgentDownloadMiddleware': 542,
            'paper.middlewares.ProcessAllExceptionMiddleware': 120,
        }
    }

    def start_requests(self):
        # url_token = "nogirlnotalk"

        df = pd.read_csv(r'C:\Users\WD\Desktop\smaller.csv')
        list_url = df.url_token.unique().tolist()
        for url_token in list_url:
            url = "/api/v4/members/"+url_token + \
                "/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Cexcerpt%2Cis_labeled%2Clabel_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B*%5D.question.has_publishing_draft%2Crelationship&offset=0&limit=20&sort_by=created"
            referer = "https://www.zhihu.com/people/"+url_token+"/answers"

            headers = self.encodeX86(url_token, url, referer)

            yield Request("https://www.zhihu.com" + url, callback=self.parse, headers=headers, dont_filter=True, errback=self.errback)

    def parse(self, response):
        response = json.loads(response.text)
        item = PaperItem()
        for data in response['data']:
            item['url_token'] = data['author']['url_token']
            item['voteup_count'] = data['voteup_count']
            item['type'] = data['author']['user_type']
            item["q_id"] = data["question"]["id"]
            print(item)
            print("■"*50)
            yield item

    # ——————请求下一页—————— #
        if response['paging']['is_end'] == False:
            next_url = response['paging']['next']
            temp_url = re.findall(r"http://www.zhihu.com(.*)", next_url)[0]
            page = re.findall(r"&offset=([0-9]+)", next_url)[0]
            referer = "https://www.zhihu.com/people/" + \
                item['url_token'] + \
                "/answers?page={page:g}".format(page=int(page)/20)
            yield Request("https://www.zhihu.com"+temp_url, callback=self.parse, errback=self.errback, dont_filter=True, headers=self.encodeX86(item['url_token'], temp_url, referer)
                          )

        else:
            print("■"*50+" 该答主已爬取完毕！")

    def encodeX86(self, str_token, url, referer):
        url_token = str_token
        url = url
        referer = referer
        f = "+".join(["3_2.0", url, referer,
                      '"AHClr_HslxCPTo_Rh6lMGnTD9ox_d8dc3rE=|1577853458"'])
        fmd5 = hashlib.new('md5', f.encode()).hexdigest()

        with open(r'C:\Users\WD\Desktop\paper\paper\spiders\g_encrypt.js', 'r') as f:
            ctx1 = execjs.compile(
                f.read(), cwd=r'C:\Users\WD\AppData\Roaming\npm\node_modules\jsdom\node_modules')
        encrypt_str = ctx1.call('b', fmd5)
        headers = {
            "referer": referer,
            "cookie": 'd_c0="AHClr_HslxCPTo_Rh6lMGnTD9ox_d8dc3rE=|1577853458";',
            # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
            "x-api-version": "3.0.91",
            "x-zse-83": "3_2.0",
            "x-zse-86": "1.0_%s" % encrypt_str,
        }
        return headers

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
