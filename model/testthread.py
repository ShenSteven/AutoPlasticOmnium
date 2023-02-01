# #!/usr/bin/env python
# # coding: utf-8
# """
# @File   : testthread.py
# @Author : Steven.Shen
# @Date   : 12/8/2022
# @Desc   :
# """
import time
import traceback
import conf.globalvar as gv
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from model.teststatus import TestStatus, SetTestStatus
from model.reporting import upload_Json_to_client, upload_result_to_mes, collect_data_to_csv, saveTestResult


class TestThread(QThread):
    signal = pyqtSignal(QWidget, TestStatus)

    def __init__(self, myWind: QWidget):
        super(TestThread, self).__init__()
        self.myWind = myWind
        self.signal[QWidget, TestStatus].connect(SetTestStatus)

    def __del__(self):
        self.wait()

    def run(self):
        """
        进行任务操作，主要的逻辑操作,返回结果
        """
        try:
            while True:
                if self.myWind.startFlag:
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
                        self.myWind.finalTestResult = result
                        self.signal[QWidget, TestStatus].emit(self.myWind,
                                                              TestStatus.PASS if self.myWind.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                    else:
                        result = self.myWind.testcase.run(gv.cf.station.fail_continue)
                        result1 = upload_Json_to_client(self.myWind.logger, self.myWind.rs_url, self.myWind.txtLogPath,
                                                        self.myWind.SN, self.myWind.testcase.jsonObj)
                        result2 = upload_result_to_mes(self.myWind.logger, self.myWind.mes_result,self.myWind.testcase.mesPhases)
                        self.myWind.finalTestResult = result & result1 & result2
                        collect_data_to_csv(self.myWind.testcase.mesPhases, self.myWind.WorkOrder, self.myWind.SN,
                                            self.myWind.logger)
                        saveTestResult(self.myWind.logger)
                        self.signal[QWidget, TestStatus].emit(self.myWind,
                                                              TestStatus.PASS if self.myWind.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                else:
                    continue
        except Exception as e:
            self.myWind.logger.fatal(f"TestThread() Exception:{e},{traceback.format_exc()}")
            self.signal[QWidget, TestStatus].emit(self.myWind, TestStatus.ABORT)
        finally:
            pass
            # gv.testThread.join(3)
            # lg.logger.debug('finally')
