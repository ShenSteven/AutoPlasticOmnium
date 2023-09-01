#!/usr/bin/env python
# coding: utf-8
"""
@File   : whileloop.py
@Author : Steven.Shen
@Date   : 8/30/2023
@Desc   : 
"""
from flowcontrol.loop import CycleType, Loop


class WhileLoop(Loop):

    def __init__(self, logger):
        self.logger = logger
        self.CycleName = CycleType.While

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
            self.jump = False
            self.while_condition = False
            # self.logger.debug('=' * 10 + f"Have Complete {self.CycleName}, ({self.LoopCounter}) Cycle test." + '=' * 10)

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
