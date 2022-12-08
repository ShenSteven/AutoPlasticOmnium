#!/usr/bin/env python
# coding: utf-8
"""
@File   : testthread.py
@Author : Steven.Shen
@Date   : 12/8/2022
@Desc   : 
"""
import time
import traceback

from PyQt5.QtCore import QThread, pyqtSignal
import conf.globalvar as gv
from model.reporting import upload_Json_to_client, upload_result_to_mes, collect_data_to_csv, saveTestResult
from model.teststatus import SetTestStatus, TestStatus
from ui.mainform import MainForm


class TestThread(QThread):
    signal = pyqtSignal(MainForm, TestStatus)

    def __init__(self, myWind: MainForm):
        super(TestThread, self).__init__()
        self.myWind = myWind
        self.signal[MainForm, TestStatus].connect(SetTestStatus)

    def __del__(self):
        self.wait()

    def run(self):
        """
        进行任务操作，主要的逻辑操作,返回结果
        """
        try:
            while True:
                if gv.startFlag:
                    if gv.IsCycle:
                        while gv.IsCycle:
                            if self.myWind.testcase.run(gv.cf.station.fail_continue):
                                self.myWind.PassNumOfCycleTest += 1
                            else:
                                self.myWind.FailNumOfCycleTest += 1
                            if self.myWind.PassNumOfCycleTest + self.myWind.FailNumOfCycleTest == gv.cf.station.loop_count:
                                self.myWind.logger.debug(
                                    f"***** All loop({gv.cf.station.loop_count}) have completed! *****")
                                self.myWind.my_signals.threadStopSignal[str].emit('stop test.')
                                time.sleep(0.5)
                            else:
                                time.sleep(gv.cf.station.loop_interval)
                    elif self.myWind.SingleStepTest:
                        self.myWind.logger.debug(f'Suite:{self.myWind.SuiteNo},Step:{self.myWind.StepNo}')
                        result = self.myWind.testcase.clone_suites[self.myWind.SuiteNo].steps[
                            self.myWind.StepNo].run(
                            self.myWind.testcase.clone_suites[self.myWind.SuiteNo])
                        gv.finalTestResult = result
                        self.signal[MainForm, TestStatus].emit(self.myWind,
                                                               TestStatus.PASS if gv.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                    else:
                        result = self.myWind.testcase.run(gv.cf.station.fail_continue)
                        result1 = upload_Json_to_client(self.myWind.logger, gv.cf.station.rs_url, gv.txtLogPath)
                        result2 = upload_result_to_mes(self.myWind.logger, gv.mes_result)
                        gv.finalTestResult = result & result1 & result2
                        collect_data_to_csv(self.myWind.logger)
                        saveTestResult(self.myWind.logger)
                        self.signal[MainForm, TestStatus].emit(self.myWind,
                                                               TestStatus.PASS if gv.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                else:
                    continue
        except Exception as e:
            self.myWind.logger.fatal(f"TestThread() Exception:{e},{traceback.format_exc()}")
            self.signal[MainForm, TestStatus].emit(self.myWind, TestStatus.ABORT)
        finally:
            pass
            # gv.testThread.join(3)
            # lg.logger.debug('finally')