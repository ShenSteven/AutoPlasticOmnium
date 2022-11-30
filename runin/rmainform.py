#!/usr/bin/env python
# coding: utf-8
"""
@File   : rmainform.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import re
import sys
import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QPushButton
from os.path import dirname, abspath, join
from PyQt5.uic import loadUi
from runin.cell import Cell
from runin.ui_runin import Ui_RuninMain


class LoginWind:

    def __init__(self):
        self.runinWin = None
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
            import conf.globalvar as gv
            gv.cf.station.station_name = self.FixtureNumber[0:self.FixtureNumber.index('-')]
            gv.cf.station.station_no = self.FixtureNumber + self.AbFace
            self.runinWin = RuninMainForm()
            self.runinWin.show()
            self.ui.hide()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))


class RuninMainForm(QMainWindow, Ui_RuninMain):
    def __init__(self, parent=None):
        import conf.globalvar as gv
        self.RowCount = gv.cf.RUNIN.row
        self.ColCount = gv.cf.RUNIN.col
        QMainWindow.__init__(self, parent)
        Ui_RuninMain.__init__(self)
        super().__init__(parent)
        self.timer = None
        self.setupUi(self)
        self.refresh()
        # self.init_test_cell()

    def initUI(self):
        for i in range(self.RowCount):
            for j in range(self.ColCount):
                self.create_cell(i, j)
        self.timer.stop()

    def create_cell(self, i, j):
        widget_cell = Cell(self.body, i + 1, j + 1)
        widget_cell.setObjectName(f"widget_{i + 1}{j + 1}")
        self.gridLayout.addWidget(widget_cell, i, j, 1, 1)
        # objName = f"widget_{i + 1}{j + 1}"
        # setattr(self, objName, Cell(self.body, i + 1, j + 1))
        # widget_cell = getattr(self, objName)
        # widget_cell.setObjectName(objName)
        # self.gridLayout.addWidget(widget_cell, i, j)
        # print(self.gridLayout.rowCount(), self.gridLayout.columnCount())

    def refresh(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.initUI)
        self.timer.start(10)  # 10 times per sec


class RuninMainForm2(QWidget):
    main_form = None
    _lock = threading.RLock()

    # def __new__(cls, *args, **kwargs):
    #
    #     if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
    #         return cls.main_form
    #     with cls._lock:  # 使用with语法，方便抢锁释放锁
    #         if not cls.main_form:
    #             cls.main_form = super().__new__(cls, *args, **kwargs)
    #         return cls.main_form

    def __init__(self):
        super().__init__()
        self.gridLayout = None
        self.timer = None
        self.RowCount = 10
        self.ColCount = 8
        self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_runin.ui'))
        self.initUI()

    def initUI(self):
        self.gridLayout = QtWidgets.QGridLayout(self.ui.body)
        self.gridLayout.setObjectName("gridLayout")
        for i in range(self.RowCount):
            for j in range(self.ColCount):
                self.create_cell(i, j)
        # self.timer.stop()

    def create_cell(self, i, j):
        # widget_cell = Cell(self.ui.body, i + 1, j + 1)
        # widget_cell.setObjectName(f"widget_{i + 1}{j + 1}")
        # self.gridLayout.addWidget(widget_cell, i, j)
        # print(self.gridLayout.rowCount(), self.gridLayout.columnCount())

        objName = f"widget_{i + 1}{j + 1}"
        setattr(self, objName, Cell(self.ui.body, i + 1, j + 1))
        widget_cell = getattr(self, objName)
        widget_cell.setObjectName(objName)
        self.gridLayout.addWidget(widget_cell, i, j)
        print(self.gridLayout.rowCount(), self.gridLayout.columnCount())
        # print(widget_cell.getObjectName())

    def refresh(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.initUI)
        self.timer.start(10)  # 10 times per sec


if __name__ == "__main__":
    app = QApplication([])
    # LoginWin = LoginWind()
    # LoginWin.ui.show()
    runinMainWin = RuninMainForm2()
    runinMainWin.ui.show()
    sys.exit(app.exec_())
