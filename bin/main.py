#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
from model.testcase import *

def run():
    test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')
    test_task.run_suites(test_task.test_suites.copy(), True)


run()
