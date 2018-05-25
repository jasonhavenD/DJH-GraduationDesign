#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:test
   Author:jasonhaven
   date:18-5-15
-------------------------------------------------
   Change Activity:18-5-15:
-------------------------------------------------
"""
import sys
import os
from pyltp import *

sys.path.append("./extraction/")
import codecs

from extraction import LTP_MODEL

LTP_DATA_DIR = "/home/jasonhaven/ltp_data"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
print("loading models......")
segmentor = Segmentor()

postagger = Postagger()


parser = Parser()
parser.load(par_model_path)
print("{} has been loaded......".format('parser.model'))

recognizer = NamedEntityRecognizer()
recognizer.load(ner_model_path)
print("{} has been loaded......".format('ner.model'))

text = '''
一汽奥迪是西北农林科技大学的一名学生。
'''

if __name__ == '__main__':
	input_lexicon = '../data/lexicon/entities.txt'
	input_postag='../data/lexicon/postag.txt'
	segmentor.load(cws_model_path)
	# segmentor.load_with_lexicon(cws_model_path, input_lexicon)  # 加载模型，第二个参数是您的外部词典文件路径
	print("{} has been loaded......".format('cws.model'))

	# postagger.load(pos_model_path)
	postagger.load_with_lexicon(pos_model_path,input_postag)
	print("{} has been loaded......".format('pos.model'))

	sentences = LTP_MODEL.sentence_split(text)
	segments_sents = LTP_MODEL.segments(sentences)
	postags_sents = LTP_MODEL.postags(segments_sents)
	ners_sents = LTP_MODEL.ners(segments_sents, postags_sents)

	with codecs.open("test.txt", 'w') as f:
		for words,nes in zip(segments_sents,ners_sents):
			f.write(str('\t'.join(list(words))))
			f.write('\n')
			f.write(str('\t'.join(list(nes))))
			f.write('\n')
			f.write('\n')
