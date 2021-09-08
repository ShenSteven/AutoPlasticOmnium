#!/usr/bin/env python
# coding: utf-8
"""
@File   : product.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""


class Station:
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

    def __init__(self, serial, test_station, test_mode, qsdkVer, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.mode = test_mode
        self.luxshare_qsdk_version = qsdkVer
        self.test_software_version = test_software_version
        self.test_phases = []


class test_phases:
    phase_name = ""
    status = "canceled"
    start_time = ""
    finish_time = ""
    phase_details = ""
    error_code = ""
    phase_items = []

    def __init__(self):
        self.phase_items = []


class phase_items:
    name = None
    value = None
    unit = None
    limit_min = None
    limit_max = None
    status = None
    spec = None
