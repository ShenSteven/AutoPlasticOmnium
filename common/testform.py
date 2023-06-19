#!/usr/bin/env python
# coding: utf-8
"""
@File   : testform.py
@Author : Steven.Shen
@Date   : 2/6/2023
@Desc   : 
"""
import sys
import threading
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import model.variables
import conf.globalvar as gv
from common.mysignals import MySignals


class TestForm(QMainWindow):

    def __init__(self, parent=None):
        super(TestForm, self).__init__(parent)
        self.logger = gv.lg.logger
        self.autoScanFlag = True
        self._lastSn = ''
        self.cap = None
        self.fileHandle = None
        self.timer = None
        self.sec = 1
        self.pause_event = threading.Event()
        self.startFlag = False
        self.IsCycle = False
        self.pauseFlag = False
        self.setIpFlag = False  # 是否设置dut IP为默认ip
        self.SingleStepTest = False
        self.finalTestResult = False
        self.SaveScriptDisableFlag = False
        self.TestVariables: model.variables.Variables = None
        self.SN = ''
        self.dut_model = ''
        self.shop_floor_url = ''
        self.WorkOrder = '1'
        self.DUTMesMac = ''
        self.DUTMesIP = ''
        self.txtLogPath = ''
        self.rs_url = ''
        self.mes_result = ''
        self.StepNo = -1
        self.SuiteNo = -1
        self.FailNumOfCycleTest = 0
        self.PassNumOfCycleTest = 0
        self.total_abort_count = 0
        self.total_fail_count = 0
        self.total_pass_count = 0
        self.continue_fail_count = 0
        self.my_signals = MySignals()

    def closeEvent(self, event):
        """
        重写QWidget类的closeEvent方法，在窗口被关闭的时候自动触发
        """
        super().closeEvent(event)  # 先添加父类的方法，以免导致覆盖父类方法（这是重点！！！）
        # self.autoScanFlag = False
        reply = QMessageBox.question(self, '提示', "是否要关闭程序?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)  # 退出程序
        else:
            event.ignore()
