#!/usr/bin/env python
# coding: utf-8
"""
@File   : loop.py
@Author : Steven.Shen
@Date   : 9/1/2023
@Desc   : 
"""
from abc import ABCMeta, abstractmethod
from enum import Enum


class CycleType(Enum):
    """测试状态枚举类"""
    FOR = 'FOR'
    DoWhile = 'DoWhile'
    While = 'While'


class Loop(metaclass=ABCMeta):
    StartStepNo = -1
    StartSuiteNo = -1
    _TotalCycle = 0
    LoopCounter = 1  # current loop number
    IsEnd = True  # it is in a loop?
    _Flag = False
    jump = False
    while_condition = None

    @abstractmethod
    def start(self, *arg):
        pass

    @abstractmethod
    def is_end(self, *arg) -> bool:
        pass

    @abstractmethod
    def clear(self):
        pass
