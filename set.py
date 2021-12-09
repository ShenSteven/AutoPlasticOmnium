#!/usr/bin/env python
# coding: utf-8
"""
@File   : set.py.py
@Author : Steven.Shen
@Date   : 2021/12/8
@Desc   : 
"""
import os
import sys

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    current_path = sys._MEIPASS
else:
    current_path = os.path.dirname(os.path.abspath(__file__))
