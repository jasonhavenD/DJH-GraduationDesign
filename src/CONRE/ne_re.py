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
from pyltp import Parser, Segmentor, Postagger


LTP_DATA_DIR = "/home/jason/ltp_data"  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')

segmentor = Segmentor()
segmentor.load(cws_model_path)

postagger = Postagger()
postagger.load(pos_model_path)

parser = Parser()
parser.load(par_model_path)


def extract(sentences, segments_sents, postags_sents, ners_sents):
	ne_triples_sents = []
	for sent,segments,postags,ners in zip(sentences,segments_sents,postags_sents,ners_sents):
		try:
			if sent.strip() == '' or len(sent) > 1000:
				continue
			ne_triples = triple_extract(sent, segments, postags, ners)
			if ne_triples == []:
				continue
			ne_triples_sents.append(ne_triples)
		except Exception as e:
			print(e)
			pass
	return ne_triples_sents


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
				if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
					ne_triples.append({'e1': e1, 'rel': r, 'e2': e2})
			# 定语后置，动宾关系
			if arcs[index].relation == 'ATT':
				if child_dict.has_key('VOB'):
					e1 = complete_e(words, postags, child_dict_list, arcs[index].head - 1)
					r = words[index]
					e2 = (words, postags, child_dict_list, child_dict['VOB'][0])

					temp_string = r + str(e2)

					if temp_string == e1[:len(temp_string)]:
						e1 = e1[len(temp_string):]
					if temp_string not in e1 and is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list,
					                                                                              sentence):
						ne_triples.append({'e1': e1, 'rel': r, 'e2': e2})
			# 含有介宾关系的主谓动补关系
			if child_dict.has_key('SBV') and child_dict.has_key('CMP'):
				# e1 = words[child_dict['SBV'][0]]
				e1 = complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
				cmp_index = child_dict['CMP'][0]
				r = words[index] + words[cmp_index]
				if child_dict_list[cmp_index].has_key('POB'):
					e2 = complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						ne_triples.append({'e1': e1, 'rel': r, 'e2': e2})

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
					if is_named_e(e1, NE_list, sentence) and is_named_e(e2, NE_list, sentence):
						ne_triples.append({'e1': e1, 'rel': r, 'e2': e2})
	return ne_triples


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


if __name__ == '__main__':
	text = '''
		奥巴马随母亲和继父前往印度尼西亚首都雅加达生活，并在当地的一所小学就读了两年。四年后他的一家又回到夏威夷，与外祖父母住在一起，从五年级起，他就读于位于火奴鲁鲁的大型私立学校——普纳荷学校（中华民国第一任临时大总统孙文曾于此校就读）至12年级，于1979年毕业，若干年后母亲与继父离婚，他便随母迁居美国本土。青年时期，奥巴马因为自己的多种族背景，很难取得社会认同，十分自卑，他过了一段荒唐的日子，做了很多愚蠢的事，比如逃学、吸毒、泡妞等，成了一个不折不扣的“迷途叛逆少年”。十几岁的他成了一个瘾君子，曾以吸食大麻和可卡因来“将‘我是谁’的问题挤出脑袋”。给青年的他带来深刻影响的不是他的父母亲，而是他的外祖父斯坦利·埃默·邓汉姆和外祖母斯坦利·安·邓汉姆，著名黑人诗人、记者和美国左翼活动家法兰克·米歇尔·戴维斯也是深刻影响青年奥巴马的人物，19世纪60年代戴维斯就成为奥巴马家里的常客。面对猛烈的空中打击和地面进攻，极端组织“伊斯兰国”的大本营拉卡开始出现恐慌，正在加固城防和转移人员。拉卡市位于叙利亚北部，去年初遭“伊斯兰国”占领并作为大本营。当地居民说，由于反“伊斯兰国”武装进逼以及俄罗斯和法国加强空袭，“伊斯兰国”人员近来开始强化防御，在通往这座城市的道路上挖了大量壕沟，他们还在城外堆放许多灌注汽油的轮胎，准备在受到进攻时点燃。由于空袭猛烈，“伊斯兰国”高层命令手下的武装人员撤离营地，躲入居民区，而且只能在小街小巷中移动，以避免被飞机发现，另外，他们下令，夜间禁止开汽车，拉卡原居民哈立德18日告诉美联社记者，10月下旬开始，“伊斯兰国”禁止当地居民逃难，而且最近强化了这一禁令，现在，居民人心惶惶，害怕被“伊斯兰国”用作“人体盾牌”，哈立德眼下居住在土耳其，不过仍与住在拉卡的亲戚朋友保持通信联系。
		'''
# for s in sentences:
# 	print(s)
# print()
# for s in segments_sents:
# 	print([x for x in s])
# print()
# for s in postags_sents:
# 	print([x for x in s])
# print()
