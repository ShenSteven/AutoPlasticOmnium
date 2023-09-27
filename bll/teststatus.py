#!/usr/bin/env python
# coding: utf-8
"""
@File   : teststatus.py
@Author : Steven.Shen
@Date   : 12/8/2022
@Desc   : 
"""
import os.path
import traceback
from datetime import datetime
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QLabel, QAction, QWidget
import conf.globalvar as gv
from common.basicfunc import ensure_path_sep


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
            if gv.LoginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 255, 0);")
                myWind.start_time = datetime.now()
                myWind.startFlag = True
                myWind.mySignals.timingSignal[bool].emit(True)
                print(
                    f"Start test,SN:{myWind.SN},CellNO={myWind.LocalNo},Station:{gv.cfg.station.station_no},DUTMode:{myWind.dut_model},"
                    f"TestMode:{gv.cfg.dut.test_mode},IsDebug:{gv.IsDebug},FTC:{gv.cfg.station.fail_continue},"
                    f"SoftVersion:{gv.VERSION},WebPS={myWind.WebPsIp}")
            else:
                myWind.treeWidget.blockSignals(True)
                if not myWind.SingleStepTest:
                    myWind.mySignals.textEditClearSignal[str].emit('')
                myWind.mySignals.lineEditEnableSignal[bool].emit(False)
                if gv.cfg.station.station_name in ['M4', 'M6', 'SX5GEV']:
                    myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_status, 'Flashing', 36,
                                                                                Qt.yellow)
                else:
                    myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_status, 'Testing', 36,
                                                                                Qt.yellow)
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_errorCode, '', 20, Qt.yellow)
                myWind.mySignals.timingSignal[bool].emit(True)
                # gv.startTime = datetime.now()
                myWind.mySignals.setIconSignal[QAction, QIcon].emit(myWind.actionStart,
                                                                    QIcon(':/images/Pause-icon.png'))
                myWind.mySignals.controlEnableSignal[QAction, bool].emit(myWind.actionStop, True)
                myWind.startFlag = True
                myWind.logger.debug(
                    f"Start test,SN:{myWind.SN},Station:{gv.cfg.station.station_no},DUTMode:{myWind.dut_model},"
                    f"TestMode:{gv.cfg.dut.test_mode},IsDebug:{gv.IsDebug},"
                    f"FTC:{gv.cfg.station.fail_continue},SoftVersion:{gv.VERSION}")
                myWind.mySignals.update_tableWidget[list].emit([])
                myWind.pause_event.set()
        elif status == TestStatus.FAIL:
            if gv.LoginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 0, 0);")
                myWind.mySignals.updateLabel[QLabel, str].emit(myWind.lb_testName,
                                                               f"<A href='file:///{myWind.txtLogPath}'>{myWind.testcase.error_details_first_fail}</A>")
            else:
                myWind.total_fail_count += 1
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_status, 'FAIL', 36, Qt.red)
                myWind.mySignals.play_audio[str].emit(os.path.join(gv.CurrentDir, 'ffmpeg', 'fail2.wav'))
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_testTime, str(myWind.sec), 11,
                                                                            Qt.gray)
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_errorCode,
                                                                            myWind.testcase.error_details_first_fail,
                                                                            20, Qt.red)
                myWind.UpdateContinueFail(False)
                if myWind.setIpFlag:
                    myWind.testcase.dut_comm.send_command(f"luxsetip {gv.cfg.dut.dut_ip} 255.255.255.0",
                                                          gv.cfg.dut.prompt, 1)
        elif status == TestStatus.PASS:
            if gv.LoginWin is not None:
                myWind.setStyleSheet("background-color: rgb(0, 255, 0);")
            else:
                myWind.total_pass_count += 1
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_status, 'PASS', 36, Qt.green)
                myWind.mySignals.play_audio[str].emit(os.path.join(gv.CurrentDir, 'ffmpeg', 'finish2.wav'))
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_errorCode, str(myWind.sec),
                                                                            20, Qt.green)
                myWind.UpdateContinueFail(True)
        elif status == TestStatus.ABORT:
            if gv.LoginWin is not None:
                myWind.setStyleSheet("background-color: rgb(255, 255, 255);")
                myWind.total_abort_count += 1
                myWind.testThread.terminate()
                myWind.testThread.wait(1)
            else:
                myWind.total_abort_count += 1
                myWind.testThread.terminate()
                myWind.testThread.wait(1)
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_status, 'Abort', 36, Qt.gray)
                myWind.mySignals.play_audio[str].emit(os.path.join(gv.CurrentDir, 'ffmpeg', 'fail1.wav'))
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_testTime, str(myWind.sec), 11,
                                                                            Qt.gray)
                myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_errorCode,
                                                                            myWind.testcase.error_details_first_fail,
                                                                            20, Qt.gray)
                myWind.saveTestResult()
    except Exception as e:
        myWind.logger.fatal(f"SetTestStatus Exception！！{e},{traceback.format_exc()}")
    finally:
        try:
            if gv.LoginWin is not None:
                if status != TestStatus.START:
                    gv.CheckSnList.remove(myWind.SN)
                    myWind.SN = ''
                    myWind.mySignals.timingSignal[bool].emit(False)
                    myWind.startFlag = False
                    myWind.logger.debug(f"Test end,ElapsedTime:{myWind.sec}s.")
                    myWind.mySignals.saveTextEditSignal[str].emit('rename')
                    if not myWind.finalTestResult:
                        myWind.mySignals.updateLabel[QLabel, str].emit(myWind.lb_testName,
                                                                       rf"<A href='file:///{ensure_path_sep(myWind.txtLogPath)}'>{myWind.testcase.error_details_first_fail}</A>")
                    else:
                        pass
            else:
                myWind.SaveScriptDisableFlag = True
                if status != TestStatus.START:
                    myWind.mySignals.setIconSignal[QAction, QIcon].emit(myWind.actionStart,
                                                                        QIcon(':/images/Start-icon.png'))
                    myWind.mySignals.controlEnableSignal[QAction, bool].emit(myWind.actionStop, False)
                    myWind.mySignals.timingSignal[bool].emit(False)
                    myWind.logger.debug(f"Test end,ElapsedTime:{myWind.sec}s.")
                    myWind.startFlag = False
                    myWind.mySignals.lineEditEnableSignal[bool].emit(True)
                    myWind.mySignals.updateStatusBarSignal[str].emit('')
                    myWind.mySignals.saveTextEditSignal[str].emit('rename')
                    if not myWind.finalTestResult:
                        myWind.mySignals.updateLabel[QLabel, str, int, QBrush].emit(myWind.lb_errorCode,
                                                                                    myWind.testcase.error_details_first_fail,
                                                                                    20, Qt.red)
                    myWind.main_form.treeWidget.blockSignals(False)
        except Exception as e:
            myWind.logger.fatal(f"SetTestStatus Exception！！{e}")
            raise
