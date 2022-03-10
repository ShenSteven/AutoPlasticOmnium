#!/usr/bin/env python
# coding: utf-8
"""
@File   : __init__.py.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""
import os
import sys
from os.path import abspath, join, dirname


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
    # we are running in a bundle
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
