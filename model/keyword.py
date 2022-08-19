#!/usr/bin/env python
# coding: utf-8
"""
@File   : keyword.py
@Author : Steven.Shen
@Date   : 2021/11/9
@Desc   : 
"""
import re
import traceback
import nidaqmx
from PyQt5.QtWidgets import QAction
import ui.mainform
import peak.peaklin
from sockets.serialport import SerialPort
from sockets.telnet import TelnetComm
import conf.globalvar as gv
import conf.logprint as lg
import subprocess
import time
import psutil
from sockets.visa import VisaComm
from .basicfunc import IsNullOrEmpty
from inspect import currentframe


def CompareLimit(limitMin, limitMax, value, is_round=False):
    if IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):
        return True, ''
    if IsNullOrEmpty(value):
        return False, ''
    temp = round(float(value)) if is_round else float(value)
    if IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 只需比较最大值
        lg.logger.debug("compare Limit_max...")
        return temp <= float(limitMax), ''
    if not IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):  # 只需比较最小值
        lg.logger.debug("compare Limit_min...")
        return temp >= float(limitMin), ''
    if not IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 比较最小最大值
        lg.logger.debug("compare Limit_min and Limit_max...")
        if float(limitMin) <= temp <= float(limitMax):
            return True, ''
        else:
            if temp < float(limitMin):
                return False, 'TooLow'
            else:
                return False, 'TooHigh'


def ping(host, timeout=1):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host test_name is valid.
    """
    param = '-n' if gv.win else '-cf'
    command = f'ping {param} 1 {host}'
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if gv.win else "utf8"), timeout=timeout)
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
        lg.logger.fatal(e)
        return False


def run_cmd(command, timeout=1):
    """send command, command executed successfully return true,otherwise false"""
    try:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding=("gbk" if gv.win else "utf8"), timeout=timeout)
        if ret.returncode == 0:  # 表示命令下发成功，不对命令内容结果做判断
            lg.logger.debug(ret.stdout)
            return True
        else:
            lg.logger.error(f"error:{ret.stderr}")
            return False
    except Exception as e:
        lg.logger.fatal(e)
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
        lg.logger.fatal(e)
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
        lg.logger.fatal(e)
        return False


def restart_process(full_path, process_name):
    """kill and start"""
    try:
        if kill_process(process_name):
            return start_process(full_path, process_name)
    except Exception as e:
        lg.logger.fatal(e)
        return False


def register(name, email, **kwargs):
    print('test_name:%s, age:%s, others:%s', (name, email, kwargs))


def subStr(SubStr1, SubStr2, revStr):
    if IsNullOrEmpty(SubStr1) and IsNullOrEmpty(SubStr2):
        return None
    elif IsNullOrEmpty(SubStr1):
        values = re.findall(f'^(.*?){SubStr2}', revStr)
    elif IsNullOrEmpty(SubStr2):
        values = re.findall(f'{SubStr1}(.*?)$', revStr)
    else:
        values = re.findall(f'{SubStr1}(.*?){SubStr2}', revStr)
    if len(values) == 1 and values[0] != '':
        testValue = values[0]
        lg.logger.debug(f'get TestValue:{testValue}')
        return testValue
    else:
        raise Exception(f'get TestValue exception:{values}')


def testKeyword(item, testSuite):
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

    # lg.logger.debug(f'isTest:{item.isTest},testName:{item.StepName}')
    # time.sleep(0.02)
    # return True, ''
    rReturn = False
    compInfo = ''
    # gv.main_form.testSequences[item.suite_index].globalVar = item.globalVar
    if gv.cf.dut.test_mode == 'debug' or gv.IsDebug and item.Keyword in gv.cf.dut.debug_skip:
        lg.logger.debug('This is debug mode.Skip this step.')
        return True, ''

    try:

        if item.Keyword == 'Waiting':
            lg.logger.debug(f'waiting {item.Timeout}s')
            time.sleep(float(item.Timeout))
            rReturn = True

        elif item.Keyword == 'SetVar':
            item.testValue = item.command
            rReturn = True
            time.sleep(0.1)

        elif item.Keyword == 'StartFor':
            return True, ''

        elif item.Keyword == 'KillProcess':
            rReturn = kill_process(item.command)

        elif item.Keyword == 'StartProcess':
            rReturn = start_process(item.command, item.ExpectStr)

        elif item.Keyword == 'RestartProcess':
            rReturn = restart_process(item.command, item.ExpectStr)

        elif item.Keyword == 'PingDUT':
            run_cmd('arp -d')
            rReturn = ping(item.command)

        elif item.Keyword == 'TelnetLogin':
            if not isinstance(gv.dut_comm, TelnetComm):
                gv.dut_comm = TelnetComm(gv.dut_ip, gv.cf.dut.prompt)
            rReturn = gv.dut_comm.open(gv.cf.dut.prompt)

        elif item.Keyword == 'TelnetAndSendCmd':
            temp = TelnetComm(item.param1, gv.cf.dut.prompt)
            if temp.open(gv.cf.dut.prompt) and \
                    temp.SendCommand(item.command, item.ExpectStr, int(item.Timeout))[0]:
                return True, ''

        elif item.Keyword == 'SerialPortOpen':
            if not isinstance(gv.dut_comm, SerialPort):
                if not IsNullOrEmpty(item.command):
                    gv.dut_comm = SerialPort(item.command, int(item.ExpectStr))
            rReturn = gv.dut_comm.open()

        elif item.Keyword == 'CloseDUTCOMM':
            if gv.dut_comm is not None:
                gv.dut_comm.close()
                rReturn = True

        elif item.Keyword == 'PLINInitConnect':
            rReturn = plin_init_connect(rReturn)

        elif item.Keyword == 'PLINDisConnect':
            rReturn = gv.PLin.DoLinDisconnect()
            ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
                True, "Not connected | ")

        elif item.Keyword == 'PLINSingleFrame':
            rReturn, revStr = gv.PLin.SingleFrame(item.ID, item._NAD, item.PCI_LEN, item.command, int(item.Timeout))
            if rReturn and item.CheckStr1 in revStr:
                item.testValue = subStr(item.SubStr1, item.SubStr2, revStr)

        elif item.Keyword == 'PLINMultiFrame':
            rReturn, revStr = gv.PLin.MultiFrame(item.ID, item._NAD, item.PCI_LEN, item.command, int(item.Timeout))
            if rReturn and item.CheckStr1 in revStr:
                item.testValue = subStr(item.SubStr1, item.SubStr2, revStr)

        elif item.Keyword == 'TransferData':
            s19datas = gv.PLin.get_data(f"{gv.current_dir}\\flash\\{item.command}")
            lg.logger.debug(s19datas)
            rReturn = gv.PLin.TransferData(item.ID, item._NAD, s19datas, item._PCI_LEN, int(item.Timeout))

        elif item.Keyword == 'CalcKey':
            item.testValue = gv.PLin.CalKey(item.command)
            lg.logger.debug(f"send key is {item.testValue}.")
            rReturn = True

        elif item.Keyword == 'GetCRC':
            item.testValue = peak.peaklin.PeakLin.get_crc_apps19(
                f"{gv.current_dir}\\flash\\{gv.cf.station.station_name}")
            rReturn = not IsNullOrEmpty(item.testValue)

        elif item.Keyword == 'NiDAQmxVolt':
            # https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Pf1SAE&l=zh-CN
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(item.CmdOrParam, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                lg.logger.debug(f"get {item.CmdOrParam} sensor Volt: {data}.")
                item.testValue = "%.2f" % ((data[0] - 0.02) * 10)
                lg.logger.debug(f"DAQmx {item.CmdOrParam} Volt: {item.testValue}.")
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'NiDAQmxCur':
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(item.CmdOrParam, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                lg.logger.debug(f"get {item.CmdOrParam} sensor Volt: {data}.")
                item.testValue = "%.2f" % ((data[0] - 0.02) * 2)
                lg.logger.debug(f"DAQmx {item.CmdOrParam} Current: {item.testValue}.")
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'NiVisaCmd':
            rReturn, revStr = gv.InstrComm.SendCommand(item.command, item.ExpectStr, int(item.Timeout))
            if rReturn and item.CheckStr1 in revStr:
                if not IsNullOrEmpty(item.SubStr1) or not IsNullOrEmpty(item.SubStr2):
                    item.testValue = subStr(item.SubStr1, item.SubStr2, revStr)
                elif str_to_int(item.CheckStr2)[0]:
                    item.testValue = "%.2f" % float(revStr.split(',')[str_to_int(item.CheckStr2)[1] - 1])
                else:
                    return True, ''
                compInfo, rReturn = assert_value(compInfo, item, rReturn)
            else:
                rReturn = False

        elif item.Keyword == 'NiVisaOpenInstr':
            gv.InstrComm = VisaComm()
            rReturn = gv.InstrComm.open(item.command)

        else:
            rReturn, revStr = gv.dut_comm.SendCommand(item.command, item.ExpectStr, int(item.Timeout))
            if rReturn and item.CheckStr1 in revStr and item.CheckStr2 in revStr:
                if not IsNullOrEmpty(item.SubStr1) or not IsNullOrEmpty(item.SubStr2):
                    item.testValue = subStr(item.SubStr1, item.SubStr2, revStr)
                    compInfo, rReturn = assert_value(compInfo, item, rReturn)
                else:
                    return True, ''
            else:
                rReturn = False
    except Exception as e:
        lg.logger.fatal(f'{currentframe().f_code.co_name}:{e},{traceback.format_exc()}')
        rReturn = False
        return rReturn, compInfo
    else:
        return rReturn, compInfo
    finally:
        if (item.StepName.startswith("GetDAQResistor") or
                item.StepName.startswith("GetDAQTemp") or
                item.Keyword == "NiDAQmxVolt" or
                item.Keyword == "NiDAQmxCur"):
            gv.ArrayListDaq.append("N/A" if IsNullOrEmpty(item.testValue) else item.testValue)
            gv.ArrayListDaqHeader.append(item.StepName)
            lg.logger.debug(f"DQA add {item.testValue}")


def assert_value(compInfo, item, rReturn):
    if not IsNullOrEmpty(item.spec) and IsNullOrEmpty(item.USL) and IsNullOrEmpty(item.LSL):
        rReturn = True if item.testValue in item.Spec else False
    if not IsNullOrEmpty(item.USL) or not IsNullOrEmpty(item.LSL):
        rReturn, compInfo = CompareLimit(item.LSL, item.USL, item.testValue)
    else:
        lg.logger.warning(f"assert is unknown,Spec:{item.spec},LSL:{item.LSL}USL:{item.USL}.")
    return compInfo, rReturn


def plin_init_connect(rReturn):
    if gv.PLin is None:
        gv.PLin = peak.peaklin.PeakLin()
        ui.mainform.MainForm.main_form.my_signals.controlEnableSignal[QAction, bool].emit(
            ui.mainform.MainForm.main_form.ui.actionPeakLin, False)
        gv.PLin.refreshHardware()
        gv.PLin.hardwareCbx_IndexChanged()
        if gv.PLin.doLinConnect():
            time.sleep(0.1)
            rReturn = gv.PLin.runSchedule()
            time.sleep(0.1)
    else:
        time.sleep(0.1)
        rReturn = gv.PLin.runSchedule()
        time.sleep(0.1)
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn


def str_to_int(strs):
    try:
        num = int(strs)
        return True, num
    except:
        return False, 0


if __name__ == "__main__":
    pass
