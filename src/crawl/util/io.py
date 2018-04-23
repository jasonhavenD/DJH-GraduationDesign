#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:io
   Author:jasonhaven
   date:2018/4/17
-------------------------------------------------
   Change Activity:2018/4/17:
-------------------------------------------------
"""


class IOHelper():
	def __init__(self):
		self.result_path = "../result"

	# self.result_path = "result"

	def write(self, fdir, fname, ftype):
		print("write()")
		pass

	def read(self, fdir, fname, ftype):
		print("read()")
		pass


if __name__ == '__main__':
	io = IOHelper()
	io.read('', '', '')
	io.write('', '', '')
