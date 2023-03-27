#!/usr/bin/env python
# coding: utf-8
"""
@File   : modbus.py
@Author : Steven.Shen
@Date   : 3/27/2023
@Desc   : 
"""
import struct
from enum import Enum
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import modbus_tk.modbus_tcp as modbus_tcp
from model.basicfunc import IsNullOrEmpty
from sockets.serialport import SerialPort


class ErrorCode(Enum):
    """modbus exception codes"""
    ILLEGAL_FUNCTION = 1  # 功能代码不合法
    ILLEGAL_DATA_ADDRESS = 2  # 数据地址不合法
    ILLEGAL_DATA_VALUE = 3  # 数据值不合法
    SLAVE_DEVICE_FAILURE = 4  # slave设备失败
    COMMAND_ACKNOWLEDGE = 5  # 命令已收到
    SLAVE_DEVICE_BUSY = 6  # slave设备忙
    MEMORY_PARITY_ERROR = 8  # 内存奇偶误差


class FunctionCode(Enum):
    """modbus function_code"""
    READ_COILS = 1  # 读线圈
    READ_DISCRETE_INPUTS = 2  # 读离散输入
    READ_HOLDING_REGISTERS = 3  # 读保持寄存器
    READ_INPUT_REGISTERS = 4  # 读输入寄存器
    WRITE_SINGLE_COIL = 5  # 写单一线圈
    WRITE_SINGLE_REGISTER = 6  # 写单一寄存器
    WRITE_MULTIPLE_COILS = 15  # 写多个线圈
    WRITE_MULTIPLE_REGISTERS = 16  # 写多寄存器


# execute(slave, function_code, starting_address, quantity_of_x=0, output_value=0,
# data_format="", expected_length=-1, write_starting_address_FC23=0）

class Modbus:
    def __init__(self, logger, ip, port, baudRate=None, write_timeout=1, timeout=0.5):
        self.logger = logger
        if IsNullOrEmpty(ip) and baudRate is not None:
            serial_rtu = SerialPort(logger, port, baudRate=baudRate, write_timeout=write_timeout, timeout=timeout)
            self.master = modbus_rtu.RtuMaster(serial_rtu)
        else:
            self.master = modbus_tcp.TcpMaster(ip, port)
        self.master.set_timeout(1.0)

    def SendCommand(self):
        res1 = self.master.execute(1, cst.READ_COILS, 0, 10)
        res2 = self.master.execute(2, cst.READ_DISCRETE_INPUTS, 0, 8)
        res3 = self.master.execute(3, cst.READ_INPUT_REGISTERS, 100, 3)
        res4 = self.master.execute(4, cst.READ_HOLDING_REGISTERS, 100, 12)
        res5 = self.master.execute(5, cst.WRITE_SINGLE_COIL, 7, output_value=1)
        res6 = self.master.execute(6, cst.WRITE_SINGLE_REGISTER, 100, output_value=54)
        res7 = self.master.execute(7, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1, 1, 0, 1, 1])
        # res8 = self.master.execute(8, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12))


def ReadFloat(*args, reverse=False):
    for n, m in args:
        n, m = '%04x' % n, '%04x' % m
    if reverse:
        v = n + m
    else:
        v = m + n
    y_bytes = bytes.fromhex(v)
    y = struct.unpack('!f', y_bytes)[0]
    y = round(y, 6)
    return y


def WriteFloat(value, reverse=False):
    y_bytes = struct.pack('!f', value)
    # y_hex = bytes.hex(y_bytes)
    y_hex = ''.join(['%02x' % i for i in y_bytes])
    n, m = y_hex[:-4], y_hex[-4:]
    n, m = int(n, 16), int(m, 16)
    if reverse:
        v = [n, m]
    else:
        v = [m, n]
    return v


def ReadDint(*args, reverse=False):
    for n, m in args:
        n, m = '%04x' % n, '%04x' % m
    if reverse:
        v = n + m
    else:
        v = m + n
    y_bytes = bytes.fromhex(v)
    y = struct.unpack('!i', y_bytes)[0]
    return y


def WriteDint(value, reverse=False):
    y_bytes = struct.pack('!i', value)
    # y_hex = bytes.hex(y_bytes)
    y_hex = ''.join(['%02x' % i for i in y_bytes])
    n, m = y_hex[:-4], y_hex[-4:]
    n, m = int(n, 16), int(m, 16)
    if reverse:
        v = [n, m]
    else:
        v = [m, n]
    return v


if __name__ == "__main__":
    print(ReadFloat((14470, 16462)))
    print(ReadFloat((50856, 16529)))
    print(WriteFloat(3.2222))
    print(ReadDint((1734, 6970)))
    print(WriteDint(456787654))
