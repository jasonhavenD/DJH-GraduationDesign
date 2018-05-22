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
from pyltp import Segmentor

LTP_DATA_DIR = "/home/jasonhaven/ltp_data"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
input_lexicon = '../../data/lexicon/entities.txt'

logger = Logger().get_logger()

if __name__ == '__main__':
	input = '../../data/preprocess/sentences.txt'
	output = '../../data/preprocess/segments.txt'
	logger.info("loading model......")
	segmentor = Segmentor()  # 初始化实例
	# segmentor.load(cws_model_path)  # 加载模型
	segmentor.load_with_lexicon(cws_model_path, input_lexicon)  # 加载模型，第二个参数是您的外部词典文件路径
	logger.info("model has been loaded......")
	sents = IOHelper.read_lines(input)
	segments = []
	for sent in sents:
		segment = segmentor.segment(sent)
		segments.append(segment)

	IOHelper.write_tokenses(output, segments)
	logger.info('release model......')
	segmentor.release()
	logger.info('finished!......')
