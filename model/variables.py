#!/usr/bin/env python
# coding: utf-8
"""
@File   : Variables.py
@Author : Steven.Shen
@Date   : 2022/6/5
@Desc   :
"""
from datetime import datetime


class Variables:
    """Environment variables and system variables"""

    def __init__(self, station_name, station_no, sn, dut_default_ip, log_path, channel, group='1'):
        self.SN = sn
        self.Station = station_name
        self.StationNo = station_no
        self.CellNo = channel
        self.Group = group
        self.DutDefaultIP = dut_default_ip
        self.LogPath = log_path
        self.WorkOrder = "NULL"
        self.Year = datetime.now().strftime('%y')
        self.Month = datetime.now().strftime('%m')
        self.Day = datetime.now().strftime('%d')


if __name__ == '__main__':
    pass
