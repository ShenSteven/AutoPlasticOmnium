#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
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
SN = sn
MesMac = "FF:FF:FF:FF:FF"
dut_mode = 'firefly'
error_code_first_fail = ""
error_details_first_fail = ""

mes_shop_floor = f"http://{c_station['mes_shop_floor']}/api/TEST/serial/{sn}/station/{c_station['station_no']}/info"
mes_result = f"http://{c_station['mes_result']}/api/TEST/serial/{sn}/station/{c_station['station_no']}/info"
mesPhases = MesInfo(sn, c_station['station_no'], c_station['test_software_version'])

test_mode = 'production'
client_result_url = ""
station = Station(sn, c_station['station_no'], test_mode, c_dut['qsdk_ver'], c_station['test_software_version'])

csv_list_header = []
csv_list_result = []
dut_comm = None
dut_ip = ''


def set_globalVal(name, value):
    globals()[name] = value


def get_globalVal(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue
