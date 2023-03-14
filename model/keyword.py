#!/usr/bin/env python
# coding: utf-8
"""
@File   : keyword.py
@Author : Steven.Shen
@Date   : 2021/11/9
@Desc   : 
"""
import os
import re
import nidaqmx
from PyQt5 import QtCore
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtWidgets import QAction, QMessageBox
import ui.mainform
import peak.peaklin
from sockets.serialport import SerialPort
from sockets.telnet import TelnetComm
import conf.globalvar as gv
import time
from sockets.visa import VisaComm
from .basicfunc import IsNullOrEmpty, kill_process, start_process, restart_process, run_cmd, ping
from inspect import currentframe


def testKeyword(test_case, item, testSuite):
    # gv.lg.logger.debug(f'isTest:{item.isTest},testName:{item.StepName}')
    time.sleep(0.3)
    # return True, ''
    rReturn = False
    compInfo = ''
    # gv.main_form.testSequences[item.suite_index].globalVar = item.globalVar
    if gv.cf.dut.test_mode == 'debug' or gv.IsDebug and item.Keyword in gv.cf.dut.debug_skip:
        item.logger.debug('This is debug mode.Skip this step.')
        return True, ''

    try:

        if item.Keyword == 'Waiting':
            item.logger.debug(f'waiting {item.Timeout}s')
            time.sleep(float(item.Timeout))
            rReturn = True

        elif item.Keyword == 'SetVar':
            item.testValue = item.command
            rReturn = True
            time.sleep(0.1)

        elif item.Keyword == 'MessageBoxShow':
            invoke_return = QMetaObject.invokeMethod(
                ui.mainform.MainForm.main_form,
                'showMessageBox',
                Qt.BlockingQueuedConnection,
                QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
                QtCore.Q_ARG(str, item.expectStr),
                QtCore.Q_ARG(str, item.command),
                QtCore.Q_ARG(int, 2))
            if invoke_return == QMessageBox.Yes or invoke_return == QMessageBox.Ok:
                rReturn = True
            else:
                rReturn = False

        elif item.Keyword == 'QInputDialog':
            invoke_return = QMetaObject.invokeMethod(
                ui.mainform.MainForm.main_form,
                'showQInputDialog',
                Qt.BlockingQueuedConnection,
                QtCore.Q_RETURN_ARG(list),
                QtCore.Q_ARG(str, item.expectStr),
                QtCore.Q_ARG(str, item.command))
            item.logger.debug(f'dialog input:{invoke_return[0]}')
            if not invoke_return[1]:
                rReturn = False
            else:
                rReturn = True

        elif item.Keyword == 'AppS19Info':
            file_path = f"{gv.current_dir}\\flash\\{item.command}"
            item.testValue = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(file_path)))
            rReturn = True

        elif item.Keyword == 'StartFor':
            return True, ''

        elif item.Keyword == 'KillProcess':
            rReturn = kill_process(item.logger, item.command)

        elif item.Keyword == 'StartProcess':
            rReturn = start_process(item.logger, item.command, item.expectStr)

        elif item.Keyword == 'RestartProcess':
            rReturn = restart_process(item.logger, item.command, item.expectStr)

        elif item.Keyword == 'PingDUT':
            run_cmd(item.logger, 'arp -d')
            rReturn = ping(item.logger, item.command)

        elif item.Keyword == 'TelnetLogin':
            if not isinstance(test_case.dut_comm, TelnetComm):
                test_case.dut_comm = TelnetComm(item.logger, gv.cf.dut.dut_ip, gv.cf.dut.prompt)
            rReturn = test_case.dut_comm.open(gv.cf.dut.prompt)

        elif item.Keyword == 'TelnetAndSendCmd':
            temp = TelnetComm(item.logger, item.Param1, gv.cf.dut.prompt)
            if temp.open(gv.cf.dut.prompt) and \
                    temp.SendCommand(item.command, item.expectStr, item.Timeout)[0]:
                return True, ''

        elif item.Keyword == 'SerialPortOpen':
            if not isinstance(test_case.dut_comm, SerialPort):
                if not IsNullOrEmpty(item.command):
                    test_case.dut_comm = SerialPort(item.logger, item.command, int(item.expectStr))
            rReturn = test_case.dut_comm.open()

        elif item.Keyword == 'CloseDUTCOMM':
            if test_case.dut_comm is not None:
                test_case.dut_comm.close()
                rReturn = True

        elif item.Keyword == 'PLINInitConnect':
            rReturn = plin_init_connect(rReturn, item.logger)

        elif item.Keyword == 'PLINInitConnectELV':
            rReturn = plin_init_connectELV(rReturn, item.logger)

        elif item.Keyword == 'PLINDisConnect':
            rReturn = gv.PLin.DoLinDisconnect()
            ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
                True, "Not connected | ")

        elif item.Keyword == 'PLINSingleFrame':
            rReturn, revStr = gv.PLin.SingleFrame(item.ID, item.NAD_, item.PCI_LEN_, item.command, item.Timeout)
            if rReturn and item.checkStr1 in revStr:
                item.testValue = subStr(item.subStr1, item.subStr2, revStr, item)
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'PLINSingleFrameCF':
            rReturn, revStr = gv.PLin.SingleFrameCF(item.ID, item.NAD_, item.PCI_LEN_, item.command, item.Timeout)
            if rReturn and item.checkStr1 in revStr:
                item.testValue = subStr(item.subStr1, item.subStr2, revStr, item)
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'PLINGetMsg32':
            gv.pMsg32 = gv.PLin.plin_Get_pMsg(item.ID, item.command)
            rReturn = True
        elif item.Keyword == 'PLINGetMsg33':
            gv.pMsg33 = gv.PLin.plin_Get_pMsg(item.ID, item.command)
            rReturn = True

        elif item.Keyword == 'WaitingALE' or item.Keyword == 'PLINWriteALE':
            # gv.PLin.plin_writeALE(gv.pMsg32, gv.pMsg33, int(item.Timeout), True if item.retry == 1 else False)
            gv.PLin.plin_writeALE(gv.pMsg32, gv.pMsg33, item.Timeout)
            rReturn = True

        elif item.Keyword == 'PLINMultiFrame':
            rReturn, revStr = gv.PLin.MultiFrame(item.ID, item.NAD_, item.PCI_LEN_, item.command, item.Timeout)
            if rReturn and item.checkStr1 in revStr:
                item.testValue = subStr(item.subStr1, item.subStr2, revStr, item)

        elif item.Keyword == 'TransferData':
            file_path = f"{gv.current_dir}\\flash\\{item.command}"
            s19datas = gv.PLin.get_datas(file_path)
            item.logger.debug(file_path)
            rReturn = gv.PLin.TransferData(item.ID, item.NAD_, s19datas, item.PCI_LEN_, item.Timeout)

        elif item.Keyword == 'SuspendDiagSchedule':
            rReturn = gv.PLin.SuspendDiagSchedule()

        elif item.Keyword == 'CalcKey':
            item.testValue = gv.PLin.CalKey(item.command)
            item.logger.debug(f"send key is {item.testValue}.")
            rReturn = True

        elif item.Keyword == 'GetCRC':
            item.testValue = peak.peaklin.PeakLin.get_crc_apps19(item.logger,
                                                                 f"{gv.current_dir}\\flash\\{gv.cf.station.station_name}")
            rReturn = not IsNullOrEmpty(item.testValue)

        elif item.Keyword == 'SrecGetStartAdd':
            rReturn, revStr = run_cmd(item.logger,
                                      rf"{gv.current_dir}\tool\srec_info.exe {gv.current_dir}\flash\{gv.cf.station.station_name}\{item.command}")
            if rReturn:
                item.testValue = ' '.join(re.findall(".{2}", revStr.split()[-3].zfill(8)))
            else:
                pass

        elif item.Keyword == 'SrecGetLen':
            rReturn, revStr = run_cmd(item.logger,
                                      rf"{gv.current_dir}\tool\srec_info.exe {gv.current_dir}\flash\{gv.cf.station.station_name}\{item.command}")
            if rReturn:
                data_len = int(revStr.split()[-1], 16) - int(revStr.split()[-3], 16) + 1
                item.testValue = ' '.join(re.findall(".{2}", hex(data_len)[2:].upper().zfill(8)))
            else:
                pass

        elif item.Keyword == 'NiDAQmxVolt':
            # https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Pf1SAE&l=zh-CN
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(item.command, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                item.logger.debug(f"get {item.command} sensor Volt: {data}.")
                item.testValue = "%.2f" % ((data[0] - 0.02) * 10)
                item.logger.debug(f"DAQmx {item.command} Volt: {item.testValue}.")
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'NiDAQmxCur':
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(item.command, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                item.logger.debug(f"get {item.command} sensor Volt: {data}.")
                item.testValue = "%.2f" % ((data[0] - 0.02) * 2)
                item.logger.debug(f"DAQmx {item.command} Current: {item.testValue}.")
            compInfo, rReturn = assert_value(compInfo, item, rReturn)

        elif item.Keyword == 'NiVisaCmd':
            rReturn, revStr = test_case.NiInstrComm.SendCommand(item.command, item.expectStr, item.Timeout)
            item.logger.debug(f'{rReturn},{item.checkStr1},{revStr}')
            if rReturn and item.checkStr1 in revStr:
                if not IsNullOrEmpty(item.subStr1) or not IsNullOrEmpty(item.subStr2):
                    item.testValue = subStr(item.subStr1, item.subStr2, revStr, item)
                elif str_to_int(item.param1)[0]:
                    item.testValue = "%.2f" % float(revStr.split(',')[str_to_int(item.param1)[1] - 1])
                else:
                    return True, ''
                compInfo, rReturn = assert_value(compInfo, item, rReturn)
            else:
                rReturn = False

        elif item.Keyword == 'NiVisaOpenInstr':
            test_case.NiInstrComm = VisaComm(item.logger)
            rReturn = test_case.NiInstrComm.open(item.command)

        else:
            rReturn, revStr = test_case.dut_comm.SendCommand(item.command, item.expectStr, item.Timeout)
            if rReturn and item.checkStr1 in revStr and item.checkStr2 in revStr:
                if not IsNullOrEmpty(item.subStr1) or not IsNullOrEmpty(item.subStr2):
                    item.testValue = subStr(item.subStr1, item.subStr2, revStr, item)
                    compInfo, rReturn = assert_value(compInfo, item, rReturn)
                else:
                    return True, ''
            else:
                rReturn = False
    except Exception as e:
        raise e
    else:
        return rReturn, compInfo
    finally:
        if (item.StepName.startswith("GetDAQResistor") or
                item.StepName.startswith("GetDAQTemp") or
                item.Keyword == "NiDAQmxVolt" or
                item.Keyword == "NiDAQmxCur"):
            test_case.ArrayListDaq.append("N/A" if IsNullOrEmpty(item.testValue) else item.testValue)
            test_case.ArrayListDaqHeader.append(item.StepName)
            item.logger.debug(f"DQA add {item.testValue}")


def CompareLimit(limitMin, limitMax, value, item, is_round=False):
    if IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):
        return True, ''
    if IsNullOrEmpty(value):
        return False, ''
    temp = round(float(value)) if is_round else float(value)
    if IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 只需比较最大值
        item.logger.debug("compare Limit_max...")
        return temp <= float(limitMax), ''
    if not IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):  # 只需比较最小值
        item.logger.debug("compare Limit_min...")
        return temp >= float(limitMin), ''
    if not IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 比较最小最大值
        item.logger.debug("compare Limit_min and Limit_max...")
        if float(limitMin) <= temp <= float(limitMax):
            return True, ''
        else:
            if temp < float(limitMin):
                return False, 'TooLow'
            else:
                return False, 'TooHigh'


def register(name, email, **kwargs):
    print('test_name:%s, age:%s, others:%s', (name, email, kwargs))


def subStr(SubStr1, SubStr2, revStr, item):
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
        item.logger.debug(f'get TestValue:{testValue}')
        return testValue.strip()
    else:
        raise Exception(f'get TestValue exception:{values}')


def assert_value(compInfo, item, rReturn):
    if not IsNullOrEmpty(item.spec):
        try:
            rReturn = True if item.testValue in item.spec else False
        except TypeError as e:
            item.logger.error(f'{currentframe().f_code.co_name}:{e}')
    elif not IsNullOrEmpty(item.USL) or not IsNullOrEmpty(item.LSL):
        try:
            rReturn, compInfo = CompareLimit(item.LSL, item.USL, item.testValue, item)
        except TypeError as e:
            item.logger.error(f'{currentframe().f_code.co_name}:{e}')
    elif IsNullOrEmpty(item.USL) and IsNullOrEmpty(item.LSL):
        pass
    else:
        item.logger.warning(f"assert is unknown,SPEC:{item.spec},LSL:{item.LSL}USL:{item.USL}.")
    return compInfo, rReturn


def str_to_int(strs):
    try:
        num = int(strs)
        return True, num
    except:
        return False, 0


def plin_init_connect(rReturn, logger):
    if gv.PLin is None:
        gv.PLin = peak.peaklin.PeakLin(logger)
        ui.mainform.MainForm.main_form.my_signals.controlEnableSignal[QAction, bool].emit(
            ui.mainform.MainForm.main_form.ui.actionPeakLin, False)
        gv.PLin.refreshHardware()
        gv.PLin.hardwareCbx_IndexChanged()
        if gv.PLin.doLinConnect():
            time.sleep(0.1)
            rReturn = gv.PLin.runScheduleDiag()
            time.sleep(0.1)
        else:
            gv.PLin = None
            return rReturn
    else:
        time.sleep(0.1)
        rReturn = gv.PLin.runScheduleDiag()
        time.sleep(0.1)
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn


def plin_init_connectELV(rReturn, logger):
    if gv.PLin is None:
        gv.PLin = peak.peaklin.PeakLin(logger)
        ui.mainform.MainForm.main_form.my_signals.controlEnableSignal[QAction, bool].emit(
            ui.mainform.MainForm.main_form.ui.actionPeakLin, False)
        gv.PLin.refreshHardware()
        gv.PLin.hardwareCbx_IndexChanged()
        if gv.PLin.doLinConnect():
            time.sleep(0.1)
            rReturn = gv.PLin.runSchedule()
            time.sleep(0.1)
            rReturn = True
        else:
            gv.PLin = None
            return rReturn
    else:
        time.sleep(0.1)
        rReturn = gv.PLin.runSchedule()
        time.sleep(0.1)
        rReturn = True
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn


if __name__ == "__main__":
    pass
