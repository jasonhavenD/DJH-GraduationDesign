#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:LTP_MODEL
   Author:jason
   date:18-4-25
-------------------------------------------------
   Change Activity:18-4-25:
-------------------------------------------------
"""
import sys
import os
from pyltp import *
import ne_re

sys.path.append('../util/')
input_lexicon = '../../data/lexicon/entities.txt'
LTP_DATA_DIR = "/home/jason/ltp_data"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
print("loading models......")
segmentor = Segmentor()
# segmentor.load(cws_model_path)
segmentor.load_with_lexicon(cws_model_path, input_lexicon)  # 加载模型，第二个参数是您的外部词典文件路径
print("{} has been loaded......".format('cws.model'))

postagger = Postagger()
postagger.load(pos_model_path)
print("{} has been loaded......".format('pos.model'))

parser = Parser()
parser.load(par_model_path)
print("{} has been loaded......".format('parser.model'))

recognizer = NamedEntityRecognizer()
recognizer.load(ner_model_path)
print("{} has been loaded......".format('ner.model'))


def sentence_split(text):
	sentences = SentenceSplitter.split(text.strip())
	return sentences


def segments(sents):
	segments = []
	for sent in sents:
		segment = segmentor.segment(sent)
		segments.append(segment)
	return segments


def postags(segments):
	postagses = []
	for seg in segments:
		postag = postagger.postag(seg)
		postagses.append(postag)
	return postagses


def ners(wordses, postagses):
	min_length = len(wordses) if len(wordses) <= len(postagses) else len(postagses)
	wordses = wordses[:min_length]
	postagses = postagses[:min_length]
	nerses = []
	for words, postags in zip(wordses, postagses):
		ners = recognizer.recognize(words, postags)
		nerses.append(ners)
	return nerses


def ner_extract(text):
	sentences = sentence_split(text)
	segments_sents = segments(sentences)
	postags_sents = postags(segments_sents)
	ners_sents = ners(segments_sents, postags_sents)
	ne_triples = ne_re.extract(sentences, segments_sents, postags_sents, ners_sents)
	return sentences, segments_sents, postags_sents, ne_triples


if __name__ == '__main__':
	text = '''
	奥巴马随母亲和继父前往印度尼西亚首都雅加达生活，并在当地的一所小学就读了两年。四年后他的一家又回到夏威夷，与外祖父母住在一起，从五年级起，他就读于位于火奴鲁鲁的大型私立学校——普纳荷学校（中华民国第一任临时大总统孙文曾于此校就读）至12年级，于1979年毕业，若干年后母亲与继父离婚，他便随母迁居美国本土。青年时期，奥巴马因为自己的多种族背景，很难取得社会认同，十分自卑，他过了一段荒唐的日子，做了很多愚蠢的事，比如逃学、吸毒、泡妞等，成了一个不折不扣的“迷途叛逆少年”。十几岁的他成了一个瘾君子，曾以吸食大麻和可卡因来“将‘我是谁’的问题挤出脑袋”。给青年的他带来深刻影响的不是他的父母亲，而是他的外祖父斯坦利·埃默·邓汉姆和外祖母斯坦利·安·邓汉姆，著名黑人诗人、记者和美国左翼活动家法兰克·米歇尔·戴维斯也是深刻影响青年奥巴马的人物，19世纪60年代戴维斯就成为奥巴马家里的常客。面对猛烈的空中打击和地面进攻，极端组织“伊斯兰国”的大本营拉卡开始出现恐慌，正在加固城防和转移人员。拉卡市位于叙利亚北部，去年初遭“伊斯兰国”占领并作为大本营。当地居民说，由于反“伊斯兰国”武装进逼以及俄罗斯和法国加强空袭，“伊斯兰国”人员近来开始强化防御，在通往这座城市的道路上挖了大量壕沟，他们还在城外堆放许多灌注汽油的轮胎，准备在受到进攻时点燃。由于空袭猛烈，“伊斯兰国”高层命令手下的武装人员撤离营地，躲入居民区，而且只能在小街小巷中移动，以避免被飞机发现，另外，他们下令，夜间禁止开汽车，拉卡原居民哈立德18日告诉美联社记者，10月下旬开始，“伊斯兰国”禁止当地居民逃难，而且最近强化了这一禁令，现在，居民人心惶惶，害怕被“伊斯兰国”用作“人体盾牌”，哈立德眼下居住在土耳其，不过仍与住在拉卡的亲戚朋友保持通信联系。
	'''
	sentences, segments_sents, postags_sents, ne_triples_sents = ner_extract(text)
	# for s in sentences:
	# 	print(s)
	# print()
	# for s in segments_sents:
	# 	print([x for x in s])
	# print()
	# for s in postags_sents:
	# 	print([x for x in s])
	# print()
	for triples in ne_triples_sents:
		for triple in triples:
			print(triple)
