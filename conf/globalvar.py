#!/usr/cf/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
import os
from os.path import dirname, abspath, join
from cryptography.fernet import Fernet
import conf
import model.product

current_path = dirname(abspath(__file__))
above_current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(current_path)
# # load test global variable
cf = conf.read_config(join(current_path, 'config.yaml'), conf.config.Configs)

key = Fernet.generate_key()
token = Fernet(key)

sn = 'G1234568799NSS'
SN = sn
dut_ip = ''
DUTMesIP = ''
MesMac = "FF:FF:FF:FF:FF"
WorkOrder = "1"
dut_mode = 'firefly'
error_code_first_fail = ""
error_details_first_fail = ""
test_software_ver = cf.station.test_software_version
IsDebug = False
logFolderPath = ""
jsonOfResult = ""
txtLogPath = ""
csv_list_header = []
csv_list_result = []
dut_comm = None
inPutValue = ""  # suite内的全局变量
StartFlag = False
IsCycle = False
finalTestResult = False
setIpFlag = False
SingleStepTest = False

ForTotalCycle = 0
ForTestCycle = 1
ForStartSuiteNo = 0
ForStartStepNo = 0
ForFlag = False

scriptFolder = f"{above_current_path}\scripts\\"
excel_file_path = f"{scriptFolder}{cf.station.testcase}"
test_script_json = f"{scriptFolder}{cf.station.station_name}.json"
SHA256Path = f"{scriptFolder}{cf.station.station_name}_key.txt"

mes_shop_floor = f"http://{cf.station.mes_shop_floor}/api/TEST/serial/{sn}/station/{cf.station.station_no}/info"
mes_result = f"http://{cf.station.mes_result}/api/TEST/serial/{sn}/station/{cf.station.station_no}/info"
mesPhases = model.product.MesInfo(sn, cf.station.station_no, cf.station.test_software_version)
test_mode = cf.dut.test_mode
stationObj = model.product.JsonResult(sn, cf.station.station_no, test_mode, cf.dut.qsdk_ver,
                                      cf.station.test_software_version)

FixSerialPort = None
main_form = None
failCount = 0
IfCond = True


def set_globalVal(name, value):
    globals()[name] = value


def get_globalVal(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue


if __name__ == '__main__':
    pass