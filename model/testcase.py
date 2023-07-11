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
import model.loadseq
import model.product
import database.sqlite
import model.variables
import conf.globalvar as gv
import sockets.serialport
from inspect import currentframe
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox


def get_keywords_list(path):
    with open(path, 'r', encoding='utf-8') as rf:
        keywords = [item.strip() for item in rf.readlines()]
        return keywords


class TestCase:
    """testcase class,edit all testcase in an Excel file, categorized by test station or testing feature in sheet."""

    def __init__(self, testcase_path, sheet_name, logger, wind=None, cflag=True, isVerify=True):
        self.sum_step = 0
        self.step_finish_num = 0
        self.step_count = 0
        self.header = []
        self.myWind = wind
        self.FixSerialPort = None  # 治具串口通信
        self.dut_comm = None  # DUT通信
        self.NiInstrComm = None
        self.clone_suites = None
        self.original_suites = None
        self.logger = logger
        self.testcase_path = None
        self.sheetName = None
        self.error_details_first_fail = ''
        self.error_code_first_fail = ''
        self.suite_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.finish_time = ''
        self.tResult = True
        self.ForStartSuiteNo = 0
        self.ForFlag = False
        self.ForStartStepNo = 0
        self.ForTotalCycle = 0
        self.ForCycleCounter = 1
        self.IfCond = True
        self.Finished = False
        self.failCount = 0
        self.startTimeJsonFlag = True
        self.startTimeJson = datetime.now()
        self.mesPhases: model.product.MesInfo
        self.jsonObj: model.product.JsonObject
        self.ArrayListDaq = []
        self.ArrayListDaqHeader = ['SN', 'DateTime']
        self.daq_data_path = ''
        self.csv_list_header = []
        self.csv_list_data = []
        self.csv_file_path = ''
        database.sqlite.init_sqlite_database(self.logger, gv.database_setting)
        self.load_testcase(testcase_path, sheet_name, logger, cflag, isVerify)

    @property
    def test_script_json(self):
        return rf'{gv.scriptFolder}{os.sep}{self.sheetName}.json'

    def load_testcase(self, testcase_path, sheet_name, logger, cflag, isVerify):
        try:
            self.sheetName = sheet_name
            self.testcase_path = testcase_path
            self.logger = logger
            if not getattr(sys, 'frozen', False) and cflag:
                model.loadseq.excel_convert_to_json(self.testcase_path, gv.cf.station.station_all, self.logger)
            if not os.path.exists(self.test_script_json):
                model.loadseq.excel_convert_to_json(self.testcase_path, [sheet_name], self.logger)
            if gv.isHide:
                self.original_suites, self.header, self.step_count = model.loadseq.load_testcase_from_py(self.sheetName)
            else:
                self.original_suites, self.header, self.step_count = model.loadseq.load_testcase_from_json(
                    self.test_script_json, isVerify)
            self.clone_suites = copy.deepcopy(self.original_suites)
            gv.Keywords = get_keywords_list(rf'{gv.current_dir}{os.sep}conf{os.sep}keywords.txt')
            self.sum_step = self.step_count
        except Exception as e:
            QMessageBox.critical(None, 'ERROR!', f'{currentframe().f_code.co_name}:{e} ', QMessageBox.Yes)
            # QMetaObject.invokeMethod(
            #     self.myWind,
            #     'showMessageBox',
            #     Qt.BlockingQueuedConnection,
            #     QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
            #     QtCore.Q_ARG(str, 'ERROR!'),
            #     QtCore.Q_ARG(str, f'{currentframe().f_code.co_name}:{e}'),
            #     QtCore.Q_ARG(int, 4))
            raise

    def run(self, global_fail_continue=False):
        try:
            for i, suite in enumerate(self.clone_suites, start=0):
                if self.ForFlag:
                    if i < self.ForStartSuiteNo:
                        continue
                    else:
                        stepNo = self.ForStartStepNo
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
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e},{traceback.format_exc()}')
            self.tResult = False
            return self.tResult
        finally:
            self.copy_to_json(self.jsonObj)
            self.copy_to_mes(self.mesPhases)
            self.clear()
            self.teardown()
            self.Finished = True

    def copy_to_json(self, obj: model.product.JsonObject):
        obj.status = 'passed' if self.tResult else 'failed'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.error_code_first_fail
        obj.error_details = self.error_details_first_fail

    def copy_to_mes(self, obj: model.product.MesInfo):
        obj.status = 'PASS' if self.tResult else 'FAIL'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.error_code_first_fail
        obj.error_details = self.error_details_first_fail

    def clear(self):
        self.tResult = True
        self.suite_result_list = []
        self.sum_step = self.step_count

    def teardown(self):
        if self.dut_comm is not None:
            self.dut_comm.close()
        if gv.PLin is not None:
            gv.PLin.close()
        if gv.cf.station.fix_flag and gv.cf.station.pop_fix and self.FixSerialPort is not None:
            self.FixSerialPort.open()
            self.FixSerialPort.sendCommand('AT+TESTEND%', )

    def get_stationNo(self):
        """通过串口读取治具中设置的测试工站名字"""
        if not gv.cf.station.fix_flag:
            return
        self.FixSerialPort = sockets.serialport.SerialPort(gv.cf.station.fix_com_port,
                                                           gv.cf.station.fix_com_baudRate)
        for i in range(0, 3):
            rReturn, revStr = self.FixSerialPort.SendCommand('AT+READ_FIXNUM%', '\r\n', 1, False)
            if rReturn:
                gv.cf.station.station_no = revStr.replace('\r\n', '').strip()
                gv.cf.station.station_name = gv.cf.station.station_no[0, gv.cf.station.station_no.index('-')]
                self.logger.debug(f"Read fix number success,stationName:{gv.cf.station.station_name}")
                break
        else:
            QMessageBox.Critical(self, 'Read StationNO', "Read FixNum error,Please check it!")
            sys.exit(0)

    if __name__ == "__main__":
        pass
