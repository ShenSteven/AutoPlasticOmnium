#!/usr/bin/env python
# coding: utf-8
"""
@File   : product.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""


class JsonObject:

    def __init__(self, serial, test_station, test_mode, image_version, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.mode = test_mode
        self.luxshare_qsdk_version = image_version
        self.test_software_version = test_software_version
        self.test_phases = None
        self.tests = []
        self.start_time = ""
        self.finish_time = ""
        self.status = "canceled"
        self.error_code = ""
        self.error_details = ""


class SuiteItem:

    def __init__(self):
        self.phase_name = ""
        self.status = "canceled"
        self.start_time = ""
        self.finish_time = ""
        self.phase_details = ""
        self.error_code = ""
        self.phase_items = []


class StepItem:
    def __init__(self):
        self.test_name = None
        self.test_value = None
        self.units = None
        self.error_code = None
        self.lower_limit = None
        self.upper_limit = None
        self.status = None
        self.start_time = None
        self.finish_time = None


class MesInfo:

    def __init__(self, serial, test_station, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.test_software_version = test_software_version
        self.status = ''
        self.start_time = ""
        self.finish_time = ""
        self.error_code = ""
        self.error_details = ""
        self.PartNumber = None
        self.MacAddress = None
        self.first_fail = None
        self.HW_REVISION = ''
        self.JSON_UPLOAD = ''
        self.MES_UPLOAD = ''


if __name__ == '__main__':
    pass
