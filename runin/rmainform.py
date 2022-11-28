#!/usr/bin/env python
# coding: utf-8
"""
@File   : rmainform.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import re
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from os.path import dirname, abspath, join
from PyQt5.uic import loadUi
import conf.globalvar as gv
from runin.ui_runin import Ui_RuninMain


# class RuninMainForm(QMainWindow, Ui_RuninMain):
#
#     def __init__(self, parent=None):
#         QMainWindow.__init__(self, parent)
#         Ui_RuninMain.__init__(self)
#         super().__init__(parent)
#         self.setupUi(self)

class LoginWind:
    def __init__(self):
        self.AbFace = ''
        self.ScanFixName = ''
        self.FixtureNumber = ''
        self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_login.ui'))
        self.ui.lineEdit.returnPressed.connect(self.onSignIn)

    def onSignIn(self):
        try:
            self.ScanFixName = self.ui.lineEdit.text()
            runin_pattern = re.compile('RUNIN-[0-9]{4}(A|B)')
            ort_pattern = re.compile('ORT-[0-9]{4}(A|B)')
            runin_mr = re.match(runin_pattern, self.ScanFixName, flags=0)
            ort_mr = re.match(ort_pattern, self.ScanFixName, flags=0)
            if runin_mr is not None:
                self.FixtureNumber = self.ScanFixName[0:10]
                self.AbFace = self.ScanFixName[10:11]
            elif ort_mr is not None:
                self.FixtureNumber = self.ScanFixName[0:8]
                self.AbFace = self.ScanFixName[8:9]
            else:
                QMessageBox.critical(None, "Error", 'Station name is Wrong!')
                self.ui.lineEdit.setText('')
                self.ui.lineEdit.setFocus()
                self.ui.label_2.setText("RUNIN/ORT-xxxxX")
                self.FixtureNumber = ''
                self.AbFace = ''
                return

            self.ui.lineEdit.Enabled = False
            gv.cf.station.station_name = self.FixtureNumber[0:self.FixtureNumber.index('-')]
            gv.cf.station.station_no = self.FixtureNumber + self.AbFace
            runinMainWin = RuninMainForm()
            runinMainWin.ui.show()
            self.ui.hide()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))


class RuninMainForm(QWidget):
    main_form = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):

        if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
            return cls.main_form
        with cls._lock:  # 使用with语法，方便抢锁释放锁
            if not cls.main_form:
                cls.main_form = super().__new__(cls, *args, **kwargs)
            return cls.main_form

    def __init__(self, row=None, column=None):
        super().__init__()
        self.RowCount = row
        self.ColCount = column
        self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_runin.ui'))


if __name__ == "__main__":
    app = QApplication([])
    LoginWin = LoginWind()
    LoginWin.ui.show()
    # mainWin = RuninMainForm()
    # mainWin.ui.show()
    app.exec_()
