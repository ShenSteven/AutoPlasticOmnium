#!/usr/bin/env python
# coding: utf-8
"""
@File   : restart.py
@Author : Steven.Shen
@Date   : 9/13/2023
@Desc   : 
"""

import argparse
import subprocess
import sys
import time
import platform
import psutil

win = platform.system() == 'Windows'
linux = platform.system() == 'Linux'


def process_exists(process_name):
    pids = psutil.pids()
    ps = [psutil.Process(pid) for pid in pids]
    process_names = [p.name for p in ps]
    if process_name in process_names:
        return True
    else:
        return False


def kill_process(process_name, killall=True):
    try:
        for pid in psutil.pids():
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                if p.name() == process_name:
                    p.kill()
                    # logger.debug(f"kill pid-{pid},test_name-{p.name()}")
                    time.sleep(1)
                    if not killall:
                        break
        return True
    except Exception as e:
        # logger.fatal(e)
        raise e


def run_cmd(command, timeout=1):
    """send command, command executed successfully return true,otherwise false"""
    try:
        IsWind = platform.system() == 'Windows'
        # logger.debug(f'run_cmd-->{command}')
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if IsWind else "utf8"), timeout=timeout)
        if ret.returncode == 0:  # 表示命令下发成功，不对命令内容结果做判断
            # logger.debug(ret.stdout)
            return True, ret.stdout
        else:
            # logger.error(f"error:{ret.stderr}")
            return False, ret.stdout
    except Exception as e:
        # logger.fatal(e)
        raise e


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
        # logger.fatal(e)
        raise e
        # return False


def restart_process(full_path, process_name):
    """kill and start"""
    try:
        if kill_process(process_name):
            return start_process(full_path, process_name)
    except Exception as e:
        # logger.fatal(e)
        raise e
        # return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='restart application')
    parser.add_argument('-n', '--name', action='store_true', help='application process name ')
    parser.add_argument('-p', '--path', action='store_true', help='application exe full path ')
    args = parser.parse_args()
    restart_process(args.path, args.name)
    # restart_process(r'C:\Program Files\Sublime Text\sublime_text.exe', 'sublime_text.exe')
    sys.exit()
