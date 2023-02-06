#!/usr/bin/env python
# coding: utf-8
"""
@File   : testform.py
@Author : Steven.Shen
@Date   : 2/6/2023
@Desc   : 
"""
import threading
import model.variables
import conf.globalvar as gv
from model.mysignals import MySignals


class TestForm:

    def __init__(self):
        self.logger = gv.lg.logger
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
        self.dut_model = 'unknown'
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
