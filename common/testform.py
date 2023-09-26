#!/usr/bin/env python
# coding: utf-8
"""
@File   : testform.py
@Author : Steven.Shen
@Date   : 2/6/2023
@Desc   : 
"""
import os
import sys
import threading
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QStyleFactory
import models.variables
import conf.globalvar as gv
from common.mysignals import MySignals


class TestForm(QMainWindow):

    def __init__(self, parent=None):
        super(TestForm, self).__init__(parent)
        self.logger = gv.lg.logger
        self.fileHandle = None
        self.timerID = None
        self.sec = 1
        self.pause_event = threading.Event()
        self.startFlag = False
        self.IsCycle = False
        self.pauseFlag = False
        self.SingleStepTest = False
        self.finalTestResult = False
        self.SaveScriptDisableFlag = False
        self.TestVariables: models.variables.Variables = None
        self.StepNo = -1
        self.SuiteNo = -1
        self.FailNumOfCycleTest = 0
        self.PassNumOfCycleTest = 0
        self.total_abort_count = 0
        self.total_fail_count = 0
        self.total_pass_count = 0
        self.continue_fail_count = 0
        self.autoScanFlag = True
        self._lastSn = ''
        self.cap = None

        self.testcase = None
        self.SN = ''
        self.txtLogPath = ''
        self.dut_model = ''
        self.shop_floor_url = ''
        self.mes_result = ''
        self.rs_url = ''
        self.WorkOrder = '1'
        self.DUTMesIP = ''
        self.DUTMesMac = ''
        self.setIpFlag = False  # 是否设置dut IP为默认ip
        self.mySignals = MySignals()
        QApplication.setStyle(QStyleFactory.create("fusion"))
        # QApplication.setStyle(QStyleFactory.create("macintosh"))

    def init_variable(self, sn):
        self.sec = 1
        self.SN = sn
        self.txtLogPath = rf'{gv.LogFolderPath}{os.sep}logging_{self.SN}_details_{time.strftime("%H-%M-%S")}.txt'
        self.shop_floor_url = f'http://{gv.cfg.station.mes_shop_floor}/api/CHKRoute/serial/{self.SN}/station/{gv.cfg.station.station_name}'
        self.mes_result = f'http://{gv.cfg.station.mes_result}/api/2/serial/{self.SN}/station/{gv.cfg.station.station_no}/info'
        self.rs_url = gv.cfg.station.rs_url
        self.WorkOrder = '1'
        self.DUTMesIP = ''
        self.DUTMesMac = ''
        self.setIpFlag = False
        self.finalTestResult = False
        if self.SingleStepTest and self.testcase.Finished:
            pass
        else:
            self.TestVariables = models.variables.Variables(self.SN, gv.cfg.LTT.channel)
        if not self.SingleStepTest:
            self.SuiteNo = -1
            self.StepNo = -1

    def timing(self, flag):
        if flag:
            self.logger.debug('start timing...')
            self.timerID = self.startTimer(1000, timerType=Qt.VeryCoarseTimer)
        else:
            self.logger.debug('stop timing...')
            self.killTimer(self.timerID)

    def closeEvent(self, event):
        """
        重写QWidget类的closeEvent方法，在窗口被关闭的时候自动触发
        """
        if not getattr(sys, 'frozen', False):
            return
        super().closeEvent(event)  # 先添加父类的方法，以免导致覆盖父类方法（这是重点！！！）
        # self.autoScanFlag = False
        reply = QMessageBox.question(self, '提示', "是否要关闭程序?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)  # 退出程序
        else:
            event.ignore()
