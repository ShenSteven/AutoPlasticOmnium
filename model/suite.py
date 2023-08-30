#!/usr/bin/env python
# coding: utf-8
"""
@File   : suite.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
import traceback
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
import model.product
import model.step
from common.basicfunc import IsNullOrEmpty, create_csv_file, write_csv_file, str_to_int
import ui.mainform


def fail_continue(test_step: model.step.Step, failContinue):
    if test_step.FTC is None:
        return failContinue
    if test_step.FTC.lower() == 'n':
        return False
    elif test_step.FTC.lower() == 'y':
        return True
    else:
        return failContinue


class TestSuite:

    def __init__(self, suiteName=None, test_serial=None, dict_=None):
        self.myWind = None
        self.logger = None
        self.name = suiteName
        self._index = test_serial
        self.isTest = True
        self.suiteResult = True
        self.isTestFinished = False
        self.totalNumber = 0
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
            self._index = self.myWind.testcase.clone_suites.index(self)
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    def run(self, test_case, global_fail_continue, stepNo=-1):
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
            test_case.sum_step = test_case.sum_step - self.totalNumber
            self.myWind.my_signals.updateProgressBar[int, int].emit(test_case.step_finish_num, test_case.sum_step)
            self.setColor(Qt.gray)
            self.suiteResult = True
            return self.suiteResult
        self.logger.debug('- ' * 8 + f"<a name='testSuite:{self.name}'>Start testSuite:{self.name}</a>" + '- ' * 9)
        self.setColor(Qt.yellow)
        suiteItem = model.product.SuiteItem()
        step_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            for i, step in enumerate(self.steps, start=0):
                if i < stepNo:
                    continue
                self.start_loop(test_case, step)
                step.suiteVar = self.suiteVar
                step_result = step.run(test_case, self, suiteItem)
                step_result_list.append(step_result)

                if not step_result and not fail_continue(step, global_fail_continue):
                    break

                if self.end_loop(test_case, step):
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
                self.myWind.my_signals.treeWidgetColor.emit(color, self.index, -1, False)
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

    def start_loop(self, test_case, step: model.step.Step):
        """FOR 循环开始判断 FOR(3)"""
        if IsNullOrEmpty(step.For):
            return
        if str_to_int(step.For)[0]:
            test_case.ForLoop.start(int(step.For), self.index, step.index)
        elif step.For.lower() == "do":
            pass
        elif step.For.lower() == "while":
            pass

    def end_loop(self, test_case, step: model.step.Step):
        """FOR 循环结束判断 END FOR"""
        if IsNullOrEmpty(step.For):
            return False
        if step.For.lower().startswith('end'):
            # self.daq_collect(test_case)
            is_end = not test_case.ForLoop.is_end()
            return is_end
        elif step.For.lower() == "do":
            return False
        elif step.For.lower() == "while":
            return False

    def daq_collect(self, test_case):
        self.logger.debug(f"collect DAQ data to {test_case.daq_data_path}")
        create_csv_file(self.logger, test_case.daq_data_path, test_case.ArrayListDaqHeader)
        data_list = [str(test_case.ForLoop.ForCycleCounter), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        data_list.extend(test_case.ArrayListDaq)
        write_csv_file(self.logger, test_case.daq_data_path, data_list)
        test_case.ArrayListDaq = []

    def copy_to_json_obj(self, obj: model.product.SuiteItem):
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
