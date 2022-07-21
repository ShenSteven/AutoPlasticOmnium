#!/usr/bin/env python
# coding: utf-8
"""
@File   : __init__.py.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""
import os
import re
import sys
from os.path import abspath, join, dirname


def match(path):
    basename = os.path.basename(path)
    return re.match("^_MEI\d+$", basename) and True or False


def get_about():
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), '__version__.py'), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


about = get_about()

# get app dir path
current_dir = ''
if getattr(sys, 'frozen', False):
    # we are running in a bundle,.exe run
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
# module = os.path.split(current_dir)[0]
# sys.path.append(module)
#
# for index, path in enumerate(sys.path):
#     print(sys.path[index])
#     if match(path):
#         print(path)
