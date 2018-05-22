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

from hanziconv import HanziConv
from util.io import IOHelper
from util.log import Logger

logger = Logger().get_logger()

if __name__ == '__main__':
	input_raw = '../../data/raw/merged.txt'
	output_raw = '../../data/preprocess/simple.txt'
	text = IOHelper.read(input_raw)
	text = HanziConv.toSimplified(text)
	IOHelper.write(output_raw, text)
	logger.info('finished!')
