#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:ne_re
   Author:jason
   date:18-4-23
-------------------------------------------------
   Change Activity:18-4-23:
-------------------------------------------------
"""
import sys
import os

sys.path.append('../util/')
import datetime
from util.io import IOHelper
from util.log import Logger
from pyltp import Parser, Segmentor, Postagger

logger = Logger().get_logger()

LTP_DATA_DIR = "/home/jasonhaven/ltp_data"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')


def extract(sentences, segments_sents, postags_sents, ners_sents, output_triples, output_ne_triples, size):
	# change size
	sentences = sentences[0:size]
	segments_sents = segments_sents[0:size]
	postags_sents = postags_sents[0:size]
	ners_sents = ners_sents[0:size]

	triples_sents = []
	ne_triples_sents = []
	for i in range(size):
		sent = sentences[i]
		segments = segments_sents[i].strip().split('\t')
		postags = postags_sents[i].strip().split('\t')
		ners = ners_sents[i].strip().split('\t')
		logger.info('extracting {} sentent...'.format(i + 1))

		try:
			if sent.strip() == '' or len(sent) > 1000:
				continue

			triples, ne_triples = triple_extract(sent.strip(), segments, postags, ners)

			if triples == []:
				continue
			triples_sents.append(triples)
			if ne_triples == []:
				continue
			ne_triples_sents.append(ne_triples)
		except Exception as e:
			logger.info('filter {} sent......'.format(i + 1))
	IOHelper.write_triples(output_triples, triples_sents)
	IOHelper.write_triples(output_ne_triples, ne_triples_sents)


def triple_extract(sentence, words, postags, netags):
	arcs = parser.parse(words, postags)
	child_dict_list = build_parse_child_dict(words, arcs)
	NE_list = set()

	for i in range(len(netags)):
		if netags[i][0] == 'S' or netags[i][0] == 'B':
			j = i
			if netags[j][0] == 'B':
				while netags[j][0] != 'E':
					j += 1
				e = ''.join(words[i:j + 1])
				NE_list.add(e)
			else:
				e = words[j]
				NE_list.add(e)

	triples = []
	ne_triples = []
	for index in range(len(postags)):
		# 抽取以谓词为中心的三元组
		if postags[index] == 'v':
			child_dict = child_dict_list[index]
			# 主谓宾
			if child_dict.has_key('SBV') and child_dict.has_key('VOB'):
				e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
				r = words[index]
				e2 = complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
				triples.append("{}\t主语谓语宾语关系\t({},{},{})".format(sentence,e1, r, e2))
				if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
					ne_triples.append("{}\t主语谓语宾语关系\t({},{},{})".format(sentence,e1, r, e2))
			# 定语后置，动宾关系
			if arcs[index].relation == 'ATT':
				if child_dict.has_key('VOB'):
					e1 = complete_e(words, postags, child_dict_list, arcs[index].head - 1)
					r = words[index]
					e2 = (words, postags, child_dict_list, child_dict['VOB'][0])
					temp_string = r + str(e2)
					if temp_string == e1[:len(temp_string)]:
						e1 = e1[len(temp_string):]
					if temp_string not in e1:
						triples.append("{}\t定语后置动宾关系\t({},{},{})".format(sentence,e1, r, e2))
					if temp_string not in e1 and is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list,
					                                                                              sentence):
						ne_triples.append("{}\t定语后置动宾关系\t({},{},{})".format(sentence,e1, r, e2))
			# 含有介宾关系的主谓动补关系
			if child_dict.has_key('SBV') and child_dict.has_key('CMP'):
				# e1 = words[child_dict['SBV'][0]]
				e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
				cmp_index = child_dict['CMP'][0]
				r = words[index] + words[cmp_index]
				if child_dict_list[cmp_index].has_key('POB'):
					e2 = complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
					triples.append("{}\t介宾关系主谓动补\t({},{},{})".format(sentence,e1, r, e2))
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						ne_triples.append("{}\t介宾关系主谓动补\t({},{},{})".format(sentence,e1, r, e2))

		# 尝试抽取命名实体有关的三元组
		if netags[index][0] == 'S' or netags[index][0] == 'B':
			ni = index
			if netags[ni][0] == 'B':
				while netags[ni][0] != 'E':
					ni += 1
				e1 = ''.join(words[index:ni + 1])
			else:
				e1 = words[ni]
			if arcs[ni].relation == 'ATT' and postags[arcs[ni].head - 1] == 'n' and netags[
				arcs[ni].head - 1] == 'O':
				r = complete_e(words, postags, child_dict_list, arcs[ni].head - 1)
				if e1 in r:
					r = r[(r.index(e1) + len(e1)):]
				if arcs[arcs[ni].head - 1].relation == 'ATT' and netags[arcs[arcs[ni].head - 1].head - 1] != 'O':
					e2 = complete_e(words, postags, child_dict_list, arcs[arcs[ni].head - 1].head - 1)
					mi = arcs[arcs[ni].head - 1].head - 1
					li = mi
					if netags[mi][0] == 'B':
						while netags[mi][0] != 'E':
							mi += 1
						e = ''.join(words[li + 1:mi + 1])
						e2 += e
					if r in e2:
						e2 = e2[(e2.index(r) + len(r)):]
					if r + e2 in sentence:
						triples.append("{}\t机构//地名//人名\t({},{},{})".format(sentence,e1, r, e2))
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						ne_triples.append("{}\t机构//地名//人名\t({},{},{})".format(sentence,e1, r, e2))
	return triples, ne_triples


def build_parse_child_dict(words, arcs):
	'''
	为句子中的每个词语维护一个保存句法依存儿子节点的字典
	:param words: 分词列表
	:param postags: 词性列表
	:param arcs:句法依存列表
	:return:字典
	'''
	child_dict_list = []
	for index in range(len(words)):
		child_dict = dict()
		for arc_index in range(len(arcs)):
			if arcs[arc_index].head == index + 1:
				if child_dict.has_key(arcs[arc_index].relation):
					child_dict[arcs[arc_index].relation].append(arc_index)
				else:
					child_dict[arcs[arc_index].relation] = []
					child_dict[arcs[arc_index].relation].append(arc_index)
		child_dict_list.append(child_dict)
	return child_dict_list


def complete_e(words, postags, child_dict_list, word_index):
	'''
	完善识别的部分实体
	:param words:分词列表
	:param postags:词性列表
	:param child_dict_list:句法依存节点的字典
	:param word_index:location
	:return:entity
	'''
	child_dict = child_dict_list[word_index]
	prefix = ''
	if child_dict.has_key('ATT'):
		for i in range(len(child_dict['ATT'])):
			prefix += complete_e(words, postags, child_dict_list, child_dict['ATT'][i])

	postfix = ''
	if postags[word_index] == 'v':
		if child_dict.has_key('VOB'):
			postfix += complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
		if child_dict.has_key('SBV'):
			prefix = complete_e(words, postags, child_dict_list, child_dict['SBV'][0]) + prefix

	return prefix + words[word_index] + postfix


def is_named_e(e, ne_list, sentence):
	'''
	judge a entity is named entity or not
	:param e:entity
	:param ne_list:lits of entities
	:param sentence:
	:return:bool
	'''
	if e not in sentence:
		return False
	words_e = segmentor.segment(e)
	postags_e = postagger.postag(words_e)
	if e in ne_list:
		return True
	else:
		NE_count = 0
		for i in range(len(words_e)):
			if words_e[i] in ne_list:
				NE_count += 1
			if postags_e[i] == 'v':
				return False
		if NE_count >= len(words_e) - NE_count:
			return True
	return False


import LTP_MODEL

if __name__ == "__main__":
	input_lexicon = '../../data/lexicon/entities.txt'
	input_sentences = "../../data/preprocess/sentences.txt"
	input_segments = "../../data/preprocess/segments.txt"
	input_postags = "../../data/preprocess/postags.txt"
	input_ners = "../../data/preprocess/ners.txt"

	output_triples = "../../data/extraction/triples.txt"
	output_ne_triples = "../../data/extraction/ne_triples.txt"

	begin=datetime.datetime.now()

	logger.info("loading models......")
	segmentor = Segmentor()
	# segmentor.load(cws_model_path)
	segmentor.load_with_lexicon(cws_model_path, input_lexicon)  # 加载模型，第二个参数是您的外部词典文件路径
	logger.info("{} has been loaded......".format('cws.model'))

	postagger = Postagger()
	postagger.load(pos_model_path)
	logger.info("{} has been loaded......".format('pos.model'))

	parser = Parser()
	parser.load(par_model_path)
	logger.info("{} has been loaded......".format('parser.model'))

	sentences = IOHelper.read_lines(input_sentences)
	segments_sents = IOHelper.read_lines(input_segments)
	postags_sents = IOHelper.read_lines(input_postags)
	ners_sents = IOHelper.read_lines(input_ners)

	size=100000
	extract(sentences, segments_sents, postags_sents, ners_sents, output_triples, output_ne_triples, size)

	end = datetime.datetime.now()
	logger.info("finished in {}s for {} sentences.".format(end-begin,size))
