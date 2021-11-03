#!/usr/c/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
from conf.globalconf import *
from model.product import JsonResult, MesInfo
from sokets.serialport import SerialPort

# try:
#     fix_serial = SerialPort('COM3', 1115200)
#     dut_serial = SerialPort('COM9', 1115200)
# except Exception as e:
#     logger.exception(e)
#     sys.exit()

sn = 'G1234568799NSS'
SN = sn
dut_ip = ''
DUTMesIP = ''
MesMac = "FF:FF:FF:FF:FF"
WorkOrder = "1"
dut_mode = 'firefly'
error_code_first_fail = ""
error_details_first_fail = ""
test_software_ver = c.station.test_software_version
isDebug = False
logFolderPath = ""
jsonOfResult = ""
txtLogPath = ""
csv_list_header = []
csv_list_result = []
dut_comm = None
inPutValue = ""  # suite内的全局变量
startFlag = False

ForTotalCycle = 0
ForTestCycle = 1
ForStartSuiteNo = 0
ForStartStepNo = 0
ForFlag = False

scriptFolder = f"{above_current_path}\scripts\\"
testcasePath = f"{scriptFolder}{c.station.testcase}"
testcaseJsonPath = f"{scriptFolder}{c.station.station_name}.json"
SHA256Path = f"{scriptFolder}{c.station.station_name}_key.txt"
print(SHA256Path)

mes_shop_floor = f"http://{c.station.mes_shop_floor}/api/TEST/serial/{sn}/station/{c.station.station_no}/info"
mes_result = f"http://{c.station.mes_result}/api/TEST/serial/{sn}/station/{c.station.station_no}/info"
mesPhases = MesInfo(sn, c.station.station_no, c.station.test_software_version)
test_mode = c.dut.test_mode
stationObj = JsonResult(sn, c.station.station_no, test_mode, c.dut.qsdk_ver, c.station.test_software_version)


def set_globalVal(name, value):
    globals()[name] = value


def get_globalVal(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue
