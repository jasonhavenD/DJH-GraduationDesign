#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:convert2simple
   Author:jason
   date:18-4-23
-------------------------------------------------
   Change Activity:18-4-23:
-------------------------------------------------
"""

import sys

sys.path.append('../util/')

import pyltp
from util.io import IOHelper
from util.log import Logger

logger = Logger().get_logger()

if __name__ == '__main__':
	input = '../../data/preprocess/simple.txt'
	output = '../../data/preprocess/sentences.txt'
	text = IOHelper.read(input)
	sents = pyltp.SentenceSplitter.split(text.strip())
	IOHelper.write_lines(output, sents)
	logger.info('finished!......')
