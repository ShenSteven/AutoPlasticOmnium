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
import peak.plin.peaklin
from model import value_dispatch
from sockets.serialport import SerialPort
from sockets.telnet import TelnetComm
import conf.globalvar as gv
import time
from sockets.visa import VisaComm
from .basicfunc import IsNullOrEmpty, kill_process, start_process, restart_process, run_cmd, ping, str_to_int, subStr, \
    assert_value


@value_dispatch.value_dispatch
def testKeyword(kw, step, test_case):
    rReturn = False
    compInfo = ''
    try:
        return rReturn, compInfo
    except NameError:
        step.logger.fatal(f'the keyword {kw} is not exist!!!')


@testKeyword.register('Waiting')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.logger.debug(f'waiting {step.Timeout}s')
    time.sleep(float(step.Timeout))
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('StartFor')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('SetVar')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.testValue = step.CmdOrParam
    rReturn = True
    time.sleep(0.1)
    return rReturn, compInfo


@testKeyword.register('MessageBoxShow')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    invoke_return = QMetaObject.invokeMethod(
        ui.mainform.MainForm.main_form,
        'showMessageBox',
        Qt.BlockingQueuedConnection,
        QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
        QtCore.Q_ARG(str, step.ExpectStr),
        QtCore.Q_ARG(str, step.CmdOrParam),
        QtCore.Q_ARG(int, 2))
    if invoke_return == QMessageBox.Yes or invoke_return == QMessageBox.Ok:
        rReturn = True
    else:
        rReturn = False
    return rReturn, compInfo


@testKeyword.register('QInputDialog')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    invoke_return = QMetaObject.invokeMethod(
        ui.mainform.MainForm.main_form,
        'showQInputDialog',
        Qt.BlockingQueuedConnection,
        QtCore.Q_RETURN_ARG(list),
        QtCore.Q_ARG(str, step.ExpectStr),
        QtCore.Q_ARG(str, step.CmdOrParam))
    if not invoke_return[1]:
        rReturn = False
    else:
        step.logger.debug(f'dialog input:{invoke_return[0]}')
        rReturn = True
    return rReturn, compInfo


@testKeyword.register('AppS19Info')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    file_path = rf"{gv.current_dir}{os.sep}flash{os.sep}{gv.cf.station.station_name}{os.sep}{step.myWind.dut_model}{os.sep}{step.CmdOrParam}"
    step.testValue = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(file_path)))
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('KillProcess')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = kill_process(step.logger, step.CmdOrParam)
    return rReturn, compInfo


@testKeyword.register('StartProcess')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = start_process(step.logger, step.CmdOrParam, step.ExpectStr)
    return rReturn, compInfo


@testKeyword.register('RestartProcess')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = restart_process(step.logger, step.CmdOrParam, step.ExpectStr)
    return rReturn, compInfo


@testKeyword.register('PingDUT')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    run_cmd(step.logger, 'arp -d')
    rReturn = ping(step.logger, step.CmdOrParam)
    return rReturn, compInfo


@testKeyword.register('TelnetLogin')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    if not isinstance(test_case.dut_comm, TelnetComm):
        if not IsNullOrEmpty(step.CmdOrParam):
            test_case.dut_comm = TelnetComm(step.logger, step.CmdOrParam, gv.cf.dut.prompt)
        else:
            test_case.dut_comm = TelnetComm(step.logger, gv.cf.dut.dut_ip, gv.cf.dut.prompt)
    rReturn = test_case.dut_comm.open(gv.cf.dut.prompt)
    return rReturn, compInfo


@testKeyword.register('TelnetAndSendCmd')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    temp = TelnetComm(step.logger, step.Param1, gv.cf.dut.prompt)
    if temp.open(gv.cf.dut.prompt) and temp.SendCommand(step.CmdOrParam, step.ExpectStr, step.Timeout)[0]:
        rReturn = True
    return rReturn, compInfo


@testKeyword.register('SerialPortOpen')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    if not isinstance(test_case.dut_comm, SerialPort):
        if not IsNullOrEmpty(step.CmdOrParam):
            test_case.dut_comm = SerialPort(step.logger, step.CmdOrParam, int(step.ExpectStr))
    rReturn = test_case.dut_comm.open()
    return rReturn, compInfo


@testKeyword.register('CloseDUTCOMM')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    if test_case.dut_comm is not None:
        test_case.dut_comm.close()
        rReturn = True
        return rReturn, compInfo


@testKeyword.register('PLINInitConnect')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    if gv.PLin is None:
        gv.PLin = peak.plin.peaklin.PeakLin(step.logger)
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
            return rReturn, compInfo
    else:
        time.sleep(0.1)
        rReturn = gv.PLin.runScheduleDiag()
        time.sleep(0.1)
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn, compInfo


@testKeyword.register('PLINInitConnectELV')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    if gv.PLin is None:
        gv.PLin = peak.plin.peaklin.PeakLin(step.logger)
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
            return rReturn, compInfo
    else:
        time.sleep(0.1)
        gv.PLin.runSchedule()
        time.sleep(0.1)
        rReturn = True
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn, compInfo


@testKeyword.register('PLINDisConnect')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = gv.PLin.DoLinDisconnect()
    ui.mainform.MainForm.main_form.my_signals.updateConnectStatusSignal[bool, str].emit(True, "Not connected | ")
    return rReturn, compInfo


@testKeyword.register('PLINSingleFrame')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = gv.PLin.SingleFrame(step.ID, step.NAD, step.PCI_LEN, step.CmdOrParam, step.Timeout)
    if rReturn and step.CheckStr1 in revStr:
        step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
    compInfo, rReturn = assert_value(compInfo, step, rReturn)
    return rReturn, compInfo


@testKeyword.register('PLINSingleFrameCF')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = gv.PLin.SingleFrameCF(step.ID, step.NAD, step.PCI_LEN, step.CmdOrParam, step.Timeout)
    if rReturn and step.CheckStr1 in revStr:
        step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
    compInfo, rReturn = assert_value(compInfo, step, rReturn)
    return rReturn, compInfo


@testKeyword.register('PLINGetMsg32')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    gv.pMsg32 = gv.PLin.peakLin_Get_pMsg(step.ID, step.CmdOrParam)
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('PLINGetMsg33')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    gv.pMsg33 = gv.PLin.peakLin_Get_pMsg(step.ID, step.CmdOrParam)
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('WaitingALE')
@testKeyword.register('PLINWriteALE')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    gv.PLin.peakLin_writeALE(gv.pMsg32, gv.pMsg33, step.Timeout)
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('PLINMultiFrame')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = gv.PLin.MultiFrame(step.ID, step.NAD, step.PCI_LEN, step.CmdOrParam, 5, step.Timeout)
    if rReturn and step.CheckStr1 in revStr:
        step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
    return rReturn, compInfo


@testKeyword.register('TransferData')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    path = rf"{gv.current_dir}{os.sep}flash{os.sep}{gv.cf.station.station_name}{os.sep}{step.myWind.dut_model}{os.sep}{step.CmdOrParam}"
    s19datas = gv.PLin.get_datas(path)
    step.logger.debug(path)
    rReturn = gv.PLin.TransferData(step.ID, step.NAD, s19datas, step.PCI_LEN, step.Timeout)
    return rReturn, compInfo


@testKeyword.register('SuspendDiagSchedule')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = gv.PLin.SuspendDiagSchedule()
    return rReturn, compInfo


@testKeyword.register('CalcKey')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.testValue = gv.PLin.CalKey(step.CmdOrParam)
    step.logger.debug(f"send key is {step.testValue}.")
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('GetCRC')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    path = rf"{gv.current_dir}{os.sep}flash{os.sep}{gv.cf.station.station_name}{os.sep}{step.myWind.dut_model}{os.sep}{step.CmdOrParam}"
    step.testValue = peak.plin.peaklin.PeakLin.get_crc_apps19(step.logger, path)
    rReturn = not IsNullOrEmpty(step.testValue)
    return rReturn, compInfo


@testKeyword.register('SrecGetStartAdd')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    cmd = rf"{gv.current_dir}{os.sep}tool{os.sep}srec_info.exe {gv.current_dir}{os.sep}flash{os.sep}{gv.cf.station.station_name}{os.sep}{step.myWind.dut_model}\{step.CmdOrParam}"
    rReturn, revStr = run_cmd(step.logger, cmd)

    if rReturn:
        step.testValue = ' '.join(re.findall(".{2}", revStr.split()[-3].zfill(8)))
    else:
        pass
    return rReturn, compInfo


@testKeyword.register('SrecGetLen')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    cmd = rf"{gv.current_dir}\tool\srec_info.exe {gv.current_dir}\flash\{gv.cf.station.station_name}\{step.myWind.dut_model}\{step.CmdOrParam}"
    rReturn, revStr = run_cmd(step.logger, cmd)
    if rReturn:
        data_len = int(revStr.split()[-1], 16) - int(revStr.split()[-3], 16) + 1
        step.testValue = ' '.join(re.findall(".{2}", hex(data_len)[2:].upper().zfill(8)))
    else:
        pass
    return rReturn, compInfo


@testKeyword.register('NiDAQmxVolt')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    # https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Pf1SAE&l=zh-CN
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(step.CmdOrParam, min_val=-10, max_val=10)
        data = task.read(number_of_samples_per_channel=1)
        step.logger.debug(f"get {step.CmdOrParam} sensor Volt: {data}.")
        step.testValue = "%.2f" % ((data[0] - 0.02) * 10)
        step.logger.debug(f"DAQmx {step.CmdOrParam} Volt: {step.testValue}.")
    compInfo, rReturn = assert_value(compInfo, step, rReturn)
    return rReturn, compInfo


@testKeyword.register('NiDAQmxCur')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(step.CmdOrParam, min_val=-10, max_val=10)
        data = task.read(number_of_samples_per_channel=1)
        step.logger.debug(f"get {step.CmdOrParam} sensor Volt: {data}.")
        step.testValue = "%.2f" % ((data[0] - 0.02) * 2)
        step.logger.debug(f"DAQmx {step.CmdOrParam} Current: {step.testValue}.")
    compInfo, rReturn = assert_value(compInfo, step, rReturn)
    return rReturn, compInfo


@testKeyword.register('NiVisaCmd')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = test_case.NiInstrComm.SendCommand(step.CmdOrParam, step.ExpectStr, step.Timeout)
    step.logger.debug(f'{rReturn},{step.CheckStr1},{revStr}')
    if rReturn and step.CheckStr1 in revStr:
        if not IsNullOrEmpty(step.SubStr1) or not IsNullOrEmpty(step.SubStr2):
            step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
        elif str_to_int(step.Param1)[0]:
            step.testValue = "%.2f" % float(revStr.split(',')[str_to_int(step.Param1)[1] - 1])
        else:
            return True, ''
        compInfo, rReturn = assert_value(compInfo, step, rReturn)
    else:
        rReturn = False
    return rReturn, compInfo


@testKeyword.register('NiVisaOpenInstr')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    test_case.NiInstrComm = VisaComm(step.logger)
    rReturn = test_case.NiInstrComm.open(step.CmdOrParam)
    return rReturn, compInfo


@testKeyword.register('default')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = test_case.dut_comm.SendCommand(step.CmdOrParam, step.ExpectStr, step.Timeout)
    if rReturn and step.CheckStr1 in revStr and step.CheckStr2 in revStr:
        if not IsNullOrEmpty(step.SubStr1) or not IsNullOrEmpty(step.SubStr2):
            step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
            compInfo, rReturn = assert_value(compInfo, step, rReturn)
        else:
            rReturn = True
    else:
        rReturn = False
    return rReturn, compInfo


# template for new keyword
@testKeyword.register('XXXX')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''

    """ test Keyword action """

    return rReturn, compInfo


if __name__ == "__main__":
    pass
