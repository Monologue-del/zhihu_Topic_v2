# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from zhihu.items import AnswerItem, QuestionItem, UrlItem
from urllib import parse


class ZhihuPipeline:
    def __init__(self, mongo_uri):
        self.mongo_ip = mongo_uri['ip']
        self.mongo_port = mongo_uri['port']
        self.mongo_user = mongo_uri['user']
        self.mongo_passwd = mongo_uri['passwd']

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI')
        )

    def open_spider(self, spider):
        # 配置数据库uri
        # 先对密码进行编码
        self.mongo_passwd = parse.quote(self.mongo_passwd)
        mongo_uri = 'mongodb://%s:%s@%s:%s' % \
                    (self.mongo_user, self.mongo_passwd, self.mongo_ip, self.mongo_port)
        # 连接到数据库
        self.client = MongoClient(mongo_uri)
        # 连接到指定数据库：话题名
        zhihu_DB = self.client['zhihu_Topic_Movie']
        # 连接到指定表
        self.question_collection = zhihu_DB['questions']
        self.answer_collection = zhihu_DB['answers']
        self.question_url_collectiion = zhihu_DB['questions_url']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # 存储用户基本信息到MongoDB
        if isinstance(item, QuestionItem):
            self.question_collection.update({'id': item['question_id']}, {'$set': item}, True)
            print('question', item['question_id'], '爬取成功')
        elif isinstance(item, AnswerItem):
            self.answer_collection.update({'id': item['answer_id']}, {'$set': item}, True)
            print('answer', item['answer_id'], '爬取成功')
        elif isinstance(item, UrlItem):
            self.question_url_collectiion.update({'id': item['url']}, {'$set': item}, True)
