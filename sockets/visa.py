#!/usr/bin/env python
# coding: utf-8
"""
@File   : visa.py
@Author : Steven.Shen
@Date   : 2022/7/29
@Desc   :
"""
import re
import time

import pyvisa
from sockets.communication import CommAbstract, IsNullOrEmpty
from inspect import currentframe
import conf.logprint as lg


def ReplaceCommonEscapeSequences(date):
    return date.replace('\\n', '\n').replace('\\r', '\r')


def InsertCommonEscapeSequences(date):
    return date.replace('\n', '\\n').replace('\r', '\\r')


class VisaComm(CommAbstract):
    def __init__(self, prompt=None):
        self.prompt = prompt
        self._mbSession = None
        self.rm = pyvisa.ResourceManager()
        lg.logger.debug(self.rm.list_resources())

    def open(self, resourceName=None):
        try:
            if resourceName in self.rm.list_resources():
                self._mbSession = self.rm.open_resource(resourceName)
                IDN = self._mbSession.query("*IDN?")
                lg.logger.debug(IDN)
                return True
            else:
                raise f"resourceName:{resourceName} is not found in ResourceManager!"
        except Exception as e:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{e}')

    def write(self, date: str):
        try:
            textToWrite = ReplaceCommonEscapeSequences(date)
            lg.logger.debug("VisaWrite-->" + textToWrite)
            self._mbSession.write(textToWrite)
        except Exception as e:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{e}')

    def read(self):
        responseContext = ''
        try:
            responseContext = InsertCommonEscapeSequences(self._mbSession.read())
        except Exception as e:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{e}')
        finally:
            lg.logger.debug("VISARead:->" + responseContext)
        return responseContext

    def query(self, cmdStr):
        responseContext = ''
        try:
            responseContext = self._mbSession.query(cmdStr)
        except Exception as e:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{e}')
        finally:
            lg.logger.debug(f"VisaQuery: {cmdStr}->" + responseContext)
        return responseContext

    def close(self):
        self._mbSession.close()

    def SendCommand(self, command, exceptStr='', timeout=3, newline=True):
        strRecAll = ''
        start_time = time.time()
        self._mbSession.timeout = timeout * 1000
        try:
            if '?' not in command:
                self.write(command)
                return True
            else:
                strRecAll = self.query(command)
            if not IsNullOrEmpty(exceptStr):
                if re.search(exceptStr, strRecAll):
                    lg.logger.info(
                        f'send: {command} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                    result = True
                else:
                    lg.logger.error(
                        f'send: {command} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                    result = False
            else:
                result = True
            return result, strRecAll
        except Exception as e:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{e}')
            return False, strRecAll


if __name__ == "__main__":
    vis = VisaComm()
    vis.open('USB0::0x0957::0x8407::US21D4120S::INSTR')
    # vis.query("*IDN?")
    vis.SendCommand("*IDN?")
    vis.SendCommand("VOLT 15.8")
    time.sleep(1)
    vis.SendCommand('Meas:VOLT?')
    vis.SendCommand('Meas:VOLT?')
    # vis.read()
    vis.close()
    # my_instrument = rm.open_resource('GPIB0::14::INSTR')
    # print(my_instrument.query('*IDN?'))
    # my_instrument.write('*IDN?')
    # print(my_instrument.read())
