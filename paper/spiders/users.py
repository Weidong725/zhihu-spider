from scrapy import Spider, Request
from pymongo import MongoClient
import pandas as pd
from pprint import pprint
from paper.items import PaperItem
import re
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from twisted.internet.error import ConnectionRefusedError
import time


class UsersSpider(Spider):
    name = 'users'
    # allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    # df = pd.read_csv(r'C:\Users\WD\Desktop\url_token.csv')
    # url_token = df.url_token
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'paper.middlewares.IpProxyDownloadMiddleware': 543,
            'paper.middlewares.UserAgentDownloadMiddleware': 305}
    }

    def start_requests(self):
        for i in self.url_token:
            if i != '':
                url = 'https://www.zhihu.com/people/'+i
                yield Request(
                    url, callback=self.parse, errback=self.errback
                )

    def parse(self, response):
        div_list = response.xpath("//main[@role='main']/div")
        # div_list = response.xpath("//div[@itemprop='people']")
        item = PaperItem()
        for div in div_list:
            # -------标题信息栏-----#
            url_token = div.xpath(
                "//meta[@itemprop='url']/@content").extract_first()
            author_name = div.xpath(
                "//span[@class='ProfileHeader-name']/text()").extract_first()
            author_headline = div.xpath(
                "//span[@class='ztext ProfileHeader-headline']/text()").extract_first()
            author_industry = div.xpath(
                "//div[@class='ProfileHeader-infoItem'][1]/text()").extract()
            author_academic = div.xpath(
                "//div[@class='ProfileHeader-infoItem'][2]/text()").extract()
            if url_token is not None:
                if "/org/" in url_token:
                    url_token = re.findall(r'/org/(.*)', url_token)
                    item['url_token'] = url_token[0]
                else:
                    url_token = re.findall(r'/people/(.*)', url_token)
                    item['url_token'] = url_token[0]
            item['author_name'] = author_name
            item['author_headline'] = 1 if author_headline != [] else 0
            item['author_industry'] = 1 if author_industry != [] else 0
            item['author_academic'] = 1 if author_academic != [] else 0
            # 判断是否设置自定义头像
            author_himg = div.xpath(
                "//div[@class='ProfileHeader-main']//img[@class='Avatar Avatar--large UserAvatar-inner']/@src").extract()
            if author_himg[0] == 'https://pic3.zhimg.com/da8e974dc_xl.jpg':
                item['author_himg'] = 0
            else:
                item['author_himg'] = 1
            # 判断是否设置自定义资料背景
            author_bimg = div.xpath(
                "//div[@class='ProfileHeader-userCover']/div/@class").extract()
            if author_bimg[0] == 'UserCover':
                item['author_bimg'] = 1
            else:
                item['author_bimg'] = 0

            #===============左中侧信息栏===============#
            #—————回复数、文章数、视频数、提问数、专栏数、想法数————#
            item['answer_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-answers'][1]//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))
            item['video_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-answers'][2]//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))
            item['question_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-asks']//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))
            item['article_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-posts']//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))
            item['column_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-columns']//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))
            item['idea_counts'] = int(div.xpath(
                "//ul[@role='tablist']/li[@aria-controls='Profile-pins']//span[@class='Tabs-meta']/text()").extract_first().replace(',', ''))

            #===============右侧信息栏===============#
            #———————个人成就———————#
            author_success = div.xpath("//div[@class='css-122fspz']").extract()
            if author_success != []:
                for i in author_success:
                    voteup_totals = re.findall(r'获得 (\d+|\S+) 次赞同', i)
                    item['voteup_totals'] = int(voteup_totals[0].replace(
                        ',', '')) if voteup_totals != [] else 0

                    like_totals = re.findall(r'获得 (\d+|\S+) 次喜欢，', i)
                    item['like_totals'] = int(like_totals[0].replace(
                        ',', '')) if len(like_totals) else 0

                    collect_totals = re.findall(r'，(\d+|\S+) 次收藏', i)
                    item['collect_totals'] = int(collect_totals[0].replace(
                        ',', '')) if len(collect_totals) else 0

                    professional = re.findall(r'，(\d+|\S+) 次专业认可', i)
                    item['professional'] = int(professional[0].replace(
                        ',', '')) if len(professional) else 0

                    public_editor = re.findall(
                        r'<!-- -->(\d+)<!-- -->', i)  # 参与公共编辑次数
                    item['public_editor'] = int(public_editor[0].replace(
                        ',', '')) if len(public_editor) else 0

                    exauthor = re.findall(r'优秀回答者', i)
                    item['exauthor'] = 1 if exauthor != [] else 0  # 是否为优秀回答者

                    zhihu_authen = re.findall(r'认证信息', i)
                    item['zhihu_authen'] = 1 if zhihu_authen != [
                    ] else 0  # 是否通过知乎身份认证

                    ans_included = re.findall(r' (\d+|\S+) 个回答', i)
                    arti_included = re.findall(r' (\d+|\S+) 篇文章', i)
                    item['ans_included'] = int(''.join(ans_included)) if ans_included != [
                    ] else 0  # 被知乎收录的回答数量
                    item['arti_included'] = int(
                        ''.join(arti_included)) if arti_included != [] else 0  # 被知乎收录的文章数量

                    zhihu_referee = re.findall(r'知乎众裁官', i)
                    item['zhihu_referee'] = 1 if zhihu_referee != [
                    ] else 0  # 是否被认证为知乎众裁官
            else:
                item['voteup_totals'] = 0
                item['like_totals'] = 0
                item['collect_totals'] = 0
                item['professional'] = 0
                item['public_editor'] = 0
                item['exauthor'] = 0
                item['zhihu_authen'] = 0
                item['ans_included'] = 0
                item['arti_included'] = 0
                item['zhihu_referee'] = 0

            # ----关注数与粉丝数----#i
            fs_list = div.xpath(
                "//div[@class='NumberBoard-itemInner']//strong/text()").extract()
            if fs_list != []:
                item['followed_counts'] = int(fs_list[0].replace(',', ''))
                item['fans_counts'] = int(fs_list[1].replace(',', ''))
            else:
                item['followed_counts'] = 0
                item['fans_counts'] = 0

            # 用户举办的live数量或关注的各类信息列表
            light_list = div.xpath(
                "//div[@class='Profile-lightList']//a/span[@class='Profile-lightItemValue']").xpath('string(.)').extract()
            if len(light_list) == 5:
                item['live_counts'] = int(light_list[0].replace(',', ''))
                item['follow_topics'] = int(light_list[1].replace(',', ''))
                item['follow_columns'] = int(light_list[2].replace(',', ''))
                item['follow_questions'] = int(light_list[3].replace(',', ''))
                item['follow_favorites'] = int(light_list[4].replace(',', ''))
            elif len(light_list) == 4:
                item['live_counts'] = 0
                item['follow_topics'] = int(light_list[0].replace(',', ''))
                item['follow_columns'] = int(light_list[1].replace(',', ''))
                item['follow_questions'] = int(light_list[2].replace(',', ''))
                item['follow_favorites'] = int(light_list[3].replace(',', ''))
            elif len(light_list) == 3:
                item['live_counts'] = 0
                item['follow_topics'] = 0
                item['follow_columns'] = int(light_list[0].replace(',', ''))
                item['follow_questions'] = int(light_list[1].replace(',', ''))
                item['follow_favorites'] = int(light_list[2].replace(',', ''))
            else:
                item['live_counts'] = 0
                item['follow_topics'] = 0
                item['follow_columns'] = 0
                item['follow_questions'] = 0
                item['follow_favorites'] = 0

            pprint(item)
            print('■'*50)
            yield item

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
