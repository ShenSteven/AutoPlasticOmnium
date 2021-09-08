#!/usr/bin/env python
# coding: utf-8
"""
@File   : telnet.py
@Author : Steven.Shen
@Date   : 2021/9/6
@Desc   : 
"""
import re
import time
from telnetlib import Telnet

from bin.basefunc import IsNullOrEmpty
from bin.globalconf import logger
from sokets.communication import CommAbstract


class TelnetComm(CommAbstract):
    def __init__(self, host, port=23):
        self.tel = Telnet(host, port)

    def open(self, *args):
        self.tel.open(self.tel.host, self.tel.port)

    def close(self):
        self.tel.close()
        logger.debug(f"{self.tel.port} serialPort close success!!")

    def read(self):
        self.tel.read_all()

    def write(self, date: str):
        date_bytes = date.encode('utf-8')
        self.tel.write(date_bytes)

    def SendCommand(self, command, exceptStr, timeout=10, newline=True):
        result = False
        strRecAll = ''
        try:
            self.tel.timeout = timeout
            if newline and not IsNullOrEmpty(command):
                command += "\n"
            else:
                pass
            time.sleep(0.01)
            logger.debug(f"{self.tel.port}_SendComd-->{command}")
            self.write(command)
            strRecAll = self.tel.read_until(exceptStr.encode('utf-8')).decode('utf-8', timeout)
            logger.debug(strRecAll)
            if re.search(exceptStr, strRecAll):
                logger.info(f'wait until {exceptStr} success in {timeout}s')
                result = True
            else:
                logger.error(f'wait {exceptStr} timeout in {timeout}s')
                result = False
            return result, strRecAll
        except Exception as e:
            logger.exception(e)
            return False, strRecAll
