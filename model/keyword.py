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


def testKeyword(test_case, step):
    # time.sleep(0.3)
    # return True, ''
    rReturn = False
    compInfo = ''
    try:
        if gv.cf.dut.test_mode == 'debug' or gv.IsDebug and step.Keyword in gv.cf.dut.debug_skip:
            step.logger.debug('This is debug mode.Skip this step.')
            rReturn = True

        elif step.Keyword == 'Waiting':
            step.logger.debug(f'waiting {step.Timeout}s')
            time.sleep(float(step.Timeout))
            rReturn = True

        elif step.Keyword == 'SetVar':
            step.testValue = step.command
            rReturn = True
            time.sleep(0.1)

        elif step.Keyword == 'MessageBoxShow':
            invoke_return = QMetaObject.invokeMethod(
                ui.mainform.MainForm.main_form,
                'showMessageBox',
                Qt.BlockingQueuedConnection,
                QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
                QtCore.Q_ARG(str, step.expectStr),
                QtCore.Q_ARG(str, step.command),
                QtCore.Q_ARG(int, 2))
            if invoke_return == QMessageBox.Yes or invoke_return == QMessageBox.Ok:
                rReturn = True
            else:
                rReturn = False

        elif step.Keyword == 'QInputDialog':
            invoke_return = QMetaObject.invokeMethod(
                ui.mainform.MainForm.main_form,
                'showQInputDialog',
                Qt.BlockingQueuedConnection,
                QtCore.Q_RETURN_ARG(list),
                QtCore.Q_ARG(str, step.expectStr),
                QtCore.Q_ARG(str, step.command))
            if not invoke_return[1]:
                rReturn = False
            else:
                step.logger.debug(f'dialog input:{invoke_return[0]}')
                rReturn = True

        elif step.Keyword == 'AppS19Info':
            file_path = rf"{gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}\{step.command}"
            step.testValue = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(file_path)))
            rReturn = True

        elif step.Keyword == 'StartFor':
            return True, ''

        elif step.Keyword == 'KillProcess':
            rReturn = kill_process(step.logger, step.command)

        elif step.Keyword == 'StartProcess':
            rReturn = start_process(step.logger, step.command, step.expectStr)

        elif step.Keyword == 'RestartProcess':
            rReturn = restart_process(step.logger, step.command, step.expectStr)

        elif step.Keyword == 'PingDUT':
            run_cmd(step.logger, 'arp -d')
            rReturn = ping(step.logger, step.command)

        elif step.Keyword == 'TelnetLogin':
            if not isinstance(test_case.dut_comm, TelnetComm):
                if not IsNullOrEmpty(step.command):
                    test_case.dut_comm = TelnetComm(step.logger, step.command, gv.cf.dut.prompt)
                else:
                    test_case.dut_comm = TelnetComm(step.logger, gv.cf.dut.dut_ip, gv.cf.dut.prompt)
            rReturn = test_case.dut_comm.open(gv.cf.dut.prompt)

        elif step.Keyword == 'TelnetAndSendCmd':
            temp = TelnetComm(step.logger, step.Param1, gv.cf.dut.prompt)
            if temp.open(gv.cf.dut.prompt) and \
                    temp.SendCommand(step.command, step.expectStr, step.Timeout)[0]:
                return True, ''

        elif step.Keyword == 'SerialPortOpen':
            if not isinstance(test_case.dut_comm, SerialPort):
                if not IsNullOrEmpty(step.command):
                    test_case.dut_comm = SerialPort(step.logger, step.command, int(step.expectStr))
            rReturn = test_case.dut_comm.open()

        elif step.Keyword == 'CloseDUTCOMM':
            if test_case.dut_comm is not None:
                test_case.dut_comm.close()
                rReturn = True

        elif step.Keyword == 'PLINInitConnect':
            rReturn = peakLin_init_connect(rReturn, step.logger)

        elif step.Keyword == 'PLINInitConnectELV':
            rReturn = peakLin_init_connectELV(rReturn, step.logger)

        elif step.Keyword == 'PLINDisConnect':
            rReturn = gv.PLin.DoLinDisconnect()
            ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
                True, "Not connected | ")

        elif step.Keyword == 'PLINSingleFrame':
            rReturn, revStr = gv.PLin.SingleFrame(step.ID, step.NAD_, step.PCI_LEN_, step.command, step.Timeout)
            if rReturn and step.checkStr1 in revStr:
                step.testValue = subStr(step.subStr1, step.subStr2, revStr, step)
            compInfo, rReturn = assert_value(compInfo, step, rReturn)

        elif step.Keyword == 'PLINSingleFrameCF':
            rReturn, revStr = gv.PLin.SingleFrameCF(step.ID, step.NAD_, step.PCI_LEN_, step.command, step.Timeout)
            if rReturn and step.checkStr1 in revStr:
                step.testValue = subStr(step.subStr1, step.subStr2, revStr, step)
            compInfo, rReturn = assert_value(compInfo, step, rReturn)

        elif step.Keyword == 'PLINGetMsg32':
            gv.pMsg32 = gv.PLin.peakLin_Get_pMsg(step.ID, step.command)
            rReturn = True
        elif step.Keyword == 'PLINGetMsg33':
            gv.pMsg33 = gv.PLin.peakLin_Get_pMsg(step.ID, step.command)
            rReturn = True

        elif step.Keyword == 'WaitingALE' or step.Keyword == 'PLINWriteALE':
            # gv.PLin.plin_writeALE(gv.pMsg32, gv.pMsg33, int(item.Timeout), True if item.retry == 1 else False)
            gv.PLin.peakLin_writeALE(gv.pMsg32, gv.pMsg33, step.Timeout)
            rReturn = True

        elif step.Keyword == 'PLINMultiFrame':
            rReturn, revStr = gv.PLin.MultiFrame(step.ID, step.NAD_, step.PCI_LEN_, step.command, step.Timeout)
            if rReturn and step.checkStr1 in revStr:
                step.testValue = subStr(step.subStr1, step.subStr2, revStr, step)

        elif step.Keyword == 'TransferData':
            path = rf"{gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}\{step.command}"
            s19datas = gv.PLin.get_datas(path)
            step.logger.debug(path)
            rReturn = gv.PLin.TransferData(step.ID, step.NAD_, s19datas, step.PCI_LEN_, step.Timeout)

        elif step.Keyword == 'SuspendDiagSchedule':
            rReturn = gv.PLin.SuspendDiagSchedule()

        elif step.Keyword == 'CalcKey':
            step.testValue = gv.PLin.CalKey(step.command)
            step.logger.debug(f"send key is {step.testValue}.")
            rReturn = True

        elif step.Keyword == 'GetCRC':
            path = rf"{gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}"
            step.testValue = peak.peaklin.PeakLin.get_crc_apps19(step.logger, path)
            rReturn = not IsNullOrEmpty(step.testValue)

        elif step.Keyword == 'SrecGetStartAdd':
            cmd = rf"{gv.current_dir}\tool\srec_info.exe {gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}\{step.command}"
            rReturn, revStr = run_cmd(step.logger, cmd)

            if rReturn:
                step.testValue = ' '.join(re.findall(".{2}", revStr.split()[-3].zfill(8)))
            else:
                pass

        elif step.Keyword == 'SrecGetLen':
            cmd = rf"{gv.current_dir}\tool\srec_info.exe {gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}\{step.command}"
            rReturn, revStr = run_cmd(step.logger, cmd)
            if rReturn:
                data_len = int(revStr.split()[-1], 16) - int(revStr.split()[-3], 16) + 1
                step.testValue = ' '.join(re.findall(".{2}", hex(data_len)[2:].upper().zfill(8)))
            else:
                pass

        elif step.Keyword == 'NiDAQmxVolt':
            # https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Pf1SAE&l=zh-CN
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(step.command, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                step.logger.debug(f"get {step.command} sensor Volt: {data}.")
                step.testValue = "%.2f" % ((data[0] - 0.02) * 10)
                step.logger.debug(f"DAQmx {step.command} Volt: {step.testValue}.")
            compInfo, rReturn = assert_value(compInfo, step, rReturn)

        elif step.Keyword == 'NiDAQmxCur':
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(step.command, min_val=-10, max_val=10)
                data = task.read(number_of_samples_per_channel=1)
                step.logger.debug(f"get {step.command} sensor Volt: {data}.")
                step.testValue = "%.2f" % ((data[0] - 0.02) * 2)
                step.logger.debug(f"DAQmx {step.command} Current: {step.testValue}.")
            compInfo, rReturn = assert_value(compInfo, step, rReturn)

        elif step.Keyword == 'NiVisaCmd':
            rReturn, revStr = test_case.NiInstrComm.SendCommand(step.command, step.expectStr, step.Timeout)
            step.logger.debug(f'{rReturn},{step.checkStr1},{revStr}')
            if rReturn and step.checkStr1 in revStr:
                if not IsNullOrEmpty(step.subStr1) or not IsNullOrEmpty(step.subStr2):
                    step.testValue = subStr(step.subStr1, step.subStr2, revStr, step)
                elif str_to_int(step.param1)[0]:
                    step.testValue = "%.2f" % float(revStr.split(',')[str_to_int(step.param1)[1] - 1])
                else:
                    return True, ''
                compInfo, rReturn = assert_value(compInfo, step, rReturn)
            else:
                rReturn = False

        elif step.Keyword == 'NiVisaOpenInstr':
            test_case.NiInstrComm = VisaComm(step.logger)
            rReturn = test_case.NiInstrComm.open(step.command)

        else:
            rReturn, revStr = test_case.dut_comm.SendCommand(step.command, step.expectStr, step.Timeout)
            if rReturn and step.checkStr1 in revStr and step.checkStr2 in revStr:
                if not IsNullOrEmpty(step.subStr1) or not IsNullOrEmpty(step.subStr2):
                    step.testValue = subStr(step.subStr1, step.subStr2, revStr, step)
                    compInfo, rReturn = assert_value(compInfo, step, rReturn)
                else:
                    return True, ''
            else:
                rReturn = False
    except Exception as e:
        raise e
    else:
        return rReturn, compInfo
    finally:
        if (step.StepName.startswith("GetDAQResistor") or step.StepName.startswith("GetDAQTemp") or
                step.Keyword == "NiDAQmxVolt" or step.Keyword == "NiDAQmxCur"):
            test_case.ArrayListDaq.append("N/A" if IsNullOrEmpty(step.testValue) else step.testValue)
            test_case.ArrayListDaqHeader.append(step.StepName)
            step.logger.debug(f"DQA add {step.testValue}")


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


def peakLin_init_connect(rReturn, logger):
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


def peakLin_init_connectELV(rReturn, logger):
    if gv.PLin is None:
        gv.PLin = peak.peaklin.PeakLin(logger)
        ui.mainform.MainForm.main_form.my_signals.controlEnableSignal[QAction, bool].emit(
            ui.mainform.MainForm.main_form.ui.actionPeakLin, False)
        gv.PLin.refreshHardware()
        gv.PLin.hardwareCbx_IndexChanged()
        if gv.PLin.doLinConnect():
            time.sleep(0.1)
            gv.PLin.runSchedule()
            time.sleep(0.1)
            rReturn = True
        else:
            gv.PLin = None
            return rReturn
    else:
        time.sleep(0.1)
        gv.PLin.runSchedule()
        time.sleep(0.1)
        rReturn = True
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn


if __name__ == "__main__":
    pass
