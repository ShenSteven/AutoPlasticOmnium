#!/usr/bin/env python
# coding: utf-8
"""
@File   : basefunc.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import csv
import hashlib
import os
from enum import Enum

from bin.globalconf import logger


def binary_read(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
        return content.decode(encoding='UTF-8')


def binary_write(filepath, content):
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf8'))


def get_sha256(filepath):
    with open(filepath, 'rb') as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        return sha256obj.hexdigest()


def IsNullOrEmpty(strObj: str):
    if strObj and len(str(strObj)) > 0:
        return False
    else:
        return True


def SetTestStatus(ABORT):
    pass


class TestStatus(Enum):
    PASS = 1
    FAIL = 2
    START = 3
    ABORT = 4


def create_csv_file(filename, header):
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                file = csv.writer(f)
                file.writerow(header)
    except Exception as e:
        logger.exception(e)


def write_csv_file(filename, row):
    try:
        with open(filename, 'a', newline='') as f:
            file = csv.writer(f)
            file.writerow(row)
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    create_csv_file('test.csv', ['No', 'Phase name', 'Test name', 'Error Code'])
    write_csv_file('test.csv', ['1wqw', '2eqweq', '3ewqewqe', '4edsd'])
    print(str(True))
