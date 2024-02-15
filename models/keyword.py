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

import bll.mainform
from common import value_dispatch
from communication.canbus import CanBus
from communication.serialport import SerialPort
from communication.telnet import TelnetComm
import conf.globalvar as gv
import time

from communication.visa import VisaComm
from common.basicfunc import IsNullOrEmpty, kill_process, start_process, restart_process, run_cmd, ping, str_to_int, \
    subStr, assert_value


@value_dispatch.value_dispatch
def testKeyword(kw, step, test_case):
    rReturn = False
    compInfo = ''
    try:
        return rReturn, compInfo
    except NameError:
        step.logger.fatal(f'the keyword {kw} is not exist!!!')


@testKeyword.register('Wait')
@testKeyword.register('Waiting')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.logger.debug(f'wait {step.Timeout}s')
    time.sleep(float(step.Timeout))
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('StartFor')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('VarSet')
@testKeyword.register('SetVar')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.testValue = step.CmdOrParam
    rReturn = True
    time.sleep(0.1)
    return rReturn, compInfo


@testKeyword.register('SetVars')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    step.testValue = step.CmdOrParam
    varList = step.SetGlobalVar.split(',')
    setattr(test_case.myWind.TestVariables, varList[0], step.RxID)
    step.logger.debug(f"setGlobalVar:{varList[0]} = {step.RxID}")
    setattr(test_case.myWind.TestVariables, varList[1], step.GRxID)
    step.logger.debug(f"setGlobalVar:{varList[1]} = {step.GRxID}")
    setattr(test_case.myWind.TestVariables, varList[2], step.TxID)
    step.logger.debug(f"setGlobalVar:{varList[2]} = {step.TxID}")
    rReturn = True
    time.sleep(0.1)
    return rReturn, compInfo


@testKeyword.register('MessageBoxShow')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    invoke_return = QMetaObject.invokeMethod(
        bll.mainform.MainForm.main_form,
        'myShowMessageBox',
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
@testKeyword.register('DialogInput')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    invoke_return = QMetaObject.invokeMethod(
        bll.mainform.MainForm.main_form,
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
    file_path = rf"{gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
    step.testValue = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(file_path)))
    rReturn = True
    return rReturn, compInfo


@testKeyword.register('KillProcess')
@testKeyword.register('ProcessKill')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = kill_process(step.logger, step.CmdOrParam)
    return rReturn, compInfo


@testKeyword.register('StartProcess')
@testKeyword.register('ProcessStart')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = start_process(step.logger, step.CmdOrParam, step.ExpectStr)
    return rReturn, compInfo


@testKeyword.register('RestartProcess')
@testKeyword.register('ProcessRestart')
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
    if not isinstance(test_case.dutComm, TelnetComm):
        if not IsNullOrEmpty(step.CmdOrParam):
            test_case.dutComm = TelnetComm(step.logger, step.CmdOrParam, gv.cfg.dut.prompt)
        else:
            test_case.dutComm = TelnetComm(step.logger, gv.cfg.dut.dutIP, gv.cfg.dut.prompt)
    rReturn = test_case.dutComm.open(gv.cfg.dut.prompt)
    return rReturn, compInfo


@testKeyword.register('TelnetAndSendCmd')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''
    temp = TelnetComm(step.logger, step.Param1, gv.cfg.dut.prompt)
    if temp.open(gv.cfg.dut.prompt) and temp.SendCommand(step.CmdOrParam, step.ExpectStr, step.Timeout)[0]:
        rReturn = True
    return rReturn, compInfo


@testKeyword.register('SerialPortOpen')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    if not isinstance(test_case.dutComm, SerialPort):
        if not IsNullOrEmpty(step.CmdOrParam):
            test_case.dutComm = SerialPort(step.logger, step.CmdOrParam, int(step.ExpectStr))
    rReturn = test_case.dutComm.open()
    return rReturn, compInfo


@testKeyword.register('CloseDUTCOMM')
@testKeyword.register('CloseDUTConnect')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    if test_case.dutComm is not None:
        test_case.dutComm.close()
        rReturn = True
        return rReturn, compInfo


@testKeyword.register('PLINInitConnect')
def _testKeyword_what(kw, step, test_case):
    from communication.peak.plin import peaklin
    rReturn = False
    compInfo = ''
    if gv.PLin is None:
        gv.PLin = peaklin.PeakLin(step.logger,
                                  gv.cfg.BLF.ReqDelay,
                                  gv.cfg.BLF.RespDelay,
                                  gv.cfg.BLF.ReadTxCount,
                                  gv.cfg.BLF.MRtoMRDelay,
                                  gv.cfg.BLF.SchedulePeriod)
        bll.mainform.MainForm.main_form.mySignals.controlEnableSignal[QAction, bool].emit(
            bll.mainform.MainForm.main_form.actionPeakLin, False)
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
    bll.mainform.MainForm.main_form.mySignals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn, compInfo


@testKeyword.register('PLINInitConnectELV')
def _testKeyword_what(kw, step, test_case):
    from communication.peak.plin import peaklin
    rReturn = False
    compInfo = ''
    if gv.PLin is None:
        gv.PLin = peaklin.PeakLin(step.logger,
                                  gv.cfg.BLF.ReqDelay,
                                  gv.cfg.BLF.RespDelay,
                                  gv.cfg.BLF.ReadTxCount,
                                  gv.cfg.BLF.MRtoMRDelay,
                                  gv.cfg.BLF.SchedulePeriod)
        bll.mainform.MainForm.main_form.mySignals.controlEnableSignal[QAction, bool].emit(
            bll.mainform.MainForm.main_form.actionPeakLin, False)
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
    bll.mainform.MainForm.main_form.mySignals.updateConnectStatusSignal[bool, str].emit(
        rReturn,
        f"Connected to PLIN-USB(19200) | HW ID:{gv.PLin.m_hHw.value} | Client:{gv.PLin.m_hClient.value} | ")
    return rReturn, compInfo


@testKeyword.register('PLINDisConnect')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn = gv.PLin.DoLinDisconnect()
    bll.mainform.MainForm.main_form.mySignals.updateConnectStatusSignal[bool, str].emit(True, "Not connected | ")
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
@testKeyword.register('UDSonLINTransferData')
def _testKeyword_what(kw, step, test_case):
    from communication.uds14229 import get_datas
    compInfo = ''
    path = rf"{gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
    s19datas = get_datas(step.logger, path)
    step.logger.debug(path)
    rReturn = gv.PLin.TransferData(step.ID, step.NAD, s19datas, step.PCI_LEN, step.Timeout)
    return rReturn, compInfo


@testKeyword.register('SuspendDiagSchedule')
@testKeyword.register('PLINSuspendDiagSchedule')
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
    # from communication.peak.plin import peaklin
    from communication.uds14229 import get_crc_apps19
    compInfo = ''
    path = rf"{gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
    step.testValue = get_crc_apps19(step.logger, path)
    rReturn = not IsNullOrEmpty(step.testValue)
    return rReturn, compInfo


@testKeyword.register('SrecGetStartAdd')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    cmd = rf"{gv.CurrentDir}{os.sep}tool{os.sep}srec_info.exe {gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
    rReturn, revStr = run_cmd(step.logger, cmd)

    if rReturn:
        step.testValue = ' '.join(re.findall(".{2}", revStr.split()[-3].zfill(8)))
    else:
        pass
    return rReturn, compInfo


@testKeyword.register('SrecGetLen')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    cmd = rf"{gv.CurrentDir}{os.sep}tool{os.sep}srec_info.exe {gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
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


@testKeyword.register('Default')
@testKeyword.register('default')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = test_case.dutComm.SendCommand(step.CmdOrParam, step.ExpectStr, step.Timeout)
    if rReturn and step.CheckStr1 in revStr and step.CheckStr2 in revStr:
        if not IsNullOrEmpty(step.SubStr1) or not IsNullOrEmpty(step.SubStr2):
            step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
            compInfo, rReturn = assert_value(compInfo, step, rReturn)
        else:
            rReturn = True
    else:
        rReturn = False
    return rReturn, compInfo


@testKeyword.register('CANConnect')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''

    if gv.CANBus is None:
        gv.CANBus = CanBus(step.logger, interface=None, channel=None, bitrate=None, appname=None)

    return rReturn, compInfo


@testKeyword.register('UDSonCANSingleFrame')
@testKeyword.register('CANSingleFrame')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = gv.CANBus.uds.SingleFrame(step.RxID, step.GRxID, step.TxID, step.PCI_LEN, step.CmdOrParam,
                                                step.Timeout)
    if rReturn and step.CheckStr1 in revStr:
        step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
    compInfo, rReturn = assert_value(compInfo, step, rReturn)
    return rReturn, compInfo


@testKeyword.register('UDSonCANMultiFrame')
@testKeyword.register('CANMultiFrame')
def _testKeyword_what(kw, step, test_case):
    compInfo = ''
    rReturn, revStr = gv.CANBus.uds.MultiFrame(step.RxID, step.GRxID, step.TxID, step.PCI_LEN, step.CmdOrParam,
                                               step.Timeout)
    if rReturn and step.CheckStr1 in revStr:
        step.testValue = subStr(step.SubStr1, step.SubStr2, revStr, step)
    return rReturn, compInfo


@testKeyword.register('CANTransferData')
@testKeyword.register('UDSonCANTransferData')
def _testKeyword_what(kw, step, test_case):
    from communication.uds14229 import get_datas
    compInfo = ''
    path = rf"{gv.CurrentDir}{os.sep}flash{os.sep}{gv.cfg.station.stationName}{os.sep}{step.myWind.dutModel}{os.sep}{step.CmdOrParam}"
    s19datas = get_datas(step.logger, path)
    step.logger.debug(path)
    rReturn = gv.CANBus.uds.TransferData(step.RxID, step.GRxID, step.TxID, s19datas, step.PCI_LEN, step.Timeout)
    return rReturn, compInfo


# template for new keyword
@testKeyword.register('XXXX')
def _testKeyword_what(kw, step, test_case):
    rReturn = False
    compInfo = ''

    """ test action
     ......
    """

    return rReturn, compInfo


if __name__ == "__main__":
    pass
