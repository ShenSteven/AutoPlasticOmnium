#!/usr/bin/env python
# coding: utf-8
"""
@File   : testcase.py
@Author : Steven.Shen
@Date   : 2022/6/5
@Desc   :
"""


class TestGlobalVar:
    def __init__(self, sn, station_name, station_no, dut_default_ip, log_path):
        self.SN = sn
        self.Station = station_name
        self.StationNo = station_no
        self.DutDefaultIP = dut_default_ip
        self.LogPath = log_path
        self.WorkOrder = "NULL"


if __name__ == '__main__':
    pass
