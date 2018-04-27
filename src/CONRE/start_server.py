#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:start_server
   Author:jason
   date:18-4-25
-------------------------------------------------
   Change Activity:18-4-25:
-------------------------------------------------
"""
import sys
import json
from hanziconv import HanziConv

reload(sys)
sys.setdefaultencoding('utf-8')

import LTP_MODEL
from py2neo import Graph, Node, Relationship
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)


@app.route('/CONRE')
@app.route('/CONRE/home')
@app.route('/CONRE/index')
@app.route('/CONRE/index.html')
def index():
	return render_template('index.html')


@app.route('/CONRE/triples', methods=['GET'])
def show_triples_of_database():
	entities, triples = query_all_triples_of_database()
	result = {'entities': entities, 'triples': triples}
	return render_template('triples of database.html', result=result)


@app.route('/CONRE/extract', methods=['POST'])
def extract():
	result = {}
	entities = set()
	triples = []
	text = request.form.get('text').strip()

	# entities = ['小明', '小红', '小红红', '大明明', '大红红']
	# tpl1 = {'e1': '小明', 'rel': 'like1', 'e2': '小红'}
	# tpl2 = {'e1': '小明', 'rel': 'like2', 'e2': '小红红'}
	# tpl3 = {'e1': '大明明', 'rel': 'like4', 'e2': '大红红'}
	# triples = [tpl1, tpl2, tpl3]
	text = HanziConv.toSimplified(text).encode('utf-8')
	sentences, segments_sents, postags_sents, ne_triples_sents = LTP_MODEL.ner_extract(text)
	for tpls in ne_triples_sents:
		# save to neo4j
		insert_triples(tpls)  # [{'e1':e1,'rel',rel,'e2':e2}]
		# save to result
		for triple in tpls:
			e1 = triple['e1'].strip()
			e2 = triple['e2'].strip()
			if len(e1) < 2 or len(e2) < 2:
				continue
			entities.add(e1)
			entities.add(e2)
			triples.append(triple)
	result['sentences'] = json.dumps(sentences, default=sentences2dict)
	result['segmentses'] = json.dumps(segments_sents, default=type2dict)
	result['postagses'] = json.dumps(postags_sents, default=type2dict)
	result['entities'] = list(entities)
	result['triples'] = triples
	return jsonify(result)

def sentences2dict(sentences):
	lst = []
	for sent in sentences:
		lst.append(sent)
	return {'sents': lst}

def type2dict(obj):
	lst = []
	for sent in obj:
		lst.append(unicode(sent,errors='ignore'))
	return {'sent': ' '.join(lst)}


def query_all_triples_of_database():
	entities = set()
	triples = []
	statement = "match (e1)-[rel]->(e2) return e1,rel,e2"
	result = graph.run(statement).data()
	for rst in result:
		e1, rel, e2 = rst['e1'], rst['rel'], rst['e2']
		dct = {}
		dct['e1'] = e1['name']
		dct['rel'] = rel.type()
		dct['e2'] = e2['name']
		entities.add(e1['name'])
		entities.add(e2['name'])
		triples.append(dct)
	return list(entities), triples


@app.route('/CONRE/query_by_node', methods=['POST'])
def query_by_node():
	name = request.form.get('name')
	entities = set()
	triples = []
	statement1 = "match (e1:Sub {name:'%s'})-[rel]-(e2) return e1,rel,e2" % name
	statement2 = "match (e1)-[rel]-(e2:Obj {name:'%s'}) return e1,rel,e2" % name

	result1 = graph.run(statement1).data()
	result2 = graph.run(statement2).data()
	for rst in result1:
		e1, rel, e2 = rst['e1'], rst['rel'], rst['e2']
		# print(e1['name'], rel.type(), e2['name'])
		dct = {}
		dct['e1'] = e1['name']
		dct['rel'] = rel.type()
		dct['e2'] = e2['name']
		entities.add(e1['name'])
		entities.add(e2['name'])
		triples.append(dct)

	for rst in result2:
		e1, rel, e2 = rst['e1'], rst['rel'], rst['e2']
		# print(e1['name'], rel.type(), e2['name'])
		dct = {}
		dct['e1'] = e1['name']
		dct['rel'] = rel.type()
		dct['e2'] = e2['name']
		entities.add(e1['name'])
		entities.add(e2['name'])
		triples.append(dct)

	result = {'entities': list(entities), 'triples': triples}
	return jsonify(result), 200


@app.route('/CONRE/query_by_relation', methods=['POST'])
def query_by_relation():
	relation = request.form.get('relation')
	entities = set()
	triples = []
	results = graph.match(rel_type=relation)
	for rst in results:
		e1, e2 = rst.nodes()
		dct = {}
		dct['e1'] = e1['name']
		dct['rel'] = relation
		dct['e2'] = e2['name']
		entities.add(e1['name'])
		entities.add(e2['name'])
		triples.append(dct)
	result = {'entities': list(entities), 'triples': triples}
	return jsonify(result), 200


def insert_triples(triples):
	'''
	triple={'e1':value,'e2':value,'rel':value}
	'''
	for triple in triples:
		e1 = triple['e1'].strip()
		e2 = triple['e2'].strip()
		if len(e1) < 2 or len(e2) < 2:
			continue
		rel = triple['rel'].strip()
		e1_node = Node('Sub', name=e1)
		e2_node = Node('Obj', name=e2)
		# find first
		exist_e1_node = graph.find_one('Sub', 'name', e1)
		exist_e2_node = graph.find_one('Obj', 'name', e2)
		if exist_e1_node != None:
			e1_node = exist_e1_node
		if exist_e2_node != None:
			e2_node = exist_e2_node
		relation_node = Relationship(e1_node, rel, e2_node)
		all = e1_node | e2_node | relation_node
		graph.create(all)


if __name__ == '__main__':
	graph = Graph('http://172.19.12.30:7474/db/data', username='neo4j', password='root')
	app.run(threaded=True)
