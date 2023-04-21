#!/usr/bin/env python
# coding: utf-8
"""
@File   : Variables.py
@Author : Steven.Shen
@Date   : 2022/6/5
@Desc   :
"""
from datetime import datetime
import conf.globalvar as gv


class Variables:
    """Environment variables and system variables"""

    def __init__(self, sn, channel, group='1'):
        self.SN = sn
        self.CellNo = channel
        self.Group = group
        self.WorkOrder = "NULL"
        self.Year = datetime.now().strftime('%y')
        self.Month = datetime.now().strftime('%m')
        self.Day = datetime.now().strftime('%d')
        self.Config = gv.cf

    def __getitem__(self, i):
        if i >= len(self.__dict__.items()):
            raise IndexError("out of index")
        item = list(self.__dict__.items())[i]
        return item


if __name__ == '__main__':
    pass
    TestVariables = Variables('SN0001', '1', '4')
    print(TestVariables.__dict__)

