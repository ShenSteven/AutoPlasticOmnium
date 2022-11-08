#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
from datetime import datetime
from os.path import join, abspath, dirname
from threading import Event
import conf.config
import platform
import model.product
import model.variables
from main import bundle_dir


def get_about():
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), '__version__.py'), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


about = get_about()

win = platform.system() == 'Windows'
linux = platform.system() == 'Linux'
tableWidgetHeader = ["SN", "ItemName", "Spec", "LSL", "Value", "USL", "Time", "StartTime", "Result"]

current_dir = bundle_dir
config_yaml_path = abspath(join(dirname(__file__), 'config.yaml'))
cf = conf.config.read_config(config_yaml_path, conf.config.Configs)

SN = ''
dut_ip = ''
DUTMesIP = ''
MesMac = 'FF:FF:FF:FF:FF'
WorkOrder = '1'
dut_model = 'unknown'

error_code_first_fail = ''
error_details_first_fail = ''
version = about['__version__']

logFolderPath = ''
# critical_log = ''
# errors_log = ''
txtLogPath = ''
jsonOfResult = ''
csv_list_header = []
csv_list_data = []
ArrayListDaq = []
ArrayListDaqHeader = ['SN', 'DateTime']
daq_data_path = ''

dut_comm = None
FixSerialPort = None
PLin = None
InstrComm = None


IsDebug = False
startFlag = False
pauseFlag = False
pause_event = Event()
IsCycle = False
finalTestResult = False
setIpFlag = False
# SingleStepTest = False
IfCond = True
failCount = 0

ForTotalCycle = 0
ForCycleCounter = 1
# ForStartSuiteNo = 0
ForStartStepNo = 0
# ForFlag = False

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

# continue_fail_count = 0
# total_pass_count = 0
# total_fail_count = 0
# total_abort_count = 0

TestVariables: model.variables.Variables = None
mesPhases: model.product.MesInfo
stationObj: model.product.JsonObject
# testThread = None
stepThread1 = None
stepThread2 =None
IsRunning1 = False
IsRunning2 = False
pMsg32 = None
pMsg33 = None

# PassNumOfCycleTest = 0
# FailNumOfCycleTest = 0
# SuiteNo = -1
# StepNo = -1
startTimeJsonFlag = True
startTimeJson = datetime.now()


def set_global_val(name, value):
    globals()[name] = value


def get_global_val(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue


if __name__ == '__main__':
    pass
