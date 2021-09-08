#!/usr/bin/env python
# coding: utf-8
"""
@File   : suite.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
from datetime import datetime

from bin.basefunc import IsNullOrEmpty
from bin.globalconf import logger
from model.product import test_phases
from bin import globalvar as gv


class TestSuite:
    SeqName = ""
    isTest = True  # 是否测试
    isTestFinished = False  # 测试完成标志
    testResult = True  # 测试结果
    totalNumber = 0  # 测试大项item总数量
    index = 0  # 测试大项在所有中的序列号
    test_version = ""  # 测试程序版本
    system_name = None  # 测试系统名称 SystemName
    test_steps = []
    start_time = ""
    finish_time = ""
    error_code = None
    phase_details = None
    elapsedTime = None

    def __init__(self, SeqName, test_serial):
        self.SeqName = SeqName
        self.index = test_serial
        self.test_steps = []

    def clear(self):
        self.isTestFinished = False
        self.testResult = True
        self.start_time = ""
        self.finish_time = ""
        self.error_code = None
        self.phase_details = None
        self.elapsedTime = None

    def copy_to(self, obj: test_phases):
        obj.phase_name = self.SeqName
        obj.status = "passed" if self.testResult else "failed"
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.error_code
        obj.phase_details = self.phase_details

    def _process_mesVer(self):
        if self.isTest:
            setattr(gv.mesPhases, self.SeqName + '_Time',
                    self.elapsedTime.seconds + self.elapsedTime.microseconds / 1000000)
            if not self.testResult:
                setattr(gv.mesPhases, self.SeqName, str(self.testResult).upper())

    def run_suite(self, global_fail_continue, stepNo=None):
        global step_result
        step_result = False
        testPhase = test_phases()
        step_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            for step in self.test_steps:
                if stepNo is not None and step.index == stepNo:
                    step_result = step.run_step(testPhase)
                    step_result_list.append(step_result)
                    break
                if stepNo is None:
                    step_result = step.run_step(testPhase)
                step_result_list.append(step_result)
                if not step_result and not (global_fail_continue or step.get_fail_continue()):
                    self.testResult = False
                    break
                else:
                    pass
            self.testResult = all(step_result_list)
            self.print_result()
            self._process_mesVer()
            self.copy_to(testPhase)  # 把seq测试结果保存到test_phase变量中.
            gv.station.test_phases.append(testPhase)  # 加入station实例,记录测试结果 用于序列化Json文件
        except Exception as e:
            logger.exception(f"run testSuite {self.SeqName} Exception！！{e}")
            self.testResult = False
            return self.testResult
        else:
            return self.testResult
        finally:
            self.clear()

    def print_result(self):
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.elapsedTime = datetime.strptime(self.finish_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(
            self.start_time, '%Y-%m-%d %H:%M:%S.%f')
        if self.testResult:
            logger.info(f"{self.SeqName} Test Pass!,ElapsedTime:{self.elapsedTime}")
        else:
            logger.error(f"{self.SeqName} Test Fail!,ElapsedTime:{self.elapsedTime}")
