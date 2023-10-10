# #!/usr/bin/env python
# # coding: utf-8
# """
# @File   : testthread.py
# @Author : Steven.Shen
# @Date   : 12/8/2022
# @Desc   :
# """
import traceback
import conf.globalvar as gv
from PyQt5.QtWidgets import QWidget, QFrame, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from bll.teststatus import TestStatus, SetTestStatus
from bll.datastore import upload_Json_to_client, upload_result_to_mes, collect_data_to_csv


class TestThread(QThread):
    signal = pyqtSignal((QMainWindow, TestStatus), (QWidget, TestStatus), (QFrame, TestStatus))

    def __init__(self, myWind: QWidget):
        super(TestThread, self).__init__()
        self.myWind = myWind
        self.signal[QMainWindow, TestStatus].connect(SetTestStatus)
        self.signal[QWidget, TestStatus].connect(SetTestStatus)
        self.signal[QFrame, TestStatus].connect(SetTestStatus)

    def __del__(self):
        self.wait()

    def run(self):
        """
        进行任务操作，主要的逻辑操作,返回结果
        """
        try:
            while True:
                if self.myWind.startFlag:
                    if self.myWind.IsCycle:
                        while self.myWind.IsCycle:
                            if self.myWind.testcase.run():
                                self.myWind.PassNumOfCycleTest += 1
                            else:
                                self.myWind.FailNumOfCycleTest += 1
                            if self.myWind.PassNumOfCycleTest + self.myWind.FailNumOfCycleTest == gv.cfg.station.LoopMaximum \
                                    or self.myWind.PassNumOfCycleTest == gv.cfg.station.LoopNumPassed:
                                self.myWind.logger.debug(
                                    f"***** All loop({gv.cfg.station.loop_count}) have completed! *****")
                                self.myWind.mySignals.threadStopSignal[str].emit('stop loop test.')
                                QThread.msleep(500)
                            else:
                                QThread.sleep(gv.cfg.station.LoopInterval)
                    elif self.myWind.SingleStepTest:
                        self.myWind.logger.debug(
                            f'Run single-step,SuiteNo:{self.myWind.SuiteNo},StepNo:{self.myWind.StepNo}')
                        result = self.myWind.testcase.cloneSuites[self.myWind.SuiteNo].steps[self.myWind.StepNo].run(
                            self.myWind.testcase, self.myWind.testcase.cloneSuites[self.myWind.SuiteNo])
                        self.myWind.finalTestResult = result
                        self.signal[QWidget, TestStatus].emit(self.myWind,
                                                              TestStatus.PASS if self.myWind.finalTestResult else TestStatus.FAIL)
                        QThread.msleep(500)
                    else:
                        result = self.myWind.testcase.run()
                        result1 = upload_Json_to_client(self.myWind.logger, self.myWind.rs_url, self.myWind.txtLogPath,
                                                        self.myWind.SN, self.myWind.testcase.jsonObj)
                        result2 = upload_result_to_mes(self.myWind.logger, self.myWind.mesUrl,
                                                       self.myWind.testcase.mesPhases)
                        self.myWind.finalTestResult = result & result1 & result2
                        collect_data_to_csv(self.myWind.testcase.mesPhases, self.myWind.testcase.csvListHeader,
                                            self.myWind.testcase.csvListData, self.myWind)
                        if gv.MainWin is not None:
                            self.myWind.saveTestResult()
                        self.signal[QWidget, TestStatus].emit(self.myWind,
                                                              TestStatus.PASS if self.myWind.finalTestResult else TestStatus.FAIL)
                        QThread.msleep(500)
                else:
                    QThread.msleep(1)
        except Exception as e:
            self.myWind.logger.fatal(f"TestThread() Exception:{e},{traceback.format_exc()}")
            self.signal[QWidget, TestStatus].emit(self.myWind, TestStatus.ABORT)
        finally:
            pass

