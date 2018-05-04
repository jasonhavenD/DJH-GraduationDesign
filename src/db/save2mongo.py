#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:save_dbpedia2db
   Author:jasonhaven
   date:2018/4/19
-------------------------------------------------
   Change Activity:2018/4/19:
-------------------------------------------------
"""
import re
import sys
import datetime
from pymongo import MongoClient
from util.log import Logger
from util.io import IOHelper

logger = Logger().get_logger()


def clean_triple(triple):
	pattern = re.compile('[{()}]')
	return re.sub(pattern, '', triple)


if __name__ == '__main__':
	input_ne_triples = "../../data/extraction/ne_triples.txt"
	input_triples = "../../data/extraction/triples.txt"

	client = MongoClient()
	# client = MongoClient('172.19.12.30', 27017)
	client = MongoClient('127.0.0.1', 27017)
	db = client.relation_extraction  # 连接数据库，没有则自动创建
	ne_triples = db.ne_triples  # 使用集合，没有则自动创建
	triples = db.triples  # 使用集合，没有则自动创建

	ne_triples_sents = IOHelper.read_lines(input_ne_triples)
	triples_sents = IOHelper.read_lines(input_triples)

	if ne_triples_sents == None or triples_sents == None:
		logger.error('read failed!')
		sys.exit(0)
	begin = datetime.datetime.now()
	try:
		count = 1
		for sent in ne_triples_sents:
			if sent.strip() == '':
				continue
			sent,type, triple = sent.strip().split('\t')
			triple = clean_triple(triple)
			doc = {}
			doc['sent']=sent.strip()
			doc['e1'], doc['rel'], doc['e2'] = triple.strip().split(',')
			ne_triples.insert(doc)
			logger.info('insert {} ne_triples'.format(count))
			count += 1
		count = 1
		for sent in triples_sents:
			if sent.strip() == '':
				continue
			sent, type, triple = sent.strip().split('\t')
			triple = clean_triple(triple)
			doc = {}
			doc['sent'] = sent.strip()
			doc['e1'], doc['rel'], doc['e2'] = triple.strip().split(',')
			triples.insert(doc)
			logger.info('insert {} triples'.format(count))
			count += 1
	except Exception as e:
		logger.error(e)
	ne_triples.ensure_index([("e1", 1)])
	ne_triples.ensure_index([("e2", 1)])
	ne_triples.ensure_index([("rel", 1)])
	ne_triples.ensure_index([("e1", 1), ("e2", 1)])
	triples.ensure_index([("e1", 1)])
	triples.ensure_index([("e2", 1)])
	triples.ensure_index([("rel", 1)])
	triples.ensure_index([("e1", 1), ("e2", 1)])
	end = datetime.datetime.now()
	logger.info("finish in {}s.".format(end - begin))
