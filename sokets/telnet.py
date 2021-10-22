#!/usr/c/env python
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

from model.basefunc import IsNullOrEmpty
from conf.globalconf import logger
from sokets.communication import CommAbstract


class TelnetComm(CommAbstract):
    def __init__(self, host, prompt, port=23):
        self.prompt = prompt
        self.tel = Telnet(host, port, timeout=2, )
        self.tel.debuglevel = 1000
        login_prompt = self.tel.read_until(prompt.encode('utf8'), 2).decode('utf8')
        logger.debug(login_prompt)

    def open(self, *args):
        self.tel.open(self.tel.host, self.tel.port)

    def close(self):
        self.tel.close()
        logger.debug(f"{self.tel.port} serialPort close success!!")

    def read(self):
        self.tel.read_all()

    def write(self, date: str):
        date_bytes = date.encode('utf8')
        self.tel.write(date_bytes)

    def SendCommand(self, command, timeout=10, exceptStr=None, newline=True):
        result = False
        strRecAll = ''
        start_time = time.time()
        if exceptStr is None:
            exceptStr = self.prompt
        try:
            self.tel.timeout = timeout
            if newline and not IsNullOrEmpty(command) and not command == '\n':
                command += "\n"
            else:
                pass
            logger.debug(f"telnet_SendComd-->{command}")
            self.write(command)
            strRecAll = self.tel.read_until(exceptStr.encode('utf-8'), timeout).decode('utf-8')
            logger.debug(strRecAll)
            if re.search(exceptStr, strRecAll):
                logger.info(f'send: {command} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                logger.error(f'send: {command} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except Exception as e:
            logger.exception(e)
            return False, strRecAll
        finally:
            if not self.prompt == exceptStr:
                strRec = self.tel.read_until(self.prompt.encode('utf-8'), timeout).decode('utf-8')
                logger.debug(strRec)


if __name__ == "__main__":
    tl = TelnetComm('192.168.1.101', "root@OpenWrt:/#")
    if tl.SendCommand("dmesg | grep 'mmcblk0' | head -1 | awk '{print $5}'", 10):
        if tl.SendCommand('\n'):
            if tl.SendCommand('luxshare_tool --get-serial-env', 10, '1N'):
                if tl.SendCommand('luxshare_tool --get-mac-env'):
                    if tl.SendCommand("dmesg | grep 'mmcblk0' | head -1 | awk '{print $5}'"):
                        pass
