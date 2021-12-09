#!/usr/bin/env python
# coding: utf-8
"""
@File   : runtimehook.py
@Author : Steven.Shen
@Date   : 2021/12/8
@Desc   : 
"""
import sys
import os

currentdir = os.path.dirname(sys.argv[0])
libdir = os.path.join(currentdir, "lib").replace('\\', '/')
print(currentdir)
sys.path.append(libdir)
os.environ['path'] += f';{libdir}'
print(sys.path)
