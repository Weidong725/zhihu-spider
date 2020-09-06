# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
class PaperPipeline(object):
    def __init__(self):
        self.f = open("qqqaa.csv", "w",newline='',encoding='utf-8')
        self.writer = csv.writer(self.f)
        self.writer.writerow([
                            'author_name'
                            ,'author_id'
                            ,'gender'
                            ,'img_counts'
                            ,'link_counts'
                            ,'content'
                            ,'word_counts'
                            ,'voteup_count'
                            ,'com_count'
                            ,'created_time'
                            ,'updated_time'
                            ,'q_created_time'
                            ,'q_title'
                            ,'q_id'
                            ,'q_tags'
                            ,'can_comment'
                            ,'author_headline'
                            ,'author_industry'
                            ,'author_academic'
                            ,'author_himg'
                            ,'author_bimg'
                            ,'answer_counts'
                            ,'video_counts'
                            ,'question_counts'
                            ,'article_counts'
                            ,'column_counts'
                            ,'idea_counts'
                            ,'voteup_totals'
                            ,'like_totals'
                            ,'collect_totals'
                            ,'professional'
                            ,'public_editor'
                            ,'exauthor'
                            ,'zhihu_authen'
                            ,'ans_included'
                            ,'arti_included'
                            ,'zhihu_referee'
                            ,'followed_counts'
                            ,'fans_counts'
                            ,'live_counts'
                            ,'follow_topics'
                            ,'follow_columns'
                            ,'follow_questions'
                            ,'follow_favorites'
                            ])

                            
    def process_item(self, item, spider):
        data_list =  [
                        item['author_name']
                        ,item['author_id']
                        ,item['gender']
                        ,item['img_counts']
                        ,item['link_counts']
                        ,item['content']
                        ,item['word_counts']
                        ,item['voteup_count']
                        ,item['com_count']
                        ,item['created_time']
                        ,item['updated_time']
                        ,item['q_created_time']
                        ,item['q_title']
                        ,item['q_id']
                        ,item['q_tags']
                        ,item['can_comment']
                        ,item['author_headline']
                        ,item['author_industry']
                        ,item['author_academic']
                        ,item['author_himg']
                        ,item['author_bimg']
                        ,item['answer_counts']
                        ,item['video_counts']
                        ,item['question_counts']
                        ,item['article_counts']
                        ,item['column_counts']
                        ,item['idea_counts']
                        ,item['voteup_totals']
                        ,item['like_totals']
                        ,item['collect_totals']
                        ,item['professional']
                        ,item['public_editor']
                        ,item['exauthor']
                        ,item['zhihu_authen']
                        ,item['ans_included']
                        ,item['arti_included']
                        ,item['zhihu_referee']
                        ,item['followed_counts']
                        ,item['fans_counts']
                        ,item['live_counts']
                        ,item['follow_topics']
                        ,item['follow_columns']
                        ,item['follow_questions']
                        ,item['follow_favorites']
                    ]
        self.writer.writerow(data_list)
        return item
    def close_spider(self, spider):#关闭
        # self.writer.close()
        self.f.close()
        
       
