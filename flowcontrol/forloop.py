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
        self.ForStartStepNo = 0
        self.ForStartSuiteNo = 0
        self.ForTotalCycle = 0
        self.ForCycleCounter = 1  # current loop number
        self.IsForEnd = False  # it is in a loop?
        self.ForFlag = False

    def start_for(self, totalCycle, StartSuiteNo, StartStepNo):
        if self.ForFlag:
            raise Exception("For loops cannot be used nested!")
        else:
            self.ForFlag = True
        self.ForTotalCycle = totalCycle
        self.ForStartSuiteNo = StartSuiteNo
        self.ForStartStepNo = StartStepNo
        self.logger.debug('=' * 10 + f"Start Cycle-{self.ForCycleCounter},TotalCycle-{self.ForTotalCycle}" + '=' * 10)

    def is_end_for(self):
        if self.ForCycleCounter < self.ForTotalCycle:
            self.IsForEnd = False
            self.ForFlag = False
            self.ForCycleCounter += 1
        else:
            self.IsForEnd = True
            self.ForFlag = False
            self.ForCycleCounter = 1
            self.logger.debug('=' * 10 + f"Have Complete all ({self.ForTotalCycle}) Cycle test." + '=' * 10)
        return self.IsForEnd
