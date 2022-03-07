#!/usr/bin/env python
# coding: utf-8
"""
@File   : keyword.py
@Author : Steven.Shen
@Date   : 2021/11/9
@Desc   : 
"""
import re
import time
from sockets.serialport import SerialPort
from sockets.telnet import TelnetComm
import conf.globalvar as gv
import conf.logprint as lg
import csv
import json
import os
import subprocess
import time
import platform
import psutil
from datetime import datetime
import yaml
# import conf.logprint as lg
from .basicfunc import IsNullOrEmpty


def CompareLimit(limitMin, limitMax, value, is_round=False):
    if IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):
        return True, ''
    if IsNullOrEmpty(value):
        return False, ''
    temp = round(float(value)) if is_round else float(value)
    if IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 只需比较最大值
        lg.logger.debug("Compare Limit_max...")
        return temp <= float(limitMax), ''
    if not IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):  # 只需比较最小值
        lg.logger.debug("Compare Limit_min...")
        return temp >= float(limitMin), ''
    if not IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 比较最小最大值
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


# import model.step
# def test(item: model.step.Step):
def test(item, testSuite):
    time.sleep(0.5)
    # invoke_return = QMetaObject.invokeMethod(
    #     ui.mainform.MainForm.main_form,
    #     'showMessageBox',
    #     Qt.BlockingQueuedConnection,
    #     QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
    #     QtCore.Q_ARG(str, 'ERROR!'),
    #     QtCore.Q_ARG(str, 'Text to msgBox'),
    #     QtCore.Q_ARG(int, 2))
    # lg.logger.debug(f"invoke_return:{invoke_return}")
    # if invoke_return == QMessageBox.Yes or invoke_return == QMessageBox.Ok:
    #     lg.logger.debug("yes ok")
    # else:
    #     lg.logger.debug('no')

    lg.logger.debug(f'isTest:{item.isTest},testName:{item.StepName}')
    return True, ''
    rReturn = False
    compInfo = ''
    # gv.main_form.testSequences[item.suite_index].globalVar = item.globalVar
    try:
        if item.TestKeyword == 'Sleep':
            lg.logger.debug(f'sleep {item.TimeOut}s')
            time.sleep(item.TimeOut)
            rReturn = True

        elif item.TestKeyword == 'KillProcess':
            rReturn = kill_process(item.ComdOrParam)

        elif item.TestKeyword == 'StartProcess':
            rReturn = start_process(item.ComdOrParam, item.ExpectStr)

        elif item.TestKeyword == 'RestartProcess':
            rReturn = restart_process(item.ComdOrParam, item.ExpectStr)

        elif item.TestKeyword == 'PingDUT':
            run_cmd('arp -d')
            rReturn = ping(item.ComdOrParam)

        elif item.TestKeyword == 'TelnetLogin':
            if gv.dut_comm is None:
                gv.dut_comm = TelnetComm(gv.dut_ip, gv.cf.station.prompt)
            rReturn = gv.dut_comm.open(gv.cf.station.prompt)

        elif item.TestKeyword == 'TelnetAndSendCmd':
            temp = TelnetComm(item.param1, gv.cf.station.prompt)
            if temp.open(gv.cf.station.prompt) and \
                    temp.SendCommand(item.ComdOrParam, item.ExpectStr, item.TimeOut)[0]:
                return True

        elif item.TestKeyword == 'SerialPortOpen':
            if gv.dut_comm is None:
                if not IsNullOrEmpty(item.ComdOrParam):
                    gv.dut_comm = SerialPort(item.ComdOrParam, int(item.ExpectStr))
            rReturn = gv.dut_comm.open()

        elif item.TestKeyword == 'CloseDUTCOMM':
            if gv.dut_comm is not None:
                gv.dut_comm.close()
                rReturn = True
        else:
            lg.logger.debug('run test step')
            pass
            rReturn, revStr = gv.dut_comm.SendCommand(item.ComdOrParam, item.ExpectStr, item.TimeOut)
            if rReturn:
                if re.search(item.CheckStr1, revStr) and re.search(item.CheckStr2, revStr):
                    rReturn = True

                    if not IsNullOrEmpty(item.SubStr1) or not IsNullOrEmpty(item.SubStr2):
                        values = re.findall(f'{item.SubStr1}(.*?){item.SubStr2}', revStr)
                        if len(values) == 1:
                            item.testValue = values[0]
                            lg.logger.debug(f'get TestValue:{item.testValue}')
                        else:
                            raise Exception(f'get TestValue exception:{values}')

                        if not IsNullOrEmpty(item.Spec):
                            rReturn = True if item.testValue in item.Spec else False
                        if not IsNullOrEmpty(item.Limit_min) or not IsNullOrEmpty(
                                item.Limit_max):
                            rReturn, compInfo = CompareLimit(item.Limit_min, item.Limit_max,
                                                             item.testValue)
                else:
                    rReturn = False
            else:
                pass

    except Exception as e:
        lg.logger.exception(f"test Exception！！{e}")
        rReturn = False
        return rReturn, compInfo
    else:
        return rReturn, compInfo
    finally:
        # item.set_errorCode_details(rReturn, item.ErrorCode.split('\n')[0])
        pass


if __name__ == "__main__":
    pass
