# -*- coding: utf-8 -*-
import json
from scrapy import Request, Spider 
from weibo.items import * 

# 5866098395

class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    # start_urls = 'https://m.weibo.cn/profile/info?uid=5387637266'
    start_urls = 'https://m.weibo.cn/profile/info?uid=1726644942'

    # weibo_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=230413{uid}&page_type=03&page={page}'
    # 微博url
    # weibo_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=230413{uid}&page={page}'
    # weibo_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=230413{uid}&page_type=03&page={page}'
    weibo_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=230413{uid}&page_type=03&page={page}'
    # 粉丝url
    follower_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id={page}'
    # 关注url
    follow_urls = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'

    def start_requests(self):
        yield Request(self.start_urls, callback=self.parse_user)


    def parse_user(self, response):
    	# print(response.text)
    	doc = json.loads(response.text)
    	if len(doc['data']['user']) > 0:
    		user_info = doc['data']['user']
    		user_item = UserItem()
    		user_item['id'] = user_info['id']
    		user_item['name'] = user_info['screen_name']
    		user_item['description'] = user_info['description']
    		user_item['fans_count'] = user_info['followers_count']
    		user_item['follows_count'] = user_info['follow_count']
    		user_item['avatar'] = user_info['profile_image_url']
    		yield user_item 
    		uid = user_info['id']
    		# 微博
    		yield Request(self.weibo_urls.format(uid=uid, page=1), \
    						callback=self.parse_weibos, meta={'page':1, 'uid':uid})
    		# 关注
    		yield Request(self.follow_urls.format(uid=uid, page=1), \
    						callback=self.parse_follows, meta={'page':1, 'uid':uid})
    		# 粉丝
    		yield Request(self.follower_urls.format(uid=uid, page=1), \
    						callback=self.parse_followers, meta={'page':1, 'uid':uid})


    def parse_weibos(self, response):
    	doc = json.loads(response.text)
    	# print(doc['data']['cards'])
    	if len(doc['data']['cards']) > 2:
    		weibo_item = WeiboItem()
    		for weibo in doc['data']['cards']:
    			if weibo['mblog']:
		    		weibo_item['id'] = weibo['mblog']['id']
		    		weibo_item['text'] = weibo['mblog']['text']
		    		# weibo_item['picture'] = weibo['mblog']['bmiddle_pic']
		    		# weibo_item['user'] = weibo['mblog']['user']
		    		yield weibo_item 
    		# 下一页微博
    		uid = response.meta.get('uid')
    		page = response.meta.get('page') + 1
    		yield Request(self.weibo_urls.format(uid=uid, page=page), callback=self.parse_weibos, meta={'uid':uid, 'page':page})


    def parse_follows(self, response):
    	doc = json.loads(response.text)
    	if len(doc['data']['cards']) > 0:
    		users_info = doc['data']['cards'][-1]['card_group']
    		user_item = UserItem()
    		field_map = {
    			'id':'id', 'name':'screen_name', 'avatar':'profile_image_url', 'gender':'gender',
    			'description':'description', 'fans_count':'followers_count', 'follows_count': 'follow_count',
    			'weibos_count':'statuses_count'
    		}
    		for user_info in users_info:
    			if user_info['user']:
    				for field, attr in field_map.items():
    					user_item[field] = user_info['user'][attr]
    				yield user_item 
    		uid = response.meta['uid']
    		page = response.meta['page'] + 1 
    		yield Request(self.follow_urls.format(uid=uid, page=page), callback=self.parse_follows, \
    						meta={'uid':uid, 'page':page})


    def parse_followers(self, response):
    	doc = json.loads(response.text)
    	if len(doc['data']['cards']) > 0:
    		users_info = doc['data']['cards'][-1]['card_group']
    		user_item = UserItem()
    		field_map = {
    			'id':'id', 'name':'screen_name', 'avatar':'profile_image_url', 'gender':'gender',
    			'description':'description', 'fans_count':'followers_count', 'follows_count':'follow_count',
    			'weibos_count':'statuses_count'
    		}
    		for user_info in users_info:
    			# if user_info['user']:
	    		for field, attr in field_map.items():
	    			user_item[field] = user_info['user'][attr]
	    		yield user_item 

    		uid = response.meta['uid']
    		page = response.meta.get('page') + 1 
    		yield Request(self.follower_urls.format(uid=uid, page=page), callback=self.parse_followers, \
    		 				meta={'uid':uid, 'page':page})







