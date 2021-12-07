#!/usr/cf/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
import os
from datetime import datetime
from os.path import dirname, abspath, join
from threading import Thread
import conf
import model.product

current_path = dirname(abspath(__file__))
above_current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
cf = conf.read_config(join(current_path, 'config.yaml'), conf.config.Configs)  # load test global variable
tableWidgetHeader = ["SN", "ItemName", "Spec", "LSL", "tValue", "USL", "ElapsedTime", "StartTime", "Result"]
SN = ''
dut_ip = ''
DUTMesIP = ''
MesMac = 'FF:FF:FF:FF:FF'
WorkOrder = '1'
dut_mode = 'unknown'
error_code_first_fail = ''
error_details_first_fail = ''
test_software_ver = cf.station.test_software_version

logFolderPath = ''
critical_log = ''
errors_log = ''
txtLogPath = ''
jsonOfResult = ''
csv_list_header = []
csv_list_result = []

dut_comm = None
FixSerialPort: None

IsDebug = False
startFlag = False
pauseFlag = False
IsCycle = False
finalTestResult = False
setIpFlag = False
SingleStepTest = False
IfCond = True
failCount = 0

ForTotalCycle = 0
ForTestCycle = 1
ForStartSuiteNo = 0
ForStartStepNo = 0
ForFlag = False

OutPutPath = rf'{above_current_path}\OutPut'
DataPath = rf'{above_current_path}\Data'
scriptFolder = f'{above_current_path}\scripts\\'
excel_file_path = f'{scriptFolder}{cf.station.testcase}'
test_script_json = f'{scriptFolder}{cf.station.station_name}.json'
SHA256Path = f'{scriptFolder}{cf.station.station_name}_key.txt'
CSVFilePath = ''
mes_shop_floor = ''
mes_result = ''
shop_floor_url = ''

mesPhases: model.product.MesInfo
stationObj: model.product.JsonResult
testThread: Thread

PassNumOfCycleTest = 0
FailNumOfCycleTest = 0
SuiteNo = -1
StepNo = -1
startTimeJsonFlag = True
startTimeJson = datetime.now()


def set_globalVal(name, value):
    globals()[name] = value


def get_globalVal(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue


if __name__ == '__main__':
    pass
