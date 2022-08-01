#!/usr/bin/env python
# coding: utf-8
"""
@File   : visa.py
@Author : Steven.Shen
@Date   : 2022/7/29
@Desc   :
"""

import pyvisa

rm = pyvisa.ResourceManager()
print(rm.list_resources())
device = rm.open_resource('TCPIP0::192.168.8.182::inst0::INSTR')
ID = device.query("*IDN?")
device.write("CURR: 2")
# my_instrument = rm.open_resource('GPIB0::14::INSTR')
# print(my_instrument.query('*IDN?'))
# my_instrument.write('*IDN?')
# print(my_instrument.read())
