#!/usr/bin/env python
# coding: utf-8
"""
@File   : forloop.py
@Author : Steven.Shen
@Date   : 8/29/2023
@Desc   : 
"""
from bll.flowcontrol.loop import Loop, CycleType


class ForLoop(Loop):

    def __init__(self, logger):
        self.logger = logger
        self.CycleName = CycleType.FOR

    def start(self, StartSuiteNo, StartStepNo, totalCycle):
        if self._Flag:
            raise Exception("For loops cannot be used nested!")
        else:
            self._Flag = True
        self.IsEnd = False  # it is in a loop?
        self.jump = False
        self._TotalCycle = totalCycle
        self.StartSuiteNo = StartSuiteNo
        self.StartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start Cycle-{self.LoopCounter},Total Cycle-{self._TotalCycle}" + '=' * 10)

    def is_end(self) -> bool:
        if self.LoopCounter < self._TotalCycle:
            self.IsEnd = False
            self._Flag = False
            self.LoopCounter += 1
            self.jump = True
        else:
            self.IsEnd = True
            self.logger.debug('=' * 10 + f"Have Complete all ({self._TotalCycle}) Cycle test." + '=' * 10)
            self.clear()
        return self.IsEnd

    def clear(self):
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self._TotalCycle = 0
        self.LoopCounter = 1  # current loop number
        self._Flag = False
        self.jump = False
