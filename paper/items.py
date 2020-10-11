# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PaperItem(scrapy.Item):

    # define the fields for your item here like:
    author_name = scrapy.Field()  # 回答者姓名
    author_id = scrapy.Field()  # 回答者id
    gender = scrapy.Field()  # 回答者性别
    img_counts = scrapy.Field()  # 答案中图片数量
    link_counts = scrapy.Field()  # 答案中超链接数量
    # rank= scrapy.Field()#答案排名
    content = scrapy.Field()  # 答案文本
    word_counts = scrapy.Field()  # 答案字数
    voteup_count = scrapy.Field()  # 答案收到点赞数
    com_count = scrapy.Field()  # 答案收到评论数
    created_time = scrapy.Field()  # 答案发布时间
    updated_time = scrapy.Field()  # 答案更新时间
    q_created_time = scrapy.Field()  # 问题发布时间
    q_title = scrapy.Field()  # 问题标题
    q_id = scrapy.Field()  # 问题编号
    can_comment = scrapy.Field()  # 是否设置评论权限
    author_headline = scrapy.Field()  # 回答者资料标题
    author_industry = scrapy.Field()  # 回答者所在行业
    author_academic = scrapy.Field()  # 回答者学业
    author_himg = scrapy.Field()  # 回答者是否设置头像图片
    author_bimg = scrapy.Field()  # 回答者是否设置资料背景图片
    answer_counts = scrapy.Field()  # 回答者回答数量
    video_counts = scrapy.Field()  # 回答者发布视频数量
    question_counts = scrapy.Field()  # 回答者提问数量
    article_counts = scrapy.Field()  # 回答者发布文章数量
    column_counts = scrapy.Field()  # 回答者专栏数量
    idea_counts = scrapy.Field()  # 回答者想法数量
    voteup_totals = scrapy.Field()  # 回答者获得总点赞数
    like_totals = scrapy.Field()  # 回答者获得总喜欢数
    collect_totals = scrapy.Field()  # 回答者获得总收藏数
    professional = scrapy.Field()  # 回答者获得专业认可数量
    public_editor = scrapy.Field()  # 回答者参与公共编辑次数
    exauthor = scrapy.Field()  # 是否被认证为优秀回答者
    zhihu_authen = scrapy.Field()  # 是否经过知乎的学历认证
    ans_included = scrapy.Field()  # 被知乎圆桌收录的回答数量
    arti_included = scrapy.Field()  # 被知乎圆桌收录的文章数量
    zhihu_referee = scrapy.Field()  # 回答者是否是知乎众裁官
    followed_counts = scrapy.Field()  # 回答者关注数
    fans_counts = scrapy.Field()  # 回答者粉丝数
    live_counts = scrapy.Field()  # 回答者发布的live数
    follow_topics = scrapy.Field()  # 回答者关注的话题数
    follow_columns = scrapy.Field()  # 回答者关注的专栏数量
    follow_questions = scrapy.Field()  # 回答者关注的问题数量
    follow_favorites = scrapy.Field()  # 回答者关注的收藏夹数量
    url_token = scrapy.Field()  # 构造连接id
    com_content = scrapy.Field()
    reviewer_token = scrapy.Field()
