#!/usr/bin/env python
# coding: utf-8
"""
@File   : teststatus.py
@Author : Steven.Shen
@Date   : 12/8/2022
@Desc   : 
"""
import traceback
from datetime import datetime
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QLabel, QAction, QWidget
import conf.globalvar as gv


class TestStatus(Enum):
    """测试状态枚举类"""
    PASS = 1
    FAIL = 2
    START = 3
    ABORT = 4


def SetTestStatus(myWind: QWidget, status: TestStatus):
    """设置并处理不同的测试状态"""
    try:
        if status == TestStatus.START:
            if gv.loginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 255, 0);")
                myWind.start_time = datetime.now()
                myWind.startFlag = True
                myWind.my_signals.timingSignal[bool].emit(True)
                print(
                    f"Start test,SN:{myWind.SN},CellNO={myWind.localNo},Station:{gv.cf.station.station_no},DUTMode:{myWind.dut_model},"
                    f"TestMode:{gv.cf.dut.test_mode},IsDebug:{gv.IsDebug},FTC:{gv.cf.station.fail_continue},"
                    f"SoftVersion:{gv.version},WebPS={myWind.WebPsIp}")
            else:
                myWind.ui.treeWidget.blockSignals(True)
                if not myWind.SingleStepTest:
                    myWind.my_signals.textEditClearSignal[str].emit('')
                myWind.my_signals.lineEditEnableSignal[bool].emit(False)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'Testing', 36,
                                                                             Qt.yellow)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode, '', 20, Qt.yellow)
                myWind.my_signals.timingSignal[bool].emit(True)
                # gv.startTime = datetime.now()
                myWind.my_signals.setIconSignal[QAction, QIcon].emit(myWind.ui.actionStart,
                                                                     QIcon(':/images/Pause-icon.png'))
                myWind.my_signals.controlEnableSignal[QAction, bool].emit(myWind.ui.actionStop, True)
                myWind.startFlag = True
                myWind.logger.debug(
                    f"Start test,SN:{myWind.SN},Station:{gv.cf.station.station_no},DUTMode:{myWind.dut_model},"
                    f"TestMode:{gv.cf.dut.test_mode},IsDebug:{gv.IsDebug},"
                    f"FTC:{gv.cf.station.fail_continue},SoftVersion:{gv.version}")
                myWind.my_signals.update_tableWidget[str].emit('clear')
                myWind.pause_event.set()
        elif status == TestStatus.FAIL:
            if gv.loginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 0, 0);")
                myWind.my_signals.updateLabel[QLabel, str].emit(myWind.lb_testName,
                                                                f"<A href='https://www.qt.io/'>{myWind.testcase.error_details_first_fail}</A>")
            else:
                myWind.total_fail_count += 1
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'FAIL', 36, Qt.red)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_testTime, str(myWind.sec), 11,
                                                                             Qt.gray)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                             myWind.testcase.error_details_first_fail,
                                                                             20, Qt.red)
                myWind.UpdateContinueFail(False)
                if myWind.setIpFlag:
                    myWind.testcase.dut_comm.send_command(f"luxsetip {gv.cf.dut.dut_ip} 255.255.255.0",
                                                          gv.cf.dut.prompt, 1)
        elif status == TestStatus.PASS:
            if gv.loginWin is not None:
                myWind.setStyleSheet("background-color: rgb(0, 255, 0);")
            else:
                myWind.total_pass_count += 1
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'PASS', 36, Qt.green)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode, str(myWind.sec),
                                                                             20, Qt.green)
                myWind.UpdateContinueFail(True)
        elif status == TestStatus.ABORT:
            if gv.loginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 255, 255);")
                myWind.total_abort_count += 1
                myWind.testThread.terminate()
                myWind.testThread.wait(1)
            else:
                myWind.total_abort_count += 1
                myWind.testThread.terminate()
                myWind.testThread.wait(1)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'Abort', 36, Qt.gray)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_testTime, str(myWind.sec), 11,
                                                                             Qt.gray)
                myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                             myWind.testcase.error_details_first_fail,
                                                                             20, Qt.gray)
                myWind.saveTestResult()
    except Exception as e:
        myWind.logger.fatal(f"SetTestStatus Exception！！{e},{traceback.format_exc()}")
    finally:
        try:
            if gv.loginWin is not None:
                if status != TestStatus.START:
                    gv.CheckSnList.remove(myWind.SN)
                    myWind.SN = ''
                    myWind.my_signals.timingSignal[bool].emit(False)
                    myWind.startFlag = False
                    myWind.logger.debug(f"Test end,ElapsedTime:{myWind.sec}s.")
                    myWind.my_signals.saveTextEditSignal[str].emit('rename')
                    if not myWind.finalTestResult:
                        myWind.my_signals.updateLabel[QLabel, str].emit(myWind.lb_testName,
                                                                        f"<A href='https://www.qt.io/'>{myWind.testcase.error_details_first_fail}</A>")
                    else:
                        pass
            else:
                myWind.SaveScriptDisableFlag = True
                if status != TestStatus.START:
                    myWind.my_signals.setIconSignal[QAction, QIcon].emit(myWind.ui.actionStart,
                                                                         QIcon(':/images/Start-icon.png'))
                    myWind.my_signals.controlEnableSignal[QAction, bool].emit(myWind.ui.actionStop, False)
                    myWind.my_signals.timingSignal[bool].emit(False)
                    myWind.logger.debug(f"Test end,ElapsedTime:{myWind.sec}s.")
                    myWind.startFlag = False
                    myWind.my_signals.lineEditEnableSignal[bool].emit(True)
                    myWind.my_signals.updateStatusBarSignal[str].emit('')
                    myWind.my_signals.saveTextEditSignal[str].emit('rename')
                    if not myWind.finalTestResult:
                        myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                                     myWind.testcase.error_details_first_fail,
                                                                                     20,
                                                                                     Qt.red)
                    myWind.main_form.ui.treeWidget.blockSignals(False)
        except Exception as e:
            myWind.logger.fatal(f"SetTestStatus Exception！！{e}")
        # finally:
        #     try:
        #         if status != TestStatus.START:
        #             pass
        #     except Exception as e:
        #         lg.logger.fatal(f"SetTestStatus Exception！！{e}")
