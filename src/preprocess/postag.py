#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:segment
   Author:jason
   date:18-4-23
-------------------------------------------------
   Change Activity:18-4-23:
-------------------------------------------------
"""

import sys

sys.path.append('../util/')
import os
from util.io import IOHelper
from util.log import Logger
from pyltp import Postagger

LTP_DATA_DIR = "/home/jason/ltp_data"  # ltp模型目录的路径
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')

logger = Logger().get_logger()

if __name__ == '__main__':
	input = '../../data/preprocess/segments.txt'
	output = '../../data/preprocess/postags.txt'
	logger.info("loading model......")
	postagger = Postagger()  # 初始化实例
	postagger.load(pos_model_path)
	# use personal dict
	# postagger.load_with_lexicon(pos_model_path, input_lexicon)
	logger.info("model has been loaded......")
	sents = IOHelper.read_lines(input)
	postagses = []
	for sent in sents:
		postag = postagger.postag(sent.split('\t'))
		postagses.append(postag)

	IOHelper.write_tokenses(output, postagses)
	logger.info('release model......')
	postagger.release()
	logger.info('finished!......')
