#!/usr/bin/env python
# coding: utf-8
"""
@File   : communication.py
@Author : Steven.Shen
@Date   : 2021/9/6
@Desc   : 
"""
from abc import ABCMeta, abstractmethod


class CommAbstract(metaclass=ABCMeta):
    # isOpen = False
    # host = ''
    # port = ''
    # user = ''
    # passwd = ''
    # logger = None

    @abstractmethod
    def open(self, *args):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def write(self, date: str):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def SendCommand(self, command, exceptStr=None, timeout=10, newline=True):
        pass
