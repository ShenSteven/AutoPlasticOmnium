#!/usr/bin/env python
# coding: utf-8
"""
@File   : serialport.py
@Author : Steven.Shen
@Date   : 2021/9/6
@Desc   : 
"""
import re
import time
import traceback

from serial import Serial, EIGHTBITS, STOPBITS_ONE, PARITY_NONE
from model.basicfunc import IsNullOrEmpty
from sockets.communication import CommAbstract
import conf.logprint as lg


class SerialPort(CommAbstract):

    def __init__(self, port, baudRate=115200, write_timeout=1, timeout=0.5):
        self.ser = Serial(port, baudrate=baudRate, write_timeout=write_timeout, timeout=timeout, bytesize=EIGHTBITS,
                          stopbits=STOPBITS_ONE, parity=PARITY_NONE)

    def open(self, *args):
        try:
            if self.ser.isOpen():
                self.close()
            self.ser.open()
            lg.logger.info(f'{self.ser.port} serialPort.Open()!!')
            return True
        except Exception as e:
            lg.logger.fatal(f'{e}, {traceback.format_exc()}')
            return False

    def close(self):
        self.ser.close()
        lg.logger.debug(f"{self.ser.port} serialPort close {'success' if not self.ser.is_open else 'fail'} !!")

    def read(self):
        self.ser.read()

    def write(self, date: str):
        self.ser.write(date.encode('utf-8'))

    def SendCommand(self, command, exceptStr=None, timeout=10, newline=True):
        strRecAll = ''
        start_time = time.time()
        try:
            self.ser.timeout = timeout
            if newline and not IsNullOrEmpty(command):
                command += "\n"
            else:
                pass
            time.sleep(0.01)
            lg.logger.debug(f"{self.ser.port}_SendComd-->{command}")
            self.ser.reset_output_buffer()
            self.ser.reset_input_buffer()
            if command is not None:
                self.write(command)
            self.ser.flush()
            if IsNullOrEmpty(exceptStr):
                exceptStr = ''
                time.sleep(timeout * 0.8)
            strRecAll = self.ser.read_until(exceptStr.encode('utf-8')).decode('utf-8')
            lg.logger.debug(strRecAll)
            if IsNullOrEmpty(exceptStr):
                return True, strRecAll
            if re.search(exceptStr, strRecAll):
                lg.logger.info(f'wait until {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                lg.logger.error(f'wait until {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except Exception as e:
            lg.logger.fatal(f'{e}, {traceback.format_exc()}')
            return False, strRecAll


if __name__ == "__main__":
    com = SerialPort('COM7', 115200, 1, 1)
    com.SendCommand('', 'luxxxx SW Version :', 100)
    com.SendCommand('\n', 'root@OpenWrt:/#', 3)
    com.SendCommand('luxxxx_tool --get-mac-env', 'root@OpenWrt:/#')
