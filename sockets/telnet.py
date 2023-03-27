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
import traceback
from telnetlib import Telnet
from model.basicfunc import IsNullOrEmpty
from sockets.communication import CommAbstract


class TelnetComm(CommAbstract):
    def __init__(self, logger, host, prompt, port=23):
        self.logger = logger
        self.prompt = prompt
        self.tel = Telnet(host, port, timeout=2, )
        self.tel.debuglevel = 1000
        login_prompt = self.tel.read_until(prompt.encode('utf8'), 2).decode('utf8')
        self.logger.debug(login_prompt)

    def open(self, *args):
        self.tel.open(self.tel.host, self.tel.port)

    def close(self):
        self.tel.close()
        self.logger.debug(f"{self.tel.port} serialPort close success!!")

    def read(self):
        self.tel.read_all()

    def write(self, date: str):
        date_bytes = date.encode('utf8')
        self.tel.write(date_bytes)

    def SendCommand(self, command, exceptStr=None, timeout=10, newline=True):
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
            self.logger.debug(f"telnet_SendCmd-->{command}")
            self.write(command)
            strRecAll = self.tel.read_until(exceptStr.encode('utf-8'), timeout).decode('utf-8')
            self.logger.debug(strRecAll)
            if re.search(exceptStr, strRecAll):
                self.logger.info(f'send: {command} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                self.logger.error(
                    f'send: {command} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except Exception as e:
            self.logger.fatal(f'{e}, {traceback.format_exc()}')
            return False, strRecAll
        finally:
            if not self.prompt == exceptStr:
                strRec = self.tel.read_until(self.prompt.encode('utf-8'), timeout).decode('utf-8')
                self.logger.debug(strRec)


if __name__ == "__main__":
    tl = TelnetComm(None, '192.168.1.101', "root@OpenWrt:/#")
    if tl.SendCommand("dmesg | grep 'mmcblk0' | head -1 | awk '{print $5}'", None, 10):
        if tl.SendCommand('\n'):
            if tl.SendCommand('luxxxx_tool --get-serial-env', None, 10, '1N'):
                if tl.SendCommand('luxxxxx_tool --get-mac-env'):
                    if tl.SendCommand("dmesg | grep 'mmcblk0' | head -1 | awk '{print $5}'"):
                        pass
