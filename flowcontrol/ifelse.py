#!/usr/bin/env python
# coding: utf-8
"""
@File   : ifelse.py
@Author : Steven.Shen
@Date   : 8/29/2023
@Desc   : 
"""
from PyQt5.QtCore import Qt


class IfElse:

    def __init__(self, logger):
        self.ifCond_all = True
        self.ifCond = True
        self.logger = logger

    def process_if_else_flow(self, keyword, test_result):
        if keyword.lower() == "if":
            self.ifCond = True if test_result else False
            self.ifCond_all = self.ifCond
        elif keyword.lower() == "&if":
            self.ifCond_all = self.ifCond and test_result
        elif keyword.lower() == "||if":
            self.ifCond_all = self.ifCond or test_result
        elif keyword.lower() == "elif":
            if self.ifCond_all:
                pass  # set isTest = False before test
            else:
                self.ifCond = True if test_result else False
                self.ifCond_all = self.ifCond
        elif keyword.lower() == "else":
            if self.ifCond_all:
                pass  # set isTest = False before test
            else:
                pass
                # self.clear()
            return True
        else:
            raise Exception(f"Unsupported this if flow command:{keyword}!")
        return self.ifCond_all

    def clear(self, keyword):
        if keyword.lower() == "else":
            self.ifCond = True
            self.ifCond_all = True
