#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:extract_rels
   Author:jasonhaven
   date:18-5-20
-------------------------------------------------
   Change Activity:18-5-20:
-------------------------------------------------
"""
import pandas as pd
import datetime
from pymongo import MongoClient
from util.log import Logger
logger = Logger().get_logger()


if __name__ == '__main__':
	client = MongoClient()
	client = MongoClient('127.0.0.1', 27017)
	db = client.relation_extraction  # 连接数据库，没有则自动创建
	ne_triples = db.ne_triples  # 使用集合，没有则自动创建
	begin = datetime.datetime.now()
	cursor=ne_triples.find()

	df=pd.DataFrame()
	rels=[]
	e1s=[]
	e2s=[]
	dicts={}
	for tpl in cursor:
		e1,rel,e2=tpl['e1'],tpl['rel'],tpl['e2']
		e1s.append(e1)
		e2s.append(e2)
		rels.append(rel)
		if rel not in dicts.keys():
			dicts[rel]=1
		else:
			dicts[rel] +=1
	print(len(e1s),len(e2s),len(rels))
	# df['e1']= e1s
	# df['e2'] = e2s
	# df['rel'] = rels
	# df.to_csv('./extract_rels.csv',sep=',',encoding='utf-8')

	# df['rel'] = list(set(rels))
	# df.to_csv('./rels.csv', sep=',', encoding='utf-8')

	print(len(dicts.items()))
	for k,v in dicts.items():
		if len(k)<2 or len(k)>10 or v<6:
			dicts.pop(k)
	print(len(dicts.items()))
	df['rel'] = dicts.keys()
	df['value'] = dicts.values()
	df.to_csv('./rel_values.csv', sep=',', encoding='utf-8')

	end = datetime.datetime.now()
	logger.info("finish in {}s.".format(end - begin))
