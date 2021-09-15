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
import subprocess
import time
from datetime import datetime
from enum import Enum
import platform

import psutil as psutil

from bin.globalconf import logger

win = platform.system() == "Windows"


def wrapper(flag):
    def wrapper_inner(func):
        def inners(**kwargs):
            start = None
            if flag:
                start = datetime.now()
            ret = func(**kwargs)
            if flag:
                logger.debug(f'elapsed time:{datetime.now() - start}')
            return ret

        return inners

    return wrapper_inner


def wrapper_time(fun):
    def inner(*args):
        start = datetime.now()
        fun(*args)
        logger.debug(f'elapsed time:{datetime.now() - start}')

    return inner


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


def SetTestStatus():
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


def CompareLimit(limitMin, limitMax, value, is_round=False):
    if IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):
        return True, ''
    if IsNullOrEmpty(value):
        return False, ''
    temp = round(float(value)) if is_round else float(value)
    if IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 只需比较最大值
        logger.debug("Compare Limit_max...")
        return temp <= float(limitMax), ''
    if not IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):  # 只需比较最小值
        logger.debug("Compare Limit_min...")
        return temp >= float(limitMin), ''
    if not IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 比较最小最大值
        logger.debug("Compare Limit_min and Limit_max...")
        if float(limitMin) <= temp <= float(limitMax):
            return True, ''
        else:
            if temp < float(limitMin):
                return False, 'TooLow'
            else:
                return False, 'TooHigh'


# @wrapper_time
def ping(host, timeout=1):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    param = '-n' if win else '-c'
    command = f'ping {param} 1 {host}'
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if win else "utf8"), timeout=timeout)
        if ret.returncode == 0 and 'TTL=' in ret.stdout:
            logger.debug(ret.stdout)
            return True
        else:
            logger.error(f"error:{ret.stdout},{ret.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.debug(f'ping {host} Timeout.')
        return False
    except Exception as e:
        logger.exception(e)
        return False


def run_cmd(command, timeout=1):
    """send command, command executed successfully return true,otherwise false"""
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if win else "utf8"), timeout=timeout)
        if ret.returncode == 0:  # 表示命令下发成功，不对命令内容结果做判断
            logger.debug(ret.stdout)
            return True
        else:
            logger.error(f"error:{ret.stderr}")
            return False
    except Exception as e:
        logger.exception(e)
        return False


def kill_process(process_name, killall=True):
    try:
        for pid in psutil.pids():
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if p.name() == process_name:
                    p.kill()
                    logger.debug(f"kill pid-{pid},name-{p.name()}")
                    time.sleep(1)
                    if not killall:
                        break
        return True
    except Exception as e:
        logger.exception(e)
        return False


def process_exists(process_name):
    pids = psutil.pids()
    ps = [psutil.Process(pid) for pid in pids]
    process_names = [p.name for p in ps]
    if process_name in process_names:
        return True
    else:
        return False


def start_process(full_path, process_name):
    """if process exists, return , otherwise start it and check"""
    try:
        if not process_exists(process_name):
            run_cmd(full_path)
            time.sleep(3)
            return process_exists(process_name)
        else:
            return True
    except Exception as e:
        logger.exception(e)
        return False


def restart_process(full_path, process_name):
    """kill and start"""
    try:
        if kill_process(process_name):
            return start_process(full_path, process_name)
    except Exception as e:
        logger.exception(e)
        return False

def register(name, email, **kwargs):
    print('name:%s, age:%s, others:%s', (name, email, kwargs))


if __name__ == '__main__':
    pass
    # create_csv_file('test.csv', ['No', 'Phase name', 'Test name', 'Error Code'])
    # write_csv_file('test.csv', ['1wqw', '2', '3', '4'])
    # print(str(True))
    # ping('192.168.1.101')
    # ping('127.0.0.1')
    # aa = restart_process('EXCEL.EXE')
    # logger.debug(f"ds{aa}")
    register("demon", "1@1.com")  # name:%s, age:%s, others:%s ('demon', '1@1.com', {})
    register("demon", "1@1.com",
             addr="shanghai")  # name:%s, age:%s, others:%s ('demon', '1@1.com', {'addr': 'shanghai'})
