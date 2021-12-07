#!/usr/cf/env python
# coding: utf-8
"""
@File   : basefunc.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import csv
import json
import os
import subprocess
import time
import platform
import psutil as psutil
from datetime import datetime
import yaml
import conf.logconf as lg
import model

win = platform.system() == "Windows"


def save_config(yaml_file, obj):
    with open(yaml_file, mode='r+', encoding='utf-8') as f:
        readall = f.read()
        try:
            js = json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=4)
            ya = yaml.safe_load(js)
            f.seek(0)
            yaml.safe_dump(ya, stream=f, default_flow_style=False, sort_keys=False, indent=4)
        except Exception as e:
            lg.logger.exception(f"save_config! {e}")
            f.seek(0)
            f.write(readall)
        else:
            pass
            lg.logger.info(f"save conf.yaml success!")


def wrapper(flag):
    def wrapper_inner(func):
        def inners(**kwargs):
            start = None
            if flag:
                start = datetime.now()
            ret = func(**kwargs)
            if flag:
                lg.logger.debug(f'elapsed time:{datetime.now() - start}')
            return ret

        return inners

    return wrapper_inner


def wrapper_time(fun):
    def inner(*args):
        start = datetime.now()
        fun(*args)
        lg.logger.debug(f'elapsed time:{datetime.now() - start}')

    return inner


def create_csv_file(filename, header, updateColumn=False):
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                file = csv.writer(f)
                file.writerow(header)
            lg.logger.debug(f'create_csv_file:{filename}')
        else:
            if updateColumn:
                with open(filename, 'r') as rf:
                    reader = csv.reader(rf)
                    # cl = [row[1] for row in reader]  # 获取第1列
                    rows = [row for row in reader]
                    with open(filename, 'w', newline='') as wf:
                        if [0] != header:
                            rows[0] = header
                            file = csv.writer(wf)
                            file.writerows(rows)
                        lg.logger.info(f'update csvHeader success!')
    except Exception as e:
        lg.logger.exception(e)


def write_csv_file(filename, row):
    try:
        with open(filename, 'a', newline='') as f:
            file = csv.writer(f)
            file.writerow(row)
        lg.logger.debug(f'CollectResultToCsv {filename}')
    except Exception as e:
        lg.logger.exception(e)


def CompareLimit(limitMin, limitMax, value, is_round=False):
    if model.IsNullOrEmpty(limitMin) and model.IsNullOrEmpty(limitMax):
        return True, ''
    if model.IsNullOrEmpty(value):
        return False, ''
    temp = round(float(value)) if is_round else float(value)
    if model.IsNullOrEmpty(limitMin) and not model.IsNullOrEmpty(limitMax):  # 只需比较最大值
        lg.logger.debug("Compare Limit_max...")
        return temp <= float(limitMax), ''
    if not model.IsNullOrEmpty(limitMin) and model.IsNullOrEmpty(limitMax):  # 只需比较最小值
        lg.logger.debug("Compare Limit_min...")
        return temp >= float(limitMin), ''
    if not model.IsNullOrEmpty(limitMin) and not model.IsNullOrEmpty(limitMax):  # 比较最小最大值
        lg.logger.debug("Compare Limit_min and Limit_max...")
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
    Remember that a host may not respond to a ping (ICMP) request even if the host test_name is valid.
    """
    param = '-n' if win else '-cf'
    command = f'ping {param} 1 {host}'
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if win else "utf8"), timeout=timeout)
        if ret.returncode == 0 and 'TTL=' in ret.stdout:
            lg.logger.debug(ret.stdout)
            return True
        else:
            lg.logger.error(f"error:{ret.stdout},{ret.stderr}")
            return False
    except subprocess.TimeoutExpired:
        lg.logger.debug(f'ping {host} Timeout.')
        return False
    except Exception as e:
        lg.logger.exception(e)
        return False


def run_cmd(command, timeout=1):
    """send command, command executed successfully return true,otherwise false"""
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if win else "utf8"), timeout=timeout)
        if ret.returncode == 0:  # 表示命令下发成功，不对命令内容结果做判断
            lg.logger.debug(ret.stdout)
            return True
        else:
            lg.logger.error(f"error:{ret.stderr}")
            return False
    except Exception as e:
        lg.logger.exception(e)
        return False


def kill_process(process_name, killall=True):
    try:
        for pid in psutil.pids():
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if p.name() == process_name:
                    p.kill()
                    lg.logger.debug(f"kill pid-{pid},test_name-{p.name()}")
                    time.sleep(1)
                    if not killall:
                        break
        return True
    except Exception as e:
        lg.logger.exception(e)
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
        lg.logger.exception(e)
        return False


def restart_process(full_path, process_name):
    """kill and start"""
    try:
        if kill_process(process_name):
            return start_process(full_path, process_name)
    except Exception as e:
        lg.logger.exception(e)
        return False


def register(name, email, **kwargs):
    print('test_name:%s, age:%s, others:%s', (name, email, kwargs))


if __name__ == '__main__':
    pass
    # create_csv_file('test.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
    # write_csv_file('test.csv', ['1wqw', '2', '3', '4'])
    # print(str(True))
    # ping('192.168.1.101')
    # ping('127.0.0.1')
    # aa = restart_process('EXCEL.EXE')
    # logger.debug(f"ds{aa}")
    register("demon", "1@1.com")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {})
    register("demon", "1@1.com",
             addr="shanghai")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {'addr': 'shanghai'})
