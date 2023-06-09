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
import traceback
import pyvisa
from common.basicfunc import IsNullOrEmpty
from sockets.communication import CommAbstract
from inspect import currentframe


def ReplaceCommonEscapeSequences(date):
    return date.replace('\\n', '\n').replace('\\r', '\r')


def InsertCommonEscapeSequences(date):
    return date.replace('\n', '\\n').replace('\r', '\\r')


class VisaComm(CommAbstract):
    def __init__(self, logger, prompt=None):
        self.prompt = prompt
        self._mbSession = None
        self.rm = pyvisa.ResourceManager()
        self.logger = logger
        # self.debug(self.rm.list_resources())

    def open(self, resourceName=None):
        try:
            if resourceName in self.rm.list_resources():
                self._mbSession = self.rm.open_resource(resourceName)
                # self._mbSession.write("*RST")
                # IDN = self._mbSession.query("*IDN?")
                # self.logger.debug(IDN)
                return True
            else:
                raise f"resourceName:{resourceName} is not found in ResourceManager!"
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e}')

    def write(self, date: str):
        try:
            textToWrite = ReplaceCommonEscapeSequences(date)
            self.logger.debug("VisaWrite-->" + textToWrite)
            self._mbSession.write(textToWrite)
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e}')

    def read(self):
        responseContext = ''
        try:
            responseContext = InsertCommonEscapeSequences(self._mbSession.read())
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e}')
        finally:
            self.logger.debug("VISARead:->" + responseContext)
        return responseContext

    def query(self, cmdStr):
        responseContext = ''
        try:
            responseContext = self._mbSession.query(cmdStr)
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e}')
        finally:
            self.logger.debug(f"VisaQuery: {cmdStr}->" + responseContext)
        return responseContext

    def close(self):
        self._mbSession.close()

    def SendCommand(self, command, exceptStr=None, timeout=3, newline=True):
        strRecAll = ''
        start_time = time.time()
        self._mbSession.timeout = timeout * 1000
        try:
            if '?' not in command:
                self.write(command)
                return True, ''
            else:
                strRecAll = self.query(command)
            if IsNullOrEmpty(exceptStr):
                return True, strRecAll
            if re.search(exceptStr, strRecAll):
                self.logger.info(
                    f'send: {command} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                self.logger.error(
                    f'send: {command} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e},{traceback.format_exc()}')
            return False, strRecAll


if __name__ == "__main__":
    pass
    # vis = VisaComm()
    # vis.open('GPIB0::5::INSTR')
    # vis.SendCommand("*IDN?")
    # time.sleep(1)
    # vis.SendCommand("VOLT 18.5,(@1)")
    # # vis.SendCommand('VOLT:PROT:LEV 60,(@1)')
    # # vis.SendCommand('CURR 1.5,(@1)')
    # # vis.SendCommand('CURR:PROT:STAT ON,(@1)')
    # vis.SendCommand('OUTP ON,(@1)')
    # # vis.SendCommand('*OPC?')
    # vis.SendCommand('MEAS:VOLT? (@1)')
    # # vis.SendCommand('Syst:err?')
    # # vis.close()
    # time.sleep(3)
    # vis.open('GPIB0::5::INSTR')
    # vis.SendCommand("VOLT 8,(@1)")
