#!/usr/bin/env python
# coding: utf-8
"""
@File   : product.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""


class JsonResult:
    serial = ""
    test_station = ""
    start_time = ""
    finish_time = ""
    status = "canceled"
    mode = ""
    error_code = ""
    error_details = ""
    luxshare_qsdk_version = ""
    test_software_version = ""
    test_phases = []
    tests = []

    def __init__(self, serial, test_station, test_mode, qsdkVer, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.mode = test_mode
        self.luxshare_qsdk_version = qsdkVer
        self.test_software_version = test_software_version
        self.test_phases = []
        self.tests = []


class SuiteItem:
    phase_name = ""
    status = "canceled"
    start_time = ""
    finish_time = ""
    phase_details = ""
    error_code = ""
    phase_items = []

    def __init__(self):
        self.phase_items = []


class StepItem:
    test_name = None
    test_value = None
    units = None
    error_code = None
    lower_limit = None
    upper_limit = None
    status = None
    start_time = None
    finish_time = None


class MesInfo:
    serial = ""
    status = ''
    start_time = ""
    finish_time = ""
    test_station = ""
    error_code = ""
    error_details = ""
    test_software_version = None
    PartNumber = None
    MacAddress = None
    first_fail = None
    HW_REVISION = ''
    JSON_UPLOAD = ''
    MES_UPLOAD = ''

    def __init__(self, serial, test_station, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.test_software_version = test_software_version


if __name__ == '__main__':
    pass
