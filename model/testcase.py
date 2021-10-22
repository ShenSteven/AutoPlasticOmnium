#!/usr/c/env python
# coding: utf-8
"""
@File   : testcase.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
from datetime import datetime
from model.loadseq import load_testcase_from_excel, load_testcase_from_json
from conf.globalconf import logger
from conf import globalvar as gv
from model.product import JsonResult, MesInfo


class TestCase:
    tResult = True
    sheetName = ""
    testcase_path_excel = None
    testcase_path_json = None
    sha256_key_path = None
    start_time = ""
    finish_time = ""
    test_suites = []

    def __init__(self, testcase_path_excel, sheetName):
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sheetName = sheetName
        self.testcase_path_excel = testcase_path_excel
        self.testcase_path_json = gv.testcaseJsonPath
        self.sha256_key_path = gv.SHA256Path
        self.test_suites = load_testcase_from_excel(self.testcase_path_excel, self.sheetName, self.testcase_path_json,
                                                    self.sha256_key_path)
        # self.test_suites = load_testcase_from_json(self.sha256_key_path, self.testcase_path_json)

    def run(self, test_suites, global_fail_continue=False, stepNo=None):
        suite_result_list = []
        try:
            for i, suite in enumerate(test_suites):
                if gv.ForFlag:
                    i = gv.ForStartSuiteNo
                    stepNo = gv.ForStartStepNo
                suite_result = test_suites[i].run(global_fail_continue, stepNo)
                suite_result_list.append(suite_result)
                if not suite_result and not global_fail_continue:
                    break
                else:
                    pass
            self.tResult = all(suite_result_list)
            self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.exception(f"run Exception！！{e}")
            self.tResult = False
            return self.tResult
        else:
            return self.tResult
        finally:
            self.copy_to_station(gv.stationObj)
            self.copy_to_mes(gv.mesPhases)
            self.clear()

    def copy_to_station(self, obj: JsonResult):
        obj.status = 'passed' if self.tResult else 'failed'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = gv.error_code_first_fail
        obj.error_details = gv.error_details_first_fail

    def copy_to_mes(self, obj: MesInfo):
        obj.status = 'PASS' if self.tResult else 'FAIL'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = gv.error_code_first_fail
        obj.error_details = gv.error_details_first_fail

    def clear(self):
        self.tResult = True


if __name__ == "__main__":
    pass
    # ss = load_sequences_from_excel("./Config/fireflyALL.xlsx", 'MBLT')  # ./Config/fireflyALL.xlsx
    # testcase1 = TestCase(r"F:\pyside2\c\fireflyALL.xlsx", 'MBLT')
    # testingSuite = testcase1.test_suites.copy()
    # testcase1.run(testingSuite)
