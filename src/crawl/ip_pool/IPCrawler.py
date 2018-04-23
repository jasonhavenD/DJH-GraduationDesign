#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:IPCrawler
   Author:jasonhaven
   date:2018/4/18
-------------------------------------------------
   Change Activity:2018/4/18:
-------------------------------------------------
"""
import urllib.request
from lxml import etree
import time
import socket

# socket.setdefaulttimeout(30)  # 设置socket层的超时时间为20秒


def get_url(url, nums):  # 国内高匿代理的链接
	url_list = []
	for i in range(1, nums):
		url_new = url + str(i)
		url_list.append(url_new)
	return url_list


def get_content(url):  # 获取网页内容
	user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
	headers = {'User-Agent': user_agent}
	req = urllib.request.Request(url=url, headers=headers)
	res = urllib.request.urlopen(req)
	content = res.read()
	return content.decode('utf-8')


def get_info(content):  # 提取网页信息 / ip 端口
	datas_ip = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[2]/text()')
	datas_port = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[3]/text()')
	with open("daili.txt", "a") as fd:
		for i in range(0, len(datas_ip)):
			out = u""
			out += u"" + datas_ip[i]
			out += u":" + datas_port[i]
			fd.write(out + u"\n")  # 所有ip和端口号写入data文件


def verif_ip(ip, port,test_url):  # 验证ip有效性
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
		"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
	}
	proxy = {'http': 'http://%s:%s' % (ip, port)}
	print(proxy)

	proxy_handler = urllib.request.ProxyHandler(proxy)
	opener = urllib.request.build_opener(proxy_handler)
	urllib.request.install_opener(opener)

	req = urllib.request.Request(url=test_url, headers=headers)
	time.sleep(2)
	try:
		res = urllib.request.urlopen(req)
		content = res.read()
		if content:
			print('that is ok')
			with open("ip_pool.txt", "a") as fd:  # 有效ip保存到ip_pool文件
				fd.write(ip + u":" + port)
				fd.write("\n")
		else:
			print('its not ok')
		res.close()
	except urllib.request.URLError as e:
		print(e.reason)
