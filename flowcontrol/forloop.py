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
        self.ForStartStepNo = -1
        self.ForStartSuiteNo = -1
        self._ForTotalCycle = 0
        self.ForCycleCounter = 1  # current loop number
        self.IsEnd = True  # it is in a loop?
        self._forFlag = False
        self.jump = False

    def start(self, totalCycle, StartSuiteNo, StartStepNo):
        if self._forFlag:
            raise Exception("For loops cannot be used nested!")
        else:
            self._forFlag = True
        self.IsEnd = False  # it is in a loop?
        self.jump = False
        self._ForTotalCycle = totalCycle
        self.ForStartSuiteNo = StartSuiteNo
        self.ForStartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start Cycle-{self.ForCycleCounter},Total Cycle-{self._ForTotalCycle}" + '=' * 10)

    def is_end(self) -> bool:
        if self.ForCycleCounter < self._ForTotalCycle:
            self.IsEnd = False
            self._forFlag = False
            self.ForCycleCounter += 1
            self.jump = True
        else:
            self.IsEnd = True
            self.logger.debug('=' * 10 + f"Have Complete all ({self._ForTotalCycle}) Cycle test." + '=' * 10)
            self.clear()
        return self.IsEnd

    def clear(self):
        self.ForStartStepNo = -1
        self.ForStartSuiteNo = -1
        self._ForTotalCycle = 0
        self.ForCycleCounter = 1  # current loop number
        self._forFlag = False
        self.jump = False
