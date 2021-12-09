#!/usr/bin/env python
# coding: utf-8
"""
@File   : test.py
@Author : Steven.Shen
@Date   : 2021/11/9
@Desc   : 
"""
import re
import time
from sokets.serialport import SerialPort
from sokets.telnet import TelnetComm
import conf.globalvar as gv
import conf.logconf as lg
import model.basefunc
import model.suite
import ui.mainform
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5 import QtCore


# import model.step
# def test(item: model.step.Step):
def test(item, testSuite):
    time.sleep(0.5)
    # invoke_return = QMetaObject.invokeMethod(
    #     ui.mainform.main_form,
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

    lg.logger.debug(f'isTest:{item.isTest},testName:{item.ItemName}')
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
            rReturn = model.basefunc.kill_process(item.ComdOrParam)

        elif item.TestKeyword == 'StartProcess':
            rReturn = model.basefunc.start_process(item.ComdOrParam, item.ExpectStr)

        elif item.TestKeyword == 'RestartProcess':
            rReturn = model.basefunc.restart_process(item.ComdOrParam, item.ExpectStr)

        elif item.TestKeyword == 'PingDUT':
            model.basefunc.run_cmd('arp -d')
            rReturn = model.basefunc.ping(item.ComdOrParam)

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
                if not model.IsNullOrEmpty(item.ComdOrParam):
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

                    if not model.IsNullOrEmpty(item.SubStr1) or not model.IsNullOrEmpty(item.SubStr2):
                        values = re.findall(f'{item.SubStr1}(.*?){item.SubStr2}', revStr)
                        if len(values) == 1:
                            item.testValue = values[0]
                            lg.logger.debug(f'get TestValue:{item.testValue}')
                        else:
                            raise Exception(f'get TestValue exception:{values}')

                        if not model.IsNullOrEmpty(item.Spec):
                            rReturn = True if item.testValue in item.Spec else False
                        if not model.IsNullOrEmpty(item.Limit_min) or not model.IsNullOrEmpty(
                                item.Limit_max):
                            rReturn, compInfo = model.basefunc.CompareLimit(item.Limit_min, item.Limit_max,
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
