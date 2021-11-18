#!/usr/cf/env python
# coding: utf-8
"""
@File   : testcase.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import copy
from datetime import datetime
import model.loadseq
import model.product
import conf.globalvar as gv


class TestCase:
    tResult = True
    sheetName = ""
    testcase_path_excel = None
    test_script_json = None
    sha256_key_path = None
    start_time = ""
    finish_time = ""
    original_suites = []
    clone_suites = []

    def __init__(self, testcase_path_excel, sheetName):
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sheetName = sheetName
        self.testcase_path_excel = testcase_path_excel
        self.test_script_json = gv.test_script_json
        self.sha256_key_path = gv.SHA256Path
        self.original_suites = model.loadseq.load_testcase_from_json(self.sha256_key_path, self.test_script_json)
        # self.original_suites = model.loadseq.load_testcase_from_excel(self.testcase_path_excel, self.sheetName,
        #                                                               self.test_script_json, self.sha256_key_path, )
        self.clone_suites = copy.deepcopy(self.original_suites)

    def run(self, global_fail_continue=False, stepNo=None):
        suite_result_list = []
        try:
            for i, suite in enumerate(self.clone_suites):
                if gv.ForFlag:
                    i = gv.ForStartSuiteNo
                    stepNo = gv.ForStartStepNo
                suite_result = self.clone_suites[i].run(global_fail_continue, stepNo)
                suite_result_list.append(suite_result)
                if not suite_result and not global_fail_continue:
                    break
            self.tResult = all(suite_result_list)
            self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            from conf.logconf import logger
            logger.exception(f"run Exception！！{e}")
            self.tResult = False
            return self.tResult
        else:
            return self.tResult
        finally:
            self.copy_to_station(gv.stationObj)
            self.copy_to_mes(gv.mesPhases)
            self.clear()

    def copy_to_station(self, obj: model.product.JsonResult):
        obj.status = 'passed' if self.tResult else 'failed'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = gv.error_code_first_fail
        obj.error_details = gv.error_details_first_fail

    def copy_to_mes(self, obj: model.product.MesInfo):
        obj.status = 'PASS' if self.tResult else 'FAIL'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = gv.error_code_first_fail
        obj.error_details = gv.error_details_first_fail

    def clear(self):
        self.tResult = True

    if __name__ == "__main__":
        pass
