#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
from datetime import datetime
from os.path import join
from threading import Thread, Event
import robotsystem.conf.config
import platform
import robotsystem.model.product
import robotsystem.model.testglobalvar
import robotsystem

win = platform.system() == 'Windows'
linux = platform.system() == 'Linux'
current_dir = robotsystem.current_dir
config_yaml_path = join(current_dir, 'conf', 'config.yaml')
logging_yaml = join(current_dir, 'conf', 'logging.yaml')
cf = robotsystem.conf.config.read_config(config_yaml_path, robotsystem.conf.config.Configs)  # load test global variable
tableWidgetHeader = ["SN", "ItemName", "Spec", "LSL", "Value", "USL", "Time", "StartTime", "Result"]

SN = ''
dut_ip = ''
DUTMesIP = ''
MesMac = 'FF:FF:FF:FF:FF'
WorkOrder = '1'
dut_model = 'unknown'

error_code_first_fail = ''
error_details_first_fail = ''
version = robotsystem.about['__version__']

logFolderPath = ''
critical_log = ''
errors_log = ''
txtLogPath = ''
jsonOfResult = ''
csv_list_header = []
csv_list_result = []
ArrayListDaq = []

dut_comm = None
FixSerialPort: None
PLin: None

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

OutPutPath = rf'{current_dir}\OutPut'
DataPath = rf'{current_dir}\Data'
scriptFolder = rf'{current_dir}\scripts'
excel_file_path = rf'{scriptFolder}\{cf.station.testcase}'
test_script_json = rf'{scriptFolder}\{cf.station.station_name}.json'
CSVFilePath = ''
mes_shop_floor = ''
mes_result = ''
shop_floor_url = ''
database_setting = rf'{current_dir}\conf\setting.db'
database_result = rf'{current_dir}\OutPut\result.db'

continue_fail_count = 0
total_pass_count = 0
total_fail_count = 0
total_abort_count = 0

mesPhases: robotsystem.model.product.MesInfo
stationObj: robotsystem.model.product.JsonObject
testThread: Thread
pause_event = Event()

PassNumOfCycleTest = 0
FailNumOfCycleTest = 0
SuiteNo = -1
StepNo = -1
startTimeJsonFlag = True
startTimeJson = datetime.now()

testGlobalVar: robotsystem.model.testglobalvar.TestGlobalVar


def set_global_val(name, value):
    globals()[name] = value


def get_global_val(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue


if __name__ == '__main__':
    pass
