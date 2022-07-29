#!/usr/bin/env python
# coding: utf-8
"""
@File   : suite.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush

import model.product
import model.step
from .basicfunc import IsNullOrEmpty
import conf.globalvar as gv
import conf.logprint as lg
import ui.mainform


def fail_continue(test_step: model.step.Step, failContinue):
    if test_step.FTC.lower() == 'n':
        return False
    elif test_step.FTC.lower() == 'y':
        return True
    else:
        return failContinue


class TestSuite:

    def __init__(self, suiteName=None, test_serial=None, dict_=None):
        self.SuiteName = suiteName
        self.index = test_serial
        self.isTest = True
        self.suiteResult = True
        self.isTestFinished = False
        self.totalNumber = 0
        self.suiteVar = ''
        self.steps = []
        self.start_time = ""
        self.finish_time = ""
        self.error_code = None
        self.phase_details = None
        self.elapsedTime = None
        self.ForStartStepNo = 0
        self.ForTotalCycle = 0
        self.ForCycleCounter = 1
        if dict_ is not None:
            self.__dict__.update(dict_)

    def run(self, test_case, global_fail_continue, stepNo=-1):
        """
        run test suite.
        :param test_case:
        :param global_fail_continue: a boolean indicate step or continue when test fail.
        :param stepNo:
        :return:test result,pass or fail.
        """
        if not self.isTest:
            self.setColor(Qt.gray)
            self.suiteResult = True
            return self.suiteResult
        lg.logger.debug(
            '- ' * 8 + f"<a name='testSuite:{self.SuiteName}'>Start testSuite:{self.SuiteName}</a>" + '- ' * 9)
        self.setColor(Qt.yellow)
        suiteItem = model.product.SuiteItem()
        step_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            for i, step_item in enumerate(self.steps, start=0):
                if stepNo != -1:
                    i = stepNo
                    stepNo = -1

                self.process_for(test_case, self.steps[i])
                # 把测试套的全局变量赋值给下面的测试步骤
                # if not IsNullOrEmpty(self.suiteVar):
                step_item.suiteVar = self.suiteVar
                step_result = self.steps[i].run(self, suiteItem)
                step_result_list.append(step_result)

                if not step_result and not fail_continue(self.steps[i], global_fail_continue):
                    break

                if self.process_EndFor(test_case, self.steps[i]):
                    break

            self.suiteResult = all(step_result_list)
            self.print_result_info()
            self.process_mesVer()
            # 加入station实例,记录测试结果 用于序列化Json文件
            if gv.stationObj.test_phases is not None:
                self.copy_to_json_obj(suiteItem)
                gv.stationObj.test_phases.append(suiteItem)
            self.setColor(Qt.green if self.suiteResult else Qt.red)
            return self.suiteResult
        except Exception as e:
            self.setColor(Qt.darkRed)
            lg.logger.exception(f"run testSuite {self.SuiteName} Exception！！{e}")
            self.suiteResult = False
            return self.suiteResult
        finally:
            self.clear()

    def process_mesVer(self):
        setattr(gv.mesPhases, self.SuiteName + '_Time',
                self.elapsedTime.seconds + self.elapsedTime.microseconds / 1000000)
        if not self.suiteResult:
            setattr(gv.mesPhases, self.SuiteName, str(self.suiteResult).upper())

    def setColor(self, color: QBrush):
        """set treeWidget item color"""
        ui.mainform.MainForm.main_form.my_signals.treeWidgetColor.emit(color, self.index, -1, False)
        # QMetaObject.invokeMethod(robotsystem.ui.mainform.MainForm.main_form, 'update_treeWidget_color',
        #                          Qt.BlockingQueuedConnection,
        #                          Q_ARG(QBrush, color),
        #                          Q_ARG(int, self.index),
        #                          Q_ARG(int, -1),
        #                          Q_ARG(bool, False))

    def print_result_info(self):
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.elapsedTime = datetime.strptime(self.finish_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(
            self.start_time, '%Y-%m-%d %H:%M:%S.%f')
        if self.suiteResult:
            lg.logger.info(f"{self.SuiteName} Test Pass!,ElapsedTime:{self.elapsedTime}")
        else:
            lg.logger.error(f"{self.SuiteName} Test Fail!,ElapsedTime:{self.elapsedTime}")

    def process_for(self, test_case, step_item: model.step.Step):
        """FOR 循环开始判断"""
        if not IsNullOrEmpty(step_item.For) and '(' in step_item.For and ')' in step_item.For:
            self.ForTotalCycle = int(re.findall(r'\((.*?)\)', step_item.For)[0])
            test_case.ForStartSuiteNo = self.index
            self.ForStartStepNo = step_item.index
            test_case.ForFlag = False
            lg.logger.debug(f"====================Start Cycle-{self.ForCycleCounter}===========================")

    def process_EndFor(self, test_case, step_item: model.step.Step):
        """FOR 循环结束判断"""
        if not IsNullOrEmpty(step_item.For) and step_item.For.lower().startswith('end'):
            if self.ForCycleCounter < self.ForTotalCycle:
                test_case.ForFlag = True
                self.ForCycleCounter += 1
                return True

            test_case.ForFlag = False
            lg.logger.debug('=' * 10 + f"Have Complete all({self.ForCycleCounter}) Cycle test." + '=' * 10)
            self.ForCycleCounter = 1
            return False
        else:
            return False

    def copy_to_json_obj(self, obj: model.product.SuiteItem):
        obj.phase_name = self.SuiteName
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
