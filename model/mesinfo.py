#!/usr/bin/env python
# coding: utf-8
"""
@File   : mesinfo.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""


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

    def __init__(self, serial, test_station, test_software_version):
        self.serial = serial
        self.test_station = test_station
        self.test_software_version = test_software_version
