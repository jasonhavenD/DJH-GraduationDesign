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
from pyltp import NamedEntityRecognizer

LTP_DATA_DIR = "/home/jason/ltp_data"  # ltp模型目录的路径
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径

logger = Logger().get_logger()

if __name__ == '__main__':
	input_segments = '../../data/preprocess/segments.txt'
	input_postags = '../../data/preprocess/postags.txt'
	output = '../../data/preprocess/ners.txt'

	logger.info("loading model......")
	recognizer = NamedEntityRecognizer()  # 初始化实例
	recognizer.load(ner_model_path)  # 加载模型
	logger.info("model has been loaded......")

	wordses = IOHelper.read_lines(input_segments)
	postagses = IOHelper.read_lines(input_postags)

	if len(wordses) != len(postagses):
		wordses = wordses[:10000]
		postagses = postagses[:10000]
	nerses = []
	for words, postags in zip(wordses, postagses):
		ners = recognizer.recognize(words.split('\t'), postags.split('\t'))
		nerses.append(ners)
	IOHelper.write_tokenses(output, nerses)
	logger.info('release model......')
	recognizer.release()
	logger.info('finished!......')
