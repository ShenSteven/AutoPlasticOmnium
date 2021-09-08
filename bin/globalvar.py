#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
import sys
from datetime import datetime
import os

from bin.globalconf import c_station, c_dut, logger
from model.mesinfo import MesInfo
from model.product import Station
from sokets.serialport import SerialPort

# try:
#     fix_serial = SerialPort('COM3', 1115200)
#     dut_serial = SerialPort('COM9', 1115200)
# except Exception as e:
#     logger.exception(e)
#     sys.exit()

sn = 'G1234568799NSS'
dut_mode = 'firefly'
error_code_first_fail = ""
error_details_first_fail = ""
testlog = os.path.join(f"{c_station['log_folder']}", datetime.now().strftime('%Y%m%d'),
                       f"{datetime.now().strftime('%H-%M-%S')}.txt")

mes_shop_floor = f"http://{c_station['mes_shop_floor']}/api/TEST/serial/{sn}/station/{c_station['station_no']}/info"
mes_result = f"http://{c_station['mes_result']}/api/TEST/serial/{sn}/station/{c_station['station_no']}/info"
mesPhases = MesInfo(sn, c_station['station_no'], c_station['test_software_version'])

test_mode = 'production'
client_result_url = ""
station = Station(sn, c_station['station_no'], test_mode, c_dut['qsdk_ver'], c_station['test_software_version'])


def set_globalVal(name, value):
    globals()[name] = value


def get_globalVal(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue
