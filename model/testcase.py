#!/usr/bin/env python
# coding: utf-8
"""
@File   : testcase.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import copy
import os
import sys
import traceback
from datetime import datetime
import model.loadseq
import model.product
import model.sqlite
import conf.globalvar as gv
# import conf.logprint as lg
from inspect import currentframe


class TestCase:
    """testcase class,edit all testcase in an Excel file, categorized by test station or testing feature in sheet."""

    def __init__(self, testcase_path, sheet_name):
        self.suite_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.finish_time = ''
        self.tResult = True
        self.sheetName = sheet_name
        self.testcase_path = testcase_path
        self.test_script_json = gv.test_script_json
        self.ForStartSuiteNo = 0
        self.ForFlag = False
        self.Finished = False
        model.sqlite.init_database(gv.database_setting)
        if not getattr(sys, 'frozen', False):
            model.loadseq.excel_convert_to_json(self.testcase_path, gv.cf.station.station_all)
        if os.path.exists(self.test_script_json):
            self.original_suites = model.loadseq.load_testcase_from_json(self.test_script_json)
        else:
            self.original_suites = model.loadseq.load_testcase_from_excel(self.testcase_path,
                                                                          self.sheetName,
                                                                          self.test_script_json)
        self.clone_suites = copy.deepcopy(self.original_suites)

    def run(self, global_fail_continue=False):
        try:
            for i, suite in enumerate(self.clone_suites, start=0):
                if self.ForFlag:
                    if i < self.ForStartSuiteNo:
                        continue
                    else:
                        stepNo = gv.ForStartStepNo
                else:
                    stepNo = -1
                suite_result = self.clone_suites[i].run(self, global_fail_continue, stepNo)
                self.suite_result_list.append(suite_result)
                if not suite_result and not global_fail_continue:
                    break
                if self.ForFlag:
                    return self.run(global_fail_continue)

            self.tResult = all(self.suite_result_list)
            self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return self.tResult
        except Exception as e:
            gv.lg.logger.fatal(f'{currentframe().f_code.co_name}:{e},{traceback.format_exc()}')
            self.tResult = False
            return self.tResult
        finally:
            self.copy_to_json(gv.stationObj)
            self.copy_to_mes(gv.mesPhases)
            self.clear()
            self.teardown()
            self.Finished = True

    def copy_to_json(self, obj: model.product.JsonObject):
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
        self.suite_result_list = []

    def teardown(self):
        if gv.dut_comm is not None:
            gv.dut_comm.close()
        if gv.PLin is not None:
            gv.PLin.close()
        if gv.cf.station.fix_flag and gv.cf.station.pop_fix and gv.FixSerialPort is not None:
            gv.FixSerialPort.open()
            gv.FixSerialPort.sendCommand('AT+TESTEND%', )

    if __name__ == "__main__":
        pass
