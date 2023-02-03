#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import time
import traceback
from datetime import datetime
import conf.globalvar as gv
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QMessageBox
import model.variables
from conf.logprint import LogPrint
from model.mysignals import MySignals, update_label
from model.teststatus import TestStatus
from model.testthread import TestThread
from runin.ui_cell import Ui_cell


class Cell(QFrame, Ui_cell):

    def __init__(self, parent=None, row=-1, col=-1, testcase=None):
        QFrame.__init__(self, parent)
        Ui_cell.__init__(self)
        self.shop_floor_url = ''
        self.TestVariables: model.variables.Variables = None
        self.WorkOrder = '1'
        self.DUTMesMac = ''
        self.DUTMesIP = ''
        self.setIpFlag = False  # 是否设置dut IP为默认ip
        self.dut_model = 'unknown'
        self.SN = ''
        self.finalTestResult = False
        self.startFlag = False
        self.txtLogPath = ''
        self.rs_url = ''
        self.mes_result = ''
        self.fileHandle = None
        self.SaveScriptDisableFlag = False
        self.SingleStepTest = False
        self.StepNo = -1
        self.SuiteNo = -1
        self.FailNumOfCycleTest = 0
        self.PassNumOfCycleTest = 0
        self.total_abort_count = 0
        self.total_fail_count = 0
        self.total_pass_count = 0
        self.continue_fail_count = 0
        self.my_signals = MySignals()
        self.timer = None
        self.sec = 1
        self.WebPsIp = 'null'
        self.LocalNo = -100
        self.row_index = row
        self.col_index = col
        self.testcase = testcase
        self.sequences = []
        self.CellLogTxt = ''
        self.logger = None
        self.setupUi(self)
        self.init_cell_ui()
        self.init_signals_connect()
        self.testThread = TestThread(self)

    def init_cell_ui(self):
        self.lb_cellNum.setText('')
        self.lb_sn.setText('')
        self.lb_model.setText('')
        self.lb_testTime.setText('')
        self.lbl_failCount.setText('')
        self.lb_testName.setText(f'{self.row_index}-{self.col_index}')
        self.testcase.myWind = self

    def init_signals_connect(self):
        """connect signals to slots"""
        self.my_signals.timingSignal[bool].connect(self.timing)
        self.my_signals.updateLabel[QLabel, str, int, QBrush].connect(update_label)
        self.my_signals.updateLabel[QLabel, str, int].connect(update_label)
        self.my_signals.updateLabel[QLabel, str].connect(update_label)
        self.my_signals.showMessageBox[str, str, int].connect(self.showMessageBox)

    @QtCore.pyqtSlot(str, str, int, result=QMessageBox.StandardButton)
    def showMessageBox(self, title, text, level=2):
        if level == 0:
            return QMessageBox.information(self, title, text, QMessageBox.Yes)
        elif level == 1:
            return QMessageBox.warning(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        elif level == 2:
            aa = QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return aa
        elif level == 3:
            return QMessageBox.about(self, title, text)
        else:
            return QMessageBox.critical(self, title, text, QMessageBox.Yes)

    def startTest(self):
        try:
            # if not self.checkContinueFailNum():
            #     return False
            self.SN = ''
            self.SN = self.lb_sn.text().strip()
            self.variable_init(self.SN)
        except Exception as e:
            self.logger.fatal(f" step run Exception！！{e},{traceback.format_exc()}")
            return False

    def checkContinueFailNum(self):
        pass

    def variable_init(self, SN):
        """测试变量初始化"""
        self.TestVariables = model.variables.Variables(gv.cf.station.station_name,
                                                       gv.cf.station.station_no, SN, gv.cf.dut.dut_ip,
                                                       gv.cf.station.log_folder)
        self.testcase.jsonObj = model.product.JsonObject(SN, gv.cf.station.station_no,
                                                         gv.cf.dut.test_mode, gv.cf.dut.qsdk_ver, gv.version)
        self.mes_result = f'http://{gv.cf.station.mes_result}/api/2/serial/{SN}/station/{gv.cf.station.station_no}/info'
        self.rs_url = gv.cf.station.rs_url
        self.shop_floor_url = f'http://{gv.cf.station.mes_shop_floor}/api/CHKRoute/serial/{SN}/station/{gv.cf.station.station_name}'
        self.testcase.mesPhases = model.product.MesInfo(SN, gv.cf.station.station_no, gv.version)
        self.init_create_dirs()
        self.finalTestResult = False
        self.setIpFlag = False
        self.DUTMesIP = ''
        self.DUTMesMac = ''
        if not self.SingleStepTest:
            self.SuiteNo = -1
            self.StepNo = -1
        self.WorkOrder = '1'
        self.testcase.startTimeJson = datetime.now()
        self.sec = 1
        self.txtLogPath = rf'{gv.logFolderPath}\logging_{self.SN}_details_{time.strftime("%H-%M-%S")}.txt'
        gv.lg = LogPrint(self.txtLogPath.replace('\\', '/'), gv.critical_log, gv.errors_log)
        self.logger = gv.lg.logger
        self.testcase.logger = self.logger
        if not self.testThread.isRunning():
            self.testThread = TestThread(self)
            self.testThread.start()
        self.testThread.signal2[Cell, TestStatus].emit(self, TestStatus.START)

    def timing(self, flag):
        if flag:
            self.logger.debug('start timing...')
            self.timer = self.startTimer(1000)
        else:
            self.logger.debug('stop timing...')
            self.killTimer(self.timer)

    def timerEvent(self, a):
        self.my_signals.updateLabel[QLabel, str, int].emit(self.lb_testTime, str(self.sec), 20)
        # QApplication.processEvents()
        self.sec += 1

    def init_create_dirs(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    mainWin = Cell()
    mainWin.show()
    app.exec_()
