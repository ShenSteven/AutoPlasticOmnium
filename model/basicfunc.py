#!/usr/bin/env python
# coding: utf-8
"""
@File   : basic func.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import os
import csv
import platform
import subprocess
import time
from datetime import datetime
import psutil
import hashlib
from socket import AddressFamily


def ping(logger, host, timeout=1):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host test_name is valid.
    """
    IsWind = platform.system() == 'Windows'
    param = '-n' if IsWind else '-cf'
    command = f'ping {param} 1 {host}'
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if IsWind else "utf8"), timeout=timeout)
        if ret.returncode == 0 and 'TTL=' in ret.stdout:
            logger.debug(ret.stdout)
            return True
        else:
            logger.error(f"error:{ret.stdout},{ret.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.debug(f'ping {host} Timeout.')
        raise
    except Exception as e:
        logger.fatal(e)
        raise


def run_cmd(logger, command, timeout=3):
    """send command, command executed successfully return true,otherwise false"""
    try:
        IsWind = platform.system() == 'Windows'
        logger.debug(f'run_cmd-->{command}')
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if IsWind else "utf8"), timeout=timeout)
        if ret.returncode == 0:  # 表示命令下发成功，不对命令内容结果做判断
            logger.debug(ret.stdout)
            return True, ret.stdout
        else:
            logger.error(f"error:{ret.stderr}")
            return False, ret.stdout
    except Exception as e:
        logger.fatal(e)
        raise


def kill_process(logger, process_name, killall=True):
    try:
        for pid in psutil.pids():
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if p.name() == process_name:
                    p.kill()
                    logger.debug(f"kill pid-{pid},test_name-{p.name()}")
                    time.sleep(1)
                    if not killall:
                        break
        return True
    except Exception as e:
        logger.fatal(e)
        raise e
        # return False


def process_exists(process_name):
    pids = psutil.pids()
    ps = [psutil.Process(pid) for pid in pids]
    process_names = [p.name for p in ps]
    if process_name in process_names:
        return True
    else:
        return False


def start_process(logger, full_path, process_name):
    """if process exists, return , otherwise start it and check"""
    try:
        if not process_exists(process_name):
            run_cmd(logger, full_path)
            time.sleep(3)
            return process_exists(process_name)
        else:
            return True
    except Exception as e:
        logger.fatal(e)
        raise e
        # return False


def restart_process(logger, full_path, process_name):
    """kill and start"""
    try:
        if kill_process(logger, process_name):
            return start_process(logger, full_path, process_name)
    except Exception as e:
        logger.fatal(e)
        raise e
        # return False


# def save_config(logger, yaml_file, obj):
#     with open(yaml_file, mode='r+', encoding='utf-8') as f:
#         readall = f.read()
#         try:
#             js = json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=4)
#             ya = yaml.safe_load(js)
#             f.seek(0)
#             yaml.safe_dump(ya, stream=f, default_flow_style=False, sort_keys=False, indent=4)
#         except Exception as e:
#             logger.fatal(f"save_config! {e}")
#             f.seek(0)
#             f.write(readall)
#             raise
#         else:
#             logger.info(f"save conf.yaml success!")


def wrapper(logger, flag):
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


def wrapper_time(logger, fun):
    def inner(*args):
        start = datetime.now()
        fun(*args)
        logger.debug(f'elapsed time:{datetime.now() - start}')

    return inner


def create_csv_file(logger, filename, header, updateColumn=False):
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                file = csv.writer(f)
                file.writerow(header)
            logger.debug(f'create_csv_file:{filename}')
        else:
            if updateColumn:
                with open(filename, 'r+', newline='') as rwf:
                    reader = csv.reader(rwf)
                    rows = [row for row in reader]
                    if [0] != header:
                        rows[0] = header
                        rwf.seek(0)
                        file = csv.writer(rwf)
                        file.writerows(rows)
                    logger.debug(f'update csvHeader success!')
    except Exception as e:
        logger.fatal(e)
        raise e


def write_csv_file(logger, filename, row):
    try:
        with open(filename, 'a', newline='') as f:
            file = csv.writer(f)
            file.writerow(row)
    except Exception as e:
        logger.fatal(e)
        raise e


def IsNullOrEmpty(strObj: str):
    if strObj and len(str(strObj)) > 0:
        return False
    else:
        return True


def binary_read(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
        return content.decode(encoding='UTF-8')


def binary_write(filepath, content):
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf8'))


def get_sha256(filepath) -> str:
    with open(filepath, 'rb') as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        return sha256obj.hexdigest()


def GetAllIpv4Address(networkSegment):
    for name, info in psutil.net_if_addrs().items():
        for addr in info:
            if AddressFamily.AF_INET == addr.family and str(addr.address).startswith(networkSegment):
                return str(addr.address)


def get_file_ext_list(path_dir, ext):
    """
    Gets the files in the directory with the specified suffix.
    :param path_dir:
    :param ext: .exe, .py and so on.
    :return: list
    """
    L = []
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if os.path.splitext(file)[1] == ext:
                L.append(os.path.join(root, file))
    return L


if __name__ == '__main__':
    pass
    # create_csv_file('test.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
    # write_csv_file('test.csv', ['1wqw', '2', '3', '4'])
    # print(str(True))
    # ping('192.168.1.101')
    # ping('127.0.0.1')
    # aa = restart_process('EXCEL.EXE')
    # logger.debug(f"ds{aa}")
    # register("demon", "1@1.com")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {})
    # register("demon", "1@1.com",
    #          addr="shanghai")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {'addr': 'shanghai'})
