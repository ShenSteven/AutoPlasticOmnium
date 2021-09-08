#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
from bin import globalvar
from bin.basefunc import create_csv_file, write_csv_file
from model.testcase import *


def run(is_cyclic=False):
    test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')
    if is_cyclic:
        while True:
            test_task.run_suites(test_task.test_suites.copy(), True, 0, 2)
    else:
        create_csv_file('result.csv', ['No', 'Phase name', 'Test name', 'Error Code'])
        test_task.run_suites(test_task.test_suites.copy(), True)
        print(globalvar.csv_list_result)
        write_csv_file('result.csv', globalvar.csv_list_result)
        write_csv_file('result.csv', globalvar.csv_list_header)


run(False)
