#!/usr/c/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
import json
import time
import requests
# from conf import globalvar as gv
from model.basefunc import create_csv_file, write_csv_file
from model.testcase import *


def run(is_cyclic=False, single_step=True):
    test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')

    if is_cyclic:
        while True:
            test_task.run(test_task.test_suites.copy(), True, 0)
    elif single_step:
        test_task.test_suites.copy()[0].test_steps[2].run()
    else:
        create_csv_file('result.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
        test_task.run(test_task.test_suites.copy(), True)
        print(gv.csv_list_result)
        write_csv_file('result.csv', gv.csv_list_result)
        write_csv_file('result.csv', gv.csv_list_header)


run(False)

print(time.strftime("%Y-%m-%d %H:%M:%S"))


def upload_result_to_mes(url):
    logger.debug(json.dumps(gv.mesPhases, default=lambda o: o.__dict__,
                            sort_keys=True,
                            indent=4))
    response = requests.post(url, logger.debug(json.dumps(gv.mesPhases, default=lambda o: o.__dict__,
                                                          sort_keys=True,
                                                          indent=4)))
    if response.status_code == 200:
        return True
    else:
        logger.debug(f'post fail:{response.content}')
        return False
