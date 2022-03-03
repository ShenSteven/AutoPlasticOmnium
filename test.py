#!/usr/bin/env python
# coding: utf-8
"""
@File   : test.py
@Author : Steven.Shen
@Date   : 2022/3/3
@Desc   : 
"""


class person(object):
    def __init__(self):
        self.__age = 18

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):
        self.__age = value


p = person()
print(p.age)
p.age = 20
print(p.age)
print(p.__dict__)
