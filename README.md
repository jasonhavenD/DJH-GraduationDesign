undergraduate graduation design  for Chinese relation extraction

---
- env:
python2.7

---

- data
	- crawl
		- chinaautonews.txt : original web text
	- corpus
		- ne_corpus.txt : corpus with ne pos
	- extraction
		- triples.txt : all triples
		- ne_triples.txt : only named entity triples
	- preprocess :
		- chinaautonews.txt : original web text but simplified
		- sentences.txt : sentences from chinaautonews.txt
		- segments.txt
		- postags.txt
		- ners.txt
- src
	- crawl
		- crawler
			- chinaautonews_crawler.py : crawler for [中国汽车新闻网](http://www.chinaautonews.com.cn/list-6-1.html)
		- ip_pool
			- main.pt start
			- IPCrawler.py : crawler for http://www.xicidaili.com/nn/
			- daili.txt : all proxies
			- ip_pool.txt : useable proxies
		- util
			- io.py : iohelper
			- log.py : logger
			- tool.py : tool for ip pool
	- preprocess
		- convert2simple.py : chinese convert
		- ner.py
		- postag.py
		- readme.md
		- segment.py
		- sentence_split.py
	- extraction
		- LTP_MODEL.py : test for CONRE
		- make_corpora.py : generate corpus
		- ne_re.py : extract triples(all triples and ne_triples)
	- CONRE
		- static
		- templates
		- util
			- io.py : iohelper
			- log.py : logger
		- LTP_MODEL.py : model for ne_re
		- ne_re.py : extract form form posted from user
		- start_server.py : start and process
	- db
		- save2mongo.py : save triples to mongo
		- save2neo4j.py : save triples from mango to neo4j
#### test script

```shell
cd /home/jasonhaven/workspace/github/DJH-GraduationDesign/src/preprocess
python convert2simple.py
python convert_raw2one.py
python sentence_split.py
python segment.py
python2 postag.py
python2 ner.py
cd ../extraction
pyhthon ne_re
cd ../db
python2 save2mongo.py
```
