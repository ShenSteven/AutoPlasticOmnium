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
from datetime import datetime
import model.loadseq
import model.product
import conf.globalvar as gv
import conf.logconf as lg
import model.sqlite


def init_database(database_name):
    try:
        if not os.path.exists(database_name):
            with model.sqlite.Sqlite(database_name) as db:
                db.execute('''CREATE TABLE SHA256_ENCRYPTION
                               (NAME TEXT PRIMARY KEY     NOT NULL,
                               SHA256           TEXT    NOT NULL
                               );''')
                db.execute('''CREATE TABLE COUNT
                                           (NAME TEXT PRIMARY KEY     NOT NULL,
                                           VALUE           INT    NOT NULL
                                           );''')
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('continue_fail_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_pass_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_fail_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_abort_count', '0')")
                print(f"Table created successfully")
        if not os.path.exists(gv.database_result):
            with model.sqlite.Sqlite(gv.database_result) as db:
                db.execute('''CREATE TABLE RESULT
                                             (ID            INTEGER PRIMARY KEY AUTOINCREMENT,
                                              SN            TEXT,
                                              STATION_NAME  TEXT    NOT NULL,
                                              STATION_NO    TEXT    NOT NULL,
                                              MODEL         TEXT    NOT NULL,
                                              SUITE_NAME    TEXT    NOT NULL,
                                              ITEM_NAME     TEXT    NOT NULL,
                                              SPEC          TEXT,
                                              LSL           TEXT,
                                              VALUE         TEXT,
                                              USL           TEXT,
                                              ELAPSED_TIME  INT,
                                              ERROR_CODE    TEXT,
                                              ERROR_DETAILS TEXT,
                                              START_TIME    TEXT    NOT NULL,
                                              TEST_RESULT   TEXT    NOT NULL,
                                              STATUS        TEXT    NOT NULL
                                             );''')
                print(f"Table created successfully")
    except Exception as e:
        lg.logger.exception(f'init_database:{e}')


class TestCase:
    tResult = True
    sheetName = ""
    testcase_path_excel = None
    test_script_json = None
    start_time = ""
    finish_time = ""
    original_suites = []
    clone_suites = []

    def __init__(self, testcase_path_excel, sheetName):
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sheetName = sheetName
        self.testcase_path_excel = testcase_path_excel
        self.test_script_json = gv.test_script_json
        init_database(gv.database_setting)
        if os.path.exists(self.test_script_json):
            self.original_suites = model.loadseq.load_testcase_from_json(self.test_script_json)
        else:
            self.original_suites = model.loadseq.load_testcase_from_excel(self.testcase_path_excel, self.sheetName,
                                                                          self.test_script_json)
        self.clone_suites = copy.deepcopy(self.original_suites)

    def run(self, global_fail_continue=False, stepNo=-1):
        suite_result_list = []
        # suite_result = False
        try:
            for i, suite in enumerate(self.clone_suites, start=0):
                if gv.ForFlag:
                    i = gv.ForStartSuiteNo
                    stepNo = gv.ForStartStepNo
                suite_result = self.clone_suites[i].run(global_fail_continue, stepNo)
                suite_result_list.append(suite_result)
                if not suite_result and not global_fail_continue:
                    break

            self.tResult = all(suite_result_list)
            self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return self.tResult
        except Exception as e:
            lg.logger.exception(f"run Exception！！{e}")
            self.tResult = False
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
