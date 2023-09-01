#!/usr/bin/env python
# coding: utf-8
"""
@File   : whileloop.py
@Author : Steven.Shen
@Date   : 8/30/2023
@Desc   : 
"""
from enum import Enum


class CycleType(Enum):
    """测试状态枚举类"""
    FOR = 'FOR'
    DoWhile = 'DoWhile'
    While = 'While'


class WhileLoop:

    def __init__(self, logger):
        self.EndStepNo = -2
        self.EndSuiteNo = -2
        self.logger = logger
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self.TotalCycle = -1
        self.CycleName = CycleType.While
        self.LoopCounter = 1  # current loop number
        self.IsEnd = True  # it is in a loop?
        self._Flag = False
        self.jump = False
        self.while_condition = None

    def start(self, StartSuiteNo, StartStepNo, condition):
        if self._Flag:
            raise Exception("the same type Loops cannot be used nested!")
        else:
            self._Flag = True
        self.StartSuiteNo = StartSuiteNo
        self.StartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start {self.CycleName}, Cycle-{self.LoopCounter}" + '=' * 10)
        if condition:
            self.IsEnd = False  # it is in a loop?
            self._Flag = False
            self.LoopCounter += 1
            self.jump = True
            self.while_condition = True
        else:
            self.IsEnd = False  # it is in a loop?
            self._Flag = False
            # self.LoopCounter += 1
            self.jump = False
            self.while_condition = False
            # self.IsEnd = True
            # self.while_condition = False
            # self.logger.debug('=' * 10 + f"Have Complete {self.CycleName}, ({self.LoopCounter}) Cycle test." + '=' * 10)
            # self.clear()

    def is_end(self) -> bool:
        if self.while_condition:
            self.IsEnd = False
            self._Flag = False
            self.jump = True
            self.while_condition = None
        else:
            self.IsEnd = True
            self.clear()
        return self.IsEnd

    def clear(self):
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self.LoopCounter = 1  # current loop number
        self._Flag = False
        self.jump = False
        self.while_condition = None
