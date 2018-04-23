#! /usr/bin/env/python
#
# coding utf-8
#
# jasonahven
#


import random
import re


class Clean_html:
	# 去除img标签,7位长空格
	removeImg = re.compile('<img.*?>| {7}|')
	# 删除超链接标签
	removeAddr = re.compile('<a.*?>|</a>')
	# 把换行的标签换为\n
	replaceLine = re.compile('<tr>|<div>|</div>|</p>')
	# 将表格制表<td>替换为\t
	replaceTD = re.compile('<td>')
	# 把段落开头换为\n加空两格
	replacePara = re.compile('<p.*?>')
	# 将换行符或双换行符替换为\n
	replaceBR = re.compile('<br><br>|<br>')
	# 将其余标签剔除
	removeExtraTag = re.compile('<.*?>')
	# 将空行删除
	removeEmpty = re.compile(r'\n\n')

	def clean(self, x):
		x = re.sub(self.removeImg, "", x)
		x = re.sub(self.removeAddr, "", x)
		x = re.sub(self.replaceLine, "\n", x)
		x = re.sub(self.replaceTD, "\t", x)
		x = re.sub(self.replacePara, "\n    ", x)
		x = re.sub(self.replaceBR, "\n", x)
		x = re.sub(self.removeEmpty, "", x)
		x = re.sub(self.removeExtraTag, "", x)
		# strip()将前后多余内容删除
		return x.strip()


def get_random_proxy():
	ips = []
	with open('../ip_pool/ip_pool.txt', 'r') as f:
		ips = f.readlines()
	ip_port = random.choice(ips).strip()
	ip, port = ip_port.split(u":")[0].strip(), ip_port.split(u":")[1].strip()
	proxy = {'http': 'http://%s:%s' % (ip, port)}
	return proxy


def get_proxies():
	proxies = []
	with open('../ip_pool/ip_pool.txt', 'r') as f:
		for ip_port in f.readlines():
			ip, port = ip_port.split(u":")[0].strip(), ip_port.split(u":")[1].strip()
			proxy = {'http': 'http://%s:%s' % (ip, port)}
			proxies.append(proxy)
	return proxies
