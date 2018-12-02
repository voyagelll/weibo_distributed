# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, time 
import logging 
import pymongo 
from weibo.items import * 


class WeiboPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri 
		self.mongo_db = mongo_db 

	@classmethod 
	def from_crawler(cls, crawler):
		return cls(
				mongo_uri = crawler.settings.get('MONGO_URI'),
				mongo_db = crawler.settings.get('MONGO_DB'),
			)

	def open_spider(self, spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]
		self.db[UserItem.collection].create_index([('id', pymongo.ASCENDING)])
		self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])

	def close_spider(self, spider):
		self.client.close()

	def process_item(self, item, spider):
		if isinstance(item, UserItem) or isinstance(item, WeiboItem):
			self.db[item.collection].update({'id':item.get('id')}, {'$set': item}, True)
		if isinstance(item, UserRelationItem):
			self.db[item.collection].update(
					{'id': item.get('id')},
					{'$addToSet': 
						{
							'follows': {'$each': item['folows']},
							'fans': {'$each': item['fans']}
						}
					}, True)
		return item 