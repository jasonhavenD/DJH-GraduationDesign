#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:convert_raw2one
   Author:jasonhaven
   date:2018/4/19
-------------------------------------------------
   Change Activity:2018/4/19:
-------------------------------------------------
"""
import os
import codecs

if __name__ == '__main__':
	input_dir = "../../data/raw"
	output = "../../data/raw/merged.txt"
	fout = codecs.open(output, 'w', encoding='utf-8')
	for parent, dir_names, file_names in os.walk(input_dir):
		for file in file_names:
			path = parent + os.sep + file
			with codecs.open(path, 'r', encoding='utf-8') as f:
				text = f.read()
				fout.write(text)
				fout.write("\n")
	fout.close()

