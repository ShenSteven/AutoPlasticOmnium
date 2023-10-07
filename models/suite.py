#!/usr/bin/env python
# coding: utf-8
"""
@File   : suite.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import traceback
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
import models.product
import models.step
from common.basicfunc import create_csv_file, write_csv_file
import ui.mainform


class TestSuite:

    def __init__(self, suiteName=None, test_serial=None, dict_=None):
        self.myWind = None
        self.logger = None
        self.name = suiteName
        self._index = test_serial
        self.isTest = True
        self.suiteResult = True
        self.isTestFinished = False
        self.totalNum = 0
        self.suiteVar = ''
        self.steps = []
        self.start_time = ""
        self.finish_time = ""
        self.error_code = ''
        self.phase_details = ''
        self.elapsedTime = None
        if dict_ is not None:
            self.__dict__.update(dict_)

    @property
    def index(self):
        if self.myWind is not None:
            self._index = self.myWind.testcase.cloneSuites.index(self)
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    def run(self, test_case, stepNo=-1):
        """
        run test suite.
        :param test_case:
        :param global_fail_continue: a boolean indicate step or continue when test fail.
        :param stepNo:
        :return:test result,pass or fail.
        """
        self.myWind = test_case.myWind
        if self.logger is None:
            self.logger = test_case.logger
        if not self.isTest:
            test_case.sumStep = test_case.sumStep - self.totalNum
            self.myWind.mySignals.updateProgressBar[int, int].emit(test_case.stepFinishNum, test_case.sumStep)
            self.setColor(Qt.gray)
            self.suiteResult = True
            return self.suiteResult
        self.logger.debug('- ' * 8 + f"<a name='testSuite:{self.name}'>Start testSuite:{self.name}</a>" + '- ' * 9)
        self.setColor(Qt.yellow)
        suiteItem = models.product.SuiteItem()
        step_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            for i, step in enumerate(self.steps, start=0):
                if i < stepNo:
                    continue
                step.suiteVar = self.suiteVar
                step_result = step.run(test_case, self, suiteItem)
                step_result_list.append(step_result)

                if not step_result and step.FTC == 'N':
                    break

                if step.end_loop(test_case, step.test_result, self.index):
                    break

            self.suiteResult = all(step_result_list)
            self.print_result_info()
            self.process_mesVer(test_case)
            if test_case.jsonObj.test_phases is not None:
                self.copy_to_json_obj(suiteItem)
                test_case.jsonObj.test_phases.append(suiteItem)
            self.setColor(Qt.green if self.suiteResult else Qt.red)
            return self.suiteResult
        except Exception as e:
            self.setColor(Qt.darkRed)
            self.logger.fatal(f"run testSuite {self.name} Exception！！{e},{traceback.format_exc()}")
            self.suiteResult = False
            return self.suiteResult
        finally:
            self.clear()

    def process_mesVer(self, test_case):
        setattr(test_case.mesPhases, self.name + '_Time',
                self.elapsedTime.seconds + self.elapsedTime.microseconds / 1000000)
        if not self.suiteResult:
            setattr(test_case.mesPhases, self.name, str(self.suiteResult).upper())

    def setColor(self, color: QBrush):
        """set treeWidget item color"""
        try:
            if isinstance(self.myWind, ui.mainform.MainForm):
                self.myWind.mySignals.treeWidgetColor.emit(color, self.index, -1, False)
        except RuntimeError:
            pass

    def print_result_info(self):
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.elapsedTime = datetime.strptime(self.finish_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(
            self.start_time, '%Y-%m-%d %H:%M:%S.%f')
        if self.suiteResult:
            self.logger.info(f"{self.name} Test Pass!,ElapsedTime:{self.elapsedTime.seconds}")
        else:
            self.logger.error(f"{self.name} Test Fail!,ElapsedTime:{self.elapsedTime.seconds}")

    def daq_collect(self, test_case):
        self.logger.debug(f"collect DAQ data to {test_case.daqDataPath}")
        create_csv_file(self.logger, test_case.daqDataPath, test_case.ArrayListDaqHeader)
        data_list = [str(test_case.ForLoop.LoopCounter), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        data_list.extend(test_case.ArrayListDaq)
        write_csv_file(self.logger, test_case.daqDataPath, data_list)
        test_case.ArrayListDaq = []

    def copy_to_json_obj(self, obj: models.product.SuiteItem):
        obj.phase_name = self.name
        obj.status = "passed" if self.suiteResult else "failed"
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.error_code
        obj.phase_details = self.phase_details

    def clear(self):
        self.isTestFinished = False
        self.suiteResult = True
        self.start_time = ''
        self.finish_time = ''
        self.error_code = ''
        self.phase_details = ''
        self.elapsedTime = None
        self.suiteVar = ''


if __name__ == "__main__":
    pass
