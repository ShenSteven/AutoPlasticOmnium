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
import models.loadseq
import models.product
import dataaccess.sqlite
import models.variables
import conf.globalvar as gv
import communication.serialport
import bll.flowcontrol.ifelse
from inspect import currentframe
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from common.basicfunc import get_line_list


class TestCase:
    """testcase class,edit all testcase in an Excel file, categorized by test station or testing feature in sheet."""

    def __init__(self, testcase_path, sheet_name, logger, wind=None, cflag=True, isVerify=True):
        self.sumStep = 0
        self.stepFinishNum = 0
        self.stepCount = 0
        self.header = []
        self.myWind = wind
        self.FixSerialPort = None  # 治具串口通信
        self.dutComm = None  # DUT通信
        self.NiInstrComm = None
        self.cloneSuites = None
        self.originalSuites = None
        self.logger = logger
        self.testcasePath = None
        self.sheetName = None
        self.errorDetailsFirstFail = ''
        self.errorCodeFirstFail = ''
        self.suiteResultList = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.finish_time = ''
        self.tResult = True
        self.ForLoop = None
        self.DoWhileLoop = None
        self.WhileLoop = None
        self.loop = None
        self.IfElseFlow = bll.flowcontrol.ifelse.IfElse(self.logger)
        self.Finished = False
        self.failCount = 0
        self.startTimeJsonFlag = True
        self.startTimeJson = datetime.now()
        self.mesPhases: models.product.MesInfo = None
        self.jsonObj: models.product.JsonObject = None
        self.ArrayListDaq = []
        self.ArrayListDaqHeader = ['SN', 'DateTime']
        self.daqDataPath = ''
        self.csvListHeader = []
        self.csvListData = []
        self.csvFilePath = ''
        dataaccess.sqlite.init_sqlite_database(self.logger, gv.DatabaseSetting)
        self.load_testcase(testcase_path, sheet_name, logger, cflag, isVerify)

    @property
    def test_script_json(self):
        return rf'{gv.ScriptFolder}{os.sep}{self.sheetName}.json'

    def load_testcase(self, testcase_path, sheet_name, logger, cflag, isVerify):
        try:
            self.sheetName = sheet_name
            self.testcasePath = testcase_path
            self.logger = logger
            if not getattr(sys, 'frozen', False) and cflag:
                models.loadseq.excel_convert_to_json(self.testcasePath, gv.cfg.station.stationAll, self.logger)
            if not os.path.exists(self.test_script_json):
                models.loadseq.excel_convert_to_json(self.testcasePath, [sheet_name], self.logger)
            if gv.IsHide:
                self.originalSuites, self.header, self.stepCount = models.loadseq.load_testcase_from_py(self.sheetName)
            else:
                self.originalSuites, self.header, self.stepCount = models.loadseq.load_testcase_from_json(
                    self.test_script_json, isVerify)
            self.cloneSuites = copy.deepcopy(self.originalSuites)
            gv.Keywords = get_line_list(rf'{gv.CurrentDir}{os.sep}conf{os.sep}keywords.txt')
            self.sumStep = self.stepCount
        except Exception as e:
            QMessageBox.critical(None, 'load_testcase error!', f'{currentframe().f_code.co_name}:{e} ', QMessageBox.Yes)
            raise

    def run(self):
        try:
            for i, suite in enumerate(self.cloneSuites, start=0):

                if self.loop is not None and not self.loop.IsEnd and self.loop.jump:
                    if i < self.loop.StartSuiteNo:
                        continue
                    else:
                        stepNo = self.loop.StartStepNo
                elif self.ForLoop is not None and not self.ForLoop.IsEnd and self.ForLoop.jump:
                    if i < self.ForLoop.StartSuiteNo:
                        continue
                    else:
                        stepNo = self.ForLoop.StartStepNo
                elif self.DoWhileLoop is not None and not self.DoWhileLoop.IsEnd and self.DoWhileLoop.jump:
                    if i < self.DoWhileLoop.StartSuiteNo:
                        continue
                    else:
                        stepNo = self.DoWhileLoop.StartStepNo
                elif self.WhileLoop is not None and not self.WhileLoop.IsEnd and self.WhileLoop.jump:
                    if i < self.WhileLoop.StartSuiteNo:
                        continue
                    else:
                        stepNo = self.WhileLoop.StartStepNo
                else:
                    stepNo = -1

                suite_result = suite.run(self, stepNo)
                self.suiteResultList.append(suite_result)
                if not suite_result:
                    break

                if self.loop is not None and self.loop.IsEnd and self.loop.jump:
                    return self.run()
                if self.ForLoop is not None and not self.ForLoop.IsEnd and self.ForLoop.jump:
                    return self.run()
                if self.DoWhileLoop is not None and not self.DoWhileLoop.IsEnd and self.DoWhileLoop.jump:
                    return self.run()
                if self.WhileLoop is not None and not self.WhileLoop.IsEnd and self.WhileLoop.jump:
                    return self.run()

            self.tResult = all(self.suiteResultList)
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

    def copy_to_json(self, obj: models.product.JsonObject):
        obj.status = 'passed' if self.tResult else 'failed'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.errorCodeFirstFail
        obj.error_details = self.errorDetailsFirstFail

    def copy_to_mes(self, obj: models.product.MesInfo):
        obj.status = 'PASS' if self.tResult else 'FAIL'
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.errorCodeFirstFail
        obj.error_details = self.errorDetailsFirstFail

    def clear(self):
        self.tResult = True
        self.suiteResultList = []
        self.sumStep = self.stepCount
        self.stepFinishNum = 0
        self.ForLoop = None
        self.DoWhileLoop = None
        self.WhileLoop = None
        self.IfElseFlow = bll.flowcontrol.ifelse.IfElse(self.logger)
        self.loop = None

    def teardown(self):
        if self.dutComm is not None:
            self.dutComm.close()
        if gv.PLin is not None:
            gv.PLin.close()
        if gv.cfg.station.fixFlag and gv.cfg.station.pop_fix and self.FixSerialPort is not None:
            self.FixSerialPort.open()
            self.FixSerialPort.sendCommand('AT+TESTEND%', )

    def get_stationNo(self):
        """通过串口读取治具中设置的测试工站名字"""
        if not gv.cfg.station.fixFlag:
            return
        self.FixSerialPort = communication.serialport.SerialPort(gv.cfg.station.fixComPort,
                                                                 gv.cfg.station.fixComBaudRate)
        for i in range(0, 3):
            rReturn, revStr = self.FixSerialPort.SendCommand('AT+READ_FIXNUM%', '\r\n', 1, False)
            if rReturn:
                gv.cfg.station.stationNo = revStr.replace('\r\n', '').strip()
                gv.cfg.station.stationName = gv.cfg.station.stationNo[0, gv.cfg.station.stationNo.index('-')]
                self.logger.debug(f"Read fix number success,stationName:{gv.cfg.station.stationName}")
                break
        else:
            QMessageBox.Critical(self, 'Read StationNO', "Read FixNum error,Please check it!")
            sys.exit(0)

    if __name__ == "__main__":
        pass
