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

import os
import codecs

from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer


def extract_from_file(fin_name, f_corpus):
	f_corpus = codecs.open(f_corpus, 'a')
	with codecs.open(fin_name, 'r')as fin:
		sents = fin.readlines()[1000:5000]

	for sent in sents:
		if sent.strip() == "" or len(sent) > 1000:
			continue
		try:
			triple_extract(sent.strip(), f_corpus)
		except Exception as e:
			pass


def triple_extract(sentence, corpus_file):
	words = segmentor.segment(sentence)
	postags = postagger.postag(words)
	netags = recognizer.recognize(words, postags)
	arcs = parser.parse(words, postags)

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
	corpus_flag = False
	child_dict_list = build_parse_child_dict(words, postags, arcs)
	for index in range(len(postags)):
		# 抽取以谓词为中心的三元组
		if postags[index] == 'v':
			child_dict = child_dict_list[index]
			# 主谓宾
			if child_dict.has_key('SBV') and child_dict.has_key('VOB'):
				e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
				r = words[index]
				e2 = complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
				# if e1 in NE_list or e2 in NE_list:
				if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
					triples.append("主语谓语宾语关系\t({},{},{})".format(e1, r, e2))
					if not corpus_flag:
						corpus_file.write(sentence)
						corpus_flag = True
					e1_start = (sentence.decode('utf-8')).index((e1.decode('utf-8')))
					e1_end = e1_start + len(e1.decode('utf-8')) - 1
					r_start = (sentence.decode('utf-8')).index((r.decode('utf-8')))
					r_end = r_start + len(r.decode('utf-8')) - 1
					e2_start = (sentence.decode('utf-8')).index((e2.decode('utf-8')))
					e2_end = e2_start + len(e2.decode('utf-8')) - 1
					corpus_file.write("\t[%s/%d-%d&%s/%d-%d&%s/%d-%d]" % (
						e1, e1_start, e1_end, r, r_start, r_end, e2, e2_start, e2_end))
					corpus_file.flush()
			# 定语后置，动宾关系
			if arcs[index].relation == 'ATT':
				if child_dict.has_key('VOB'):
					e1 = complete_e(words, postags, child_dict_list, arcs[index].head - 1)
					r = words[index]
					e2 = complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
					temp_string = r + e2
					if temp_string == e1[:len(temp_string)]:
						e1 = e1[len(temp_string):]
					# if temp_string not in e1 and (e1 in NE_list or e2 in NE_list):
					if temp_string not in e1 and is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list,
					                                                                              sentence):
						triples.append("定语后置动宾关系\t({},{},{})".format(e1, r, e2))
						if not corpus_flag:
							corpus_file.write(sentence)
							corpus_flag = True
						e1_start = (sentence.decode('utf-8')).index((e1.decode('utf-8')))
						e1_end = e1_start + len(e1.decode('utf-8')) - 1
						r_start = (sentence.decode('utf-8')).index((r.decode('utf-8')))
						r_end = r_start + len(r.decode('utf-8')) - 1
						e2_start = (sentence.decode('utf-8')).index((e2.decode('utf-8')))
						e2_end = e2_start + len(e2.decode('utf-8')) - 1
						corpus_file.write("\t[%s/%d-%d&%s/%d-%d&%s/%d-%d]" % (
							e1, e1_start, e1_end, r, r_start, r_end, e2, e2_start, e2_end))
						corpus_file.flush()
			# 含有介宾关系的主谓动补关系
			if child_dict.has_key('SBV') and child_dict.has_key('CMP'):
				# e1 = words[child_dict['SBV'][0]]
				e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
				cmp_index = child_dict['CMP'][0]
				r = words[index] + words[cmp_index]
				if child_dict_list[cmp_index].has_key('POB'):
					e2 = complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
					# if e1 in NE_list or e2 in NE_list:
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						triples.append("介宾关系主谓动补\t({},{},{})".format(e1, r, e2))
						if not corpus_flag:
							corpus_file.write(sentence)
							corpus_flag = True
						e1_start = (sentence.decode('utf-8')).index((e1.decode('utf-8')))
						e1_end = e1_start + len(e1.decode('utf-8')) - 1
						r_start = (sentence.decode('utf-8')).index((r.decode('utf-8')))
						r_end = r_start + len(r.decode('utf-8')) - 1
						e2_start = (sentence.decode('utf-8')).index((e2.decode('utf-8')))
						e2_end = e2_start + len(e2.decode('utf-8')) - 1
						corpus_file.write("\t[%s/%d-%d&%s/%d-%d&%s/%d-%d]" % (
							e1, e1_start, e1_end, r, r_start, r_end, e2, e2_start, e2_end))
						corpus_file.flush()
		# 尝试抽取命名实体有关的三元组
		if netags[index][0] == 'S' or netags[index][0] == 'B':
			ni = index
			if netags[ni][0] == 'B':
				while netags[ni][0] != 'E':
					ni += 1
				e1 = ''.join(words[index:ni + 1])
			else:
				e1 = words[ni]
			if arcs[ni].relation == 'ATT' and postags[arcs[ni].head - 1] == 'n' and netags[arcs[ni].head - 1] == 'O':
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
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						triples.append("机构//地名//人名\t({},{},{})".format(e1, r, e2))
						if not corpus_flag:
							corpus_file.write(sentence)
							corpus_flag = True
						e1_start = (sentence.decode('utf-8')).index((e1.decode('utf-8')))
						e1_end = e1_start + len(e1.decode('utf-8')) - 1
						r_start = (sentence.decode('utf-8')).index((r.decode('utf-8')))
						r_end = r_start + len(r.decode('utf-8')) - 1
						e2_start = (sentence.decode('utf-8')).index((e2.decode('utf-8')))
						e2_end = e2_start + len(e2.decode('utf-8')) - 1
						corpus_file.write("\t[%s/%d-%d&%s/%d-%d&%s/%d-%d]" % (
							e1, e1_start, e1_end, r, r_start, r_end, e2, e2_start, e2_end))
						corpus_file.flush()
	if corpus_flag:
		corpus_file.write("\n")
		corpus_file.flush()
	return triples


def build_parse_child_dict(words, postags, arcs):
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


LTP_DATA_DIR = "/home/jason/ltp_data"  # ltp模型目录的路径

if __name__ == "__main__":
	cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
	pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
	par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
	ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
	print("loading models......")
	segmentor = Segmentor()
	segmentor.load(cws_model_path)
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
	input_sents = "../../data/preprocess/sentences.txt"
	output_corpus = "../../data/corpus/ne_corpus.txt"

	extract_from_file(input_sents, output_corpus)
