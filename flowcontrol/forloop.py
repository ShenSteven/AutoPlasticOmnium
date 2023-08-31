#!/usr/bin/env python
# coding: utf-8
"""
@File   : forloop.py
@Author : Steven.Shen
@Date   : 8/29/2023
@Desc   : 
"""


class ForLoop:

    def __init__(self, logger):
        self.logger = logger
        self.StartStepNo = -1
        self.StartSuiteNo = -1
        self._TotalCycle = 0
        self.CycleCounter = 1  # current loop number
        self.IsEnd = True  # it is in a loop?
        self._forFlag = False
        self.jump = False

    def start(self, StartSuiteNo, StartStepNo, totalCycle):
        if self._forFlag:
            raise Exception("For loops cannot be used nested!")
        else:
            self._forFlag = True
        self.IsEnd = False  # it is in a loop?
        self.jump = False
        self._TotalCycle = totalCycle
        self.StartSuiteNo = StartSuiteNo
        self.StartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start Cycle-{self.CycleCounter},Total Cycle-{self._TotalCycle}" + '=' * 10)

    def is_end(self) -> bool:
        if self.CycleCounter < self._TotalCycle:
            self.IsEnd = False
            self._forFlag = False
            self.CycleCounter += 1
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
        self.CycleCounter = 1  # current loop number
        self._forFlag = False
        self.jump = False
