#!/usr/bin/env python
# coding: utf-8
"""
@File   : dowhile.py
@Author : Steven.Shen
@Date   : 8/30/2023
@Desc   : 
"""
from enum import Enum


class CycleType(Enum):
    """测试状态枚举类"""
    FOR = 'FOR'
    DoWhile = 'DoWhile'
    WhileDo = 'WhileDo'


class DoWhile:

    def __init__(self, logger):
        self.logger = logger
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self.TotalCycle = -1
        self.CycleName = CycleType.DoWhile
        self.LoopCounter = 1  # current loop number
        self.IsEnd = True  # it is in a loop?
        self._Flag = False
        self.jump = False

    def start(self, StartSuiteNo, StartStepNo):
        if self._Flag:
            raise Exception("the same type Loops cannot be used nested!")
        else:
            self._Flag = True
        self.IsEnd = False  # it is in a loop?
        self.jump = False
        self.StartSuiteNo = StartSuiteNo
        self.StartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start {self.CycleName}, Cycle-{self.LoopCounter}" + '=' * 10)

    def is_end(self, condition) -> bool:
        if not condition:
            self.IsEnd = False
            self._Flag = False
            self.LoopCounter += 1
            self.jump = True
        else:
            self.IsEnd = True
            self.logger.debug('=' * 10 + f"Have Complete {self.CycleName}, ({self.LoopCounter}) Cycle test." + '=' * 10)
            self.clear()
        return self.IsEnd

    def clear(self):
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self.LoopCounter = 1  # current loop number
        self._Flag = False
        self.jump = False
