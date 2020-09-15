# -*- coding: utf-8 -*-
from scrapy import Spider,Request
from paper.items import PaperItem
from pprint import pprint
from datetime import datetime
import json 
import re
import time
import copy

class ZhihupaperSpider(Spider):
    name = 'zhihupaper'
    # allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def start_requests(self): 
        # question_id = str(341910651)
        question_id = input("请输入问题编号：")
        include = 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics'
        url = 'https://www.zhihu.com/api/v4/questions/{question_id}/answers?include={include}&limit=5&offset=0&platform=desktop&sort_by=default'
        cookies = '_zap=0e9a1227-2310-4881-86fb-88389f6600ff; d_c0="AHClr_HslxCPTo_Rh6lMGnTD9ox_d8dc3rE=|1577853458"; _ga=GA1.2.1140736772.1584584324; __utmv=51854390.100--|2=registration_date=20161120=1^3=entry_date=20161120=1; _xsrf=CAHcdJpWgZ4AqYAdo1ZH1xBzEmzmUVlF; q_c1=cb84721714fd4d97b5ca67282ff6ea53|1596980905000|1578645063000; capsion_ticket="2|1:0|10:1598281628|14:capsion_ticket|44:NDE1Zjg4NjI5NjFiNDI2ZWIyNGU0MzU3YjkxODNhZjM=|d3c473abcf57bc9ed55dd2affed9f852a61cf28d6028399b95ea788375a0630c"; z_c0="2|1:0|10:1598281630|4:z_c0|92:Mi4xd3FhMkF3QUFBQUFBY0tXdjhleVhFQ1lBQUFCZ0FsVk5uaVV4WUFEME5nRlpZelRmbmR6QUlZVUR0TUM4ams1Um1B|77f233463541c4b9fc31a6a9b42b5f88163ef18b4303fd70456f44a1eca16e97"; tst=h; _gid=GA1.2.1510045404.1599306524; tshl=; __utma=51854390.1140736772.1584584324.1598528992.1599375982.6; __utmz=51854390.1599375982.6.3.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/313964070; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1599486275,1599488570,1599488736,1599535405; SESSIONID=5pwuaHLszXu6pXNArIfJUYI3GLZSMQVw4Omdvj3KhDc; JOID=VlkSA0g7TLr2FYwxTT9Oa5wP3aNfCzrKgHPBezlGEcnHZtN6CvlG6a0XjzBJX6eB65Banw7InWfausewzI_Fmqo=; osd=UFsUBEM9TrzxHoozSzhFbZ4J2qhZCTzNi3XDfT5NF8vBYdh8CP9B4qsViTdCWaWH7JtcnQjPlmHYvMC7yo3DnaE=; _gat_gtag_UA_149949619_1=1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1599541707; KLBRSID=af132c66e9ed2b57686ff5c489976b91|1599541720|1599535403'
        cookies = {i.split("=")[0]:i.split("=")[1] for i in cookies.split("; ")}
        yield Request(
            url.format(question_id=question_id,include=include)
            ,callback=self.parse
            ,cookies=cookies
            ,headers={'referer':'https://www.zhihu.com/question/'+question_id}
            )

    def parse(self, response):
        """问答对页面"""
        response = json.loads(response.text)
        item = PaperItem()#实例化item类型对象
        for data in response['data']:
            item['author_name'] = data['author']['name']
            item['author_id'] = data['id']
            item['gender'] = data['author']['gender']
            
            content= data['content']
            if content is not None:
                img_url = re.findall("data-default-watermark-src=\"(.*?)\"",content) # 回答内容中包含的图片链接列表
                hyper_links= re.findall("a href=\"(.*?)\"",content) # 回答内容中包含的超链接地址列表
                item["img_counts"]=len(img_url) # 显示图片数量
                item["link_counts"]=len(hyper_links) # 显示超链接数量
                item["content"] = re.sub("<.*?>|\s|--|=","",content) # 提出html标签的纯净答案文本
                item["word_counts"] = len(item["content"])

            item['voteup_count'] = data['voteup_count']#答案获得赞同数
            item['com_count'] = data['comment_count']#答案评论数
            item['q_title'] = data['question']['title']#答案标题
            item['q_id'] = data['question']['id']#答案标题
            item['q_created_time'] = data['question']['created']#问题创建时间戳
            item['created_time'] = data['created_time']#答案发布时间时间戳
            item['updated_time'] = data['updated_time']#答案修改时间时间戳
            can_comment= data['can_comment']['reason'] #是否设置评论权限
            item['can_comment'] = can_comment if can_comment != '' else 0
            url_token = data['author']['url_token']#访问回答者详情页所需
            user_url = 'https://www.zhihu.com/people/'+url_token
            if url_token is not None:  
                yield Request(user_url
                            ,callback=self.author_info
                            ,meta = {"item":copy.deepcopy(item)})
            
            time.sleep(1)
        # ——————请求下一页—————— #    
        if response['paging']['is_end'] == False:
            next_url = response['paging']['next']
            yield Request(next_url,callback=self.parse)
        else:
            print('*'*10+'爬取完毕'+'*'*10)
    
    def author_info(self,response):
        """用户html详情页"""
        item = response.meta['item']
        div_list = response.xpath("//div[@itemprop='people']")
        
        for div in div_list:
            # -------标题信息栏-----#
            author_headline = div.xpath("//span[@class='ztext ProfileHeader-headline']/text()").extract_first()
            author_industry = div.xpath("//div[@class='ProfileHeader-infoItem'][1]/text()").extract()
            author_academic = div.xpath("//div[@class='ProfileHeader-infoItem'][2]/text()").extract()
            item['author_headline'] = 1 if  author_headline != [] else 0
            item['author_industry'] = 1 if  author_industry != [] else 0
            item['author_academic'] = 1 if  author_academic != [] else 0
            # 判断是否设置自定义头像
            author_himg = div.xpath("//div[@class='ProfileHeader-main']//img[@class='Avatar Avatar--large UserAvatar-inner']/@src").extract()
            if author_himg[0] == 'https://pic3.zhimg.com/da8e974dc_xl.jpg':
                item['author_himg'] = 0
            else:
                item['author_himg'] = 1
            #判断是否设置自定义资料背景
            author_bimg = div.xpath("//div[@class='ProfileHeader-userCover']/div/@class").extract()
            if author_bimg[0] == 'UserCover':
                item['author_bimg'] = 1
            else:
                item['author_bimg'] = 0
            

            #===============左中侧信息栏===============#
            #—————回复数、文章数、视频数、提问数、专栏数、想法数————#
            item['answer_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-answers'][1]//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            item['video_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-answers'][2]//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            item['question_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-asks']//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            item['article_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-posts']//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            item['column_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-columns']//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            item['idea_counts'] = int(div.xpath("//ul[@role='tablist']/li[@aria-controls='Profile-pins']//span[@class='Tabs-meta']/text()").extract_first().replace(',',''))
            
            #===============右侧信息栏===============#
            #———————个人成就———————#
            author_success = div.xpath("//div[@class='css-122fspz']").extract()
            if author_success != []:     
                for i in author_success:
                    voteup_totals = re.findall(r'获得 (\d+|\S+) 次赞同',i)
                    item['voteup_totals'] = int(voteup_totals[0].replace(',','')) if voteup_totals!=[] else 0

                    like_totals = re.findall(r'获得 (\d+|\S+) 次喜欢，',i)
                    item['like_totals'] = int(like_totals[0].replace(',','')) if len(like_totals) else 0

                    collect_totals = re.findall(r'，(\d+|\S+) 次收藏',i)
                    item['collect_totals'] = int(collect_totals[0].replace(',',''))  if len(collect_totals) else 0

                    professional = re.findall(r'，(\d+|\S+) 次专业认可',i)
                    item['professional'] = int(professional[0].replace(',',''))  if len(professional) else 0

                    public_editor = re.findall(r'<!-- -->(\d+)<!-- -->',i) #参与公共编辑次数
                    item['public_editor'] = int(public_editor[0].replace(',',''))  if len(public_editor) else 0

                    exauthor = re.findall(r'优秀回答者',i)
                    item['exauthor'] = 1 if exauthor != [] else 0  #是否为优秀回答者

                    zhihu_authen = re.findall(r'认证信息',i)
                    item['zhihu_authen'] = 1 if zhihu_authen != [] else 0 #是否通过知乎身份认证

                    ans_included = re.findall(r' (\d+|\S+) 个回答',i)
                    arti_included = re.findall(r' (\d+|\S+) 篇文章',i)
                    item['ans_included'] = int(''.join(ans_included)) if ans_included != [] else 0 #被知乎收录的回答数量
                    item['arti_included'] = int(''.join(arti_included)) if arti_included != [] else 0 #被知乎收录的文章数量

                    zhihu_referee = re.findall(r'知乎众裁官',i)
                    item['zhihu_referee'] = 1 if zhihu_referee != [] else 0 #是否被认证为知乎众裁官
            else:
                item['voteup_totals']=0
                item['like_totals']=0
                item['collect_totals']=0
                item['professional']=0
                item['public_editor']=0
                item['exauthor']=0
                item['zhihu_authen']=0
                item['ans_included']=0
                item['arti_included']=0
                item['zhihu_referee']=0
                
                
            #----关注数与粉丝数----#i
            fs_list= div.xpath("//div[@class='NumberBoard-itemInner']//strong/text()").extract()
            if fs_list != []:
                item['followed_counts'] = int(fs_list[0].replace(',',''))
                item['fans_counts'] = int(fs_list[1].replace(',',''))
            else:
                item['followed_counts'] = 0
                item['fans_counts'] = 0
            
            
            #用户举办的live数量或关注的各类信息列表
            light_list = div.xpath("//div[@class='Profile-lightList']//a/span[@class='Profile-lightItemValue']").xpath('string(.)').extract()
            if len(light_list) == 5:
                item['live_counts'] = int(light_list[0].replace(',',''))
                item['follow_topics'] = int(light_list[1].replace(',',''))
                item['follow_columns'] = int(light_list[2].replace(',',''))
                item['follow_questions'] = int(light_list[3].replace(',',''))
                item['follow_favorites'] = int(light_list[4].replace(',',''))
            elif len(light_list) == 4:
                item['live_counts'] = 0
                item['follow_topics'] = int(light_list[0].replace(',',''))
                item['follow_columns'] = int(light_list[1].replace(',',''))
                item['follow_questions'] = int(light_list[2].replace(',',''))
                item['follow_favorites'] = int(light_list[3].replace(',',''))
            elif len(light_list) == 3:
                item['live_counts'] = 0
                item['follow_topics'] = 0
                item['follow_columns'] = int(light_list[0].replace(',',''))
                item['follow_questions'] = int(light_list[1].replace(',',''))
                item['follow_favorites'] = int(light_list[2].replace(',',''))
            else:
                item['live_counts'] = 0
                item['follow_topics'] = 0
                item['follow_columns'] = 0
                item['follow_questions'] = 0
                item['follow_favorites'] = 0
            
            pprint(item)
            print('*'*20)
            
            yield item

