#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from threading import Thread
import conf.globalvar as gv
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QCursor
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QMessageBox, QMenu
import model.variables
from conf.logprint import LogPrint
from common.basicfunc import IsNullOrEmpty
from common.mysignals import update_label
from common.testform import TestForm
from model.teststatus import TestStatus
from model.testthread import TestThread
from runin.ui_cell import Ui_cell
from time import strftime
from time import gmtime


class Cell(QFrame, Ui_cell, TestForm):

    def __init__(self, parent=None, row=-1, col=-1):
        Ui_cell.__init__(self)
        TestForm.__init__(self)
        self.WebPsIp = '192.168.10.'
        self.webSwitchCon = None
        self.row_index = row
        self.col_index = col
        self.testcase: model.testcase.TestCase = model.testcase.TestCase(rf'{gv.ExcelFilePath}',
                                                                         f'{gv.cfg.station.station_name}', self.logger,
                                                                         self, False)
        self.setupUi(self)
        self.init_cell_ui()
        self.init_signals_connect()
        self.testThread = TestThread(self)

    @property
    def LocalNo(self):
        if gv.cfg.RUNIN.col > 8:
            raise ValueError('out of! config.RUNIN.col must is 8 or less.')
        else:
            return (self.row_index - 1) * gv.cfg.RUNIN.col + self.col_index

    def init_cell_ui(self):
        self.lb_cellNum.setText('')
        self.lb_sn.setText('')
        self.lb_model.setText('')
        self.lb_testTime.setText('')
        self.lbl_failCount.setText('')
        self.lb_testName.setText(f'{self.row_index}-{self.col_index}')
        self.WebPsIp = '192.168.10.' + str(self.row_index)
        self.testcase.myWind = self
        self.lb_cellNum.setText(str(self.LocalNo))

    def init_signals_connect(self):
        """connect signals to slots"""
        self.mySignals.timingSignal[bool].connect(self.timing)
        self.mySignals.updateLabel[QLabel, str, int, QBrush].connect(update_label)
        self.mySignals.updateLabel[QLabel, str, int].connect(update_label)
        self.mySignals.updateLabel[QLabel, str].connect(update_label)
        self.mySignals.showMessageBox[str, str, int].connect(self.showMessageBox)
        self.mySignals.saveTextEditSignal[str].connect(self.on_actionSaveLog)
        self.lb_testName.linkActivated.connect(self.link_clicked)
        self.customContextMenuRequested.connect(self.on_menu)
        self.actionClearCell.triggered.connect(self.On_actionClearCell)
        self.actionRetest.triggered.connect(self.On_actionRetest)
        self.actionResetFailCount.triggered.connect(self.On_actionResetFailCount)
        self.actionSetDefaultIP.triggered.connect(self.On_actionSetDefaultIP)
        self.actionTelnetLogin.triggered.connect(self.On_actionTelnetLogin)

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

    def on_actionSaveLog(self, info):
        def thread_update():
            if info == 'rename':
                rename_log = self.txtLogPath.replace('logging',
                                                     str(self.finalTestResult).upper()).replace('details',
                                                                                                self.testcase.error_details_first_fail)
                self.logger.debug(f"rename test log to: {rename_log}")
                self.fileHandle.close()
                os.rename(self.txtLogPath, rename_log)
                self.txtLogPath = rename_log

        thread = Thread(target=thread_update, daemon=True)
        thread.start()

    def startTest(self):
        try:
            # if not self.checkContinueFailNum():
            #     return False
            self.test_initialize(self.lb_sn.text())
        except Exception as e:
            self.logger.fatal(f" step run Exception！！{e},{traceback.format_exc()}")
            return False
        else:
            return True

    def checkContinueFailNum(self):
        pass

    def test_initialize(self, SN):
        """测试变量初始化"""
        gv.InitCreateDirs(self.logger)
        self.init_variable(SN)
        self.testcase.jsonObj = model.product.JsonObject(SN, gv.cfg.station.station_no,
                                                         gv.cfg.dut.test_mode, gv.cfg.dut.qsdk_ver, gv.VERSION)
        self.testcase.daq_data_path = rf'{gv.OutPutPath}{os.sep}{gv.cfg.station.station_no}_{self.LocalNo}_DAQ_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
        self.testcase.mesPhases = model.product.MesInfo(SN, gv.cfg.station.station_no, gv.VERSION)
        self.testcase.startTimeJson = datetime.now()
        self.TestVariables = model.variables.Variables(SN, str(self.LocalNo), str(gv.cfg.LTT.row))
        self.txtLogPath = rf'{gv.LogFolderPath}{os.sep}logging_{self.LocalNo}_{self.SN}_details_{time.strftime("%H-%M-%S")}.txt'
        gv.lg = LogPrint(self.txtLogPath.replace('\\', '/'), gv.CriticalLog, gv.ErrorsLog)
        self.logger = gv.lg.logger
        self.testcase.logger = self.logger
        self.init_textEditHandler()
        if not self.testThread.isRunning():
            self.testThread = TestThread(self)
            self.testThread.start()
        self.testThread.signal[Cell, TestStatus].emit(self, TestStatus.START)

    def init_textEditHandler(self):
        """create log handler for textEdit"""
        log_console = logging.getLogger('testlog').handlers[0]
        if getattr(sys, 'frozen', False):
            logging.getLogger('testlog').removeHandler(log_console)
            self.fileHandle = gv.lg.logger.handlers[0]
        else:
            gv.cfg.station.privileges = 'lab'
            self.fileHandle = gv.lg.logger.handlers[1]

    def UpdateContinueFail(self, testResult: bool):
        if gv.IsDebug or gv.cfg.dut.test_mode.lower() == 'debug':
            return
        if testResult:
            self.continue_fail_count = 0
        else:
            self.continue_fail_count += 1

    # def timing(self, flag):
    #     if flag:
    #         self.logger.debug('start timing...')
    #         self.timer = self.startTimer(1000)
    #     else:
    #         self.logger.debug('stop timing...')
    #         self.killTimer(self.timer)

    def timerEvent(self, a):
        self.mySignals.updateLabel[QLabel, str].emit(self.lb_testTime, strftime("%H:%M:%S", gmtime(self.sec)))
        # QApplication.processEvents()
        self.sec += 1

    def link_clicked(self):
        def open_testlog():
            if os.path.exists(self.txtLogPath):
                os.startfile(self.txtLogPath)
            else:
                self.logger.warning(f"no find txt log,path:{self.txtLogPath}")

        thread = Thread(target=open_testlog, daemon=True)
        thread.start()

    def on_menu(self):
        menu = QMenu(self)
        menu.addAction(self.actionClearCell)
        menu.addAction(self.actionRetest)
        menu.addAction(self.actionResetFailCount)
        menu.addAction(self.actionSetDefaultIP)
        menu.addAction(self.actionTelnetLogin)
        menu.exec_(QCursor.pos())

    def On_actionClearCell(self):
        if not self.startFlag:
            self.lb_cellNum.setText('')
            self.lb_sn.setText('')
            self.lb_model.setText('')
            self.lb_testTime.setText('')
            self.lbl_failCount.setText('')
            self.lb_testName.setText(f'{self.row_index}-{self.col_index}')
            self.setStyleSheet("background-color: rgb(154, 142, 139);")

    def On_actionRetest(self):
        if IsNullOrEmpty(self.lb_sn.text()):
            return
        if self.startFlag:
            invoke_return = QMessageBox.warning(self, 'Retest?', 'Under testing,Are you sure retest?',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if invoke_return == QMessageBox.No:
                return
            self.testThread.signal[Cell, TestStatus].emit(self, TestStatus.ABORT)
            time.sleep(1)
        if not self.startTest():
            return
        gv.CheckSnList.append(self.SN)

    def On_actionResetFailCount(self):
        self.UpdateContinueFail(True)

    def On_actionSetDefaultIP(self):
        pass

    def On_actionTelnetLogin(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    mainWin = Cell()
    mainWin.show()
    app.exec_()
