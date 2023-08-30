#!/usr/bin/env python
# coding: utf-8
"""
@File   : ifelse.py
@Author : Steven.Shen
@Date   : 8/29/2023
@Desc   : 
"""
from common.basicfunc import IsNullOrEmpty


class IfElse:

    def __init__(self, logger):
        self.ifCond_all = True
        self.ifCond = True
        self.logger = logger

    def process_if_else_flow(self, if_else, test_result):
        if if_else.lower() == "if":
            self.ifCond = True if test_result else False
            self.ifCond_all = self.ifCond
        elif if_else.lower() == "&if":
            self.ifCond_all = self.ifCond and test_result
        elif if_else.lower() == "||if":
            self.ifCond_all = self.ifCond or test_result
        elif if_else.lower() == "elif":
            if self.ifCond_all:
                pass  # set isTest = False before test
            else:
                self.ifCond = True if test_result else False
                self.ifCond_all = self.ifCond
        elif if_else.lower() == "else":
            if self.ifCond_all:
                pass  # set isTest = False before test
            else:
                pass
                # self.clear()
            return True
        else:
            raise Exception(f"Unsupported this if flow command:{if_else}!")
        return self.ifCond_all

    def clear(self, if_else):
        if not IsNullOrEmpty(if_else) and if_else.lower() == "else":
            self.ifCond = True
            self.ifCond_all = True
