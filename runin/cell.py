#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import threading
import traceback
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QMessageBox
from model.mysignals import MySignals, update_label
from model.testthread import TestThread
from runin.ui_cell import Ui_cell


class Cell(QFrame, Ui_cell):
    main_form = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):

        if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
            return cls.main_form
        with cls._lock:  # 使用with语法，方便抢锁释放锁
            if not cls.main_form:
                cls.main_form = super().__new__(cls, *args, **kwargs)
            return cls.main_form

    def __init__(self, parent=None, row=-1, col=-1, testcase=None):
        QFrame.__init__(self, parent)
        Ui_cell.__init__(self)
        self.SN = ''
        self.sec = 1
        self.my_signals = MySignals()
        self.timer = None
        self.setupUi(self)
        self.row_index = row
        self.col_index = col
        self.testcase = testcase
        self.sequences = []
        self.CellLogTxt = ''
        self.rs_url = ''
        self.mes_result = ''
        self.logger = None
        self.StartFlag = False
        self.init_cell_ui()
        self.init_signals_connect()
        self.testThread = TestThread(self)

    def init_cell_ui(self):
        self.lb_cellNum.setText('')
        self.lb_sn.setText('')
        self.lb_model.setText('')
        self.lb_testTime.setText('')
        self.lbl_failCount.setText('')
        self.lb_testName.setText(f'{self.row_index}-{self.col_index}')
        self.testcase.myWind = self

    def init_signals_connect(self):
        """connect signals to slots"""
        self.my_signals.timingSignal[bool].connect(self.timing)
        self.my_signals.updateLabel[QLabel, str, int, QBrush].connect(update_label)
        self.my_signals.updateLabel[QLabel, str, int].connect(update_label)
        self.my_signals.updateLabel[QLabel, str].connect(update_label)
        self.my_signals.showMessageBox[str, str, int].connect(self.showMessageBox)

    @QtCore.pyqtSlot(str, str, int, result=QMessageBox.StandardButton)
    def showMessageBox(self, title, text, level=2):
        if level == 0:
            return QMessageBox.information(self, title, text, QMessageBox.Yes)
        elif level == 1:
            return QMessageBox.warning(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        elif level == 2:
            aa = QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return aa
        elif level == 3:
            return QMessageBox.about(self, title, text)
        else:
            return QMessageBox.critical(self, title, text, QMessageBox.Yes)

    def startTest(self):
        try:
            if not self.checkContinueFailNum():
                return False
            self.startTestInit()
            if not self.testThread.isRunning():
                self.testThread = TestThread(self)
                self.testThread.start()
                # self.logger.debug(
                #     f"TestStart...CellNO={self.LocalNo},SN={self.SN},Station={Global.FIXTURENAME},DUTMode={self.dutMode},"
                #     f"TestMode={Global.TESTMODE},FAIL_CONTINUE={Global.FAIL_CONTINUE},SoftVersion:{Global.Version},WebPS={WebPsIp}")
        except Exception as e:
            self.logger.fatal(f" step run Exception！！{e},{traceback.format_exc()}")
            return False

    def checkContinueFailNum(self):
        pass

    def startTestInit(self):
        pass

    def timing(self, flag):
        if flag:
            self.logger.debug('start timing...')
            self.timer = self.startTimer(1000)
        else:
            self.logger.debug('stop timing...')
            self.killTimer(self.timer)

    def timerEvent(self, a):
        self.my_signals.updateLabel[QLabel, str, int].emit(self.lb_testTime, str(self.sec), 20)
        QApplication.processEvents()
        self.sec += 1


if __name__ == "__main__":
    app = QApplication([])
    mainWin = Cell()
    mainWin.show()
    app.exec_()
