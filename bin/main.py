#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
from model.testcase import *


def run(is_cyclic=False):
    test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')

    if is_cyclic:
        while True:
            test_task.run_suites(test_task.test_suites.copy(), True, 0, 2)
    else:
        test_task.run_suites(test_task.test_suites.copy(), True)


run(True)
