#!/usr/bin/env python
# coding: utf-8
"""
@File   : rmainform.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import os
import re
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from os.path import dirname, abspath, join
from PyQt5.uic import loadUi
import model.testcase
from runin.cell import Cell
from runin.ui_runin import Ui_RuninMain
import conf.globalvar as gv


class LoginWind:

    def __init__(self):
        self.runinWin = None
        self.AbFace = ''
        self.ScanFixName = ''
        self.FixtureNumber = ''
        self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_login.ui'))
        self.ui.lineEdit.returnPressed.connect(self.onSignIn)

    def onSignIn(self):
        # import conf.globalvar as gv
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
            self.runinWin = RuninMainForm()
            self.runinWin.show()
            self.ui.hide()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))


class RuninMainForm(QMainWindow, Ui_RuninMain):
    def __init__(self, parent=None):
        self.CellList = []
        self.CheckSnList = []
        self.RowCount = gv.cf.RUNIN.row
        self.ColCount = gv.cf.RUNIN.col
        self.testcase = model.testcase.TestCase(rf'{gv.excel_file_path}', f'{gv.cf.station.station_name}')
        self.testSequences = self.testcase.clone_suites
        QMainWindow.__init__(self, parent)
        Ui_RuninMain.__init__(self)
        super().__init__(parent)
        # self.timer = None
        self.setupUi(self)
        # self.refresh()
        self.initUI()

        self.lineEdit_2.returnPressed.connect(self.start_cell_test)

    def initUI(self):
        for i in range(self.RowCount):
            for j in range(self.ColCount):
                self.create_cell(i, j)
        self.lineEdit.setFocus()
        # self.timer.stop()

    def create_cell(self, i, j):
        widget_cell = Cell(self.body, i + 1, j + 1)
        widget_cell.setObjectName(f"widget_{i + 1}{j + 1}")
        self.gridLayout.addWidget(widget_cell, i, j, 1, 1)
        self.CellList.append(widget_cell)
        # objName = f"widget_{i + 1}{j + 1}"
        # setattr(self, objName, Cell(self.body, i + 1, j + 1))
        # widget_cell = getattr(self, objName)
        # widget_cell.setObjectName(objName)
        # self.gridLayout.addWidget(widget_cell, i, j)
        # print(self.gridLayout.rowCount(), self.gridLayout.columnCount())

    # def refresh(self):
    #     self.timer = QTimer()
    #     self.timer.timeout.connect(self.initUI)
    #     self.timer.start(10)  # 10 times per sec
    def start_cell_test(self):
        try:
            scanSN = self.lineEdit_2.text().strip()
            localNo = int(self.lineEdit.text().strip()[1:])
            if len(scanSN) == gv.cf.dut.sn_len:
                if scanSN in self.CheckSnList:
                    self.lineEdit_2.setStyleSheet("background-color: rgb(255, 85, 255);")
                    self.lb_info.setText('SN is repetitive!')
                    self.clear_input()
                    return

            if not self.CellList[localNo - 1].StartFlag:
                self.clear_input()
                gv.logPath = gv.logFolderPath + rf"\{datetime.now().strftime('%Y%m%d')}"
                os.makedirs(gv.OutPutPath, exist_ok=True)
                os.makedirs(gv.DataPath, exist_ok=True)
                os.makedirs(gv.logPath + r"\Json", exist_ok=True)
                os.makedirs(gv.cf.station.log_folder + r"\CsvData\Upload", exist_ok=True)
                gv.debugPath = fr"{gv.logPath}\debug_{datetime.now().strftime('%Y%m%d')}.txt"
                self.init_cell_param(localNo, scanSN)
                self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.lineEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.lb_info.setText('')

            else:
                pass
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))
            self.clear_input()

    def clear_input(self):
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit.setFocus()

    def init_cell_param(self, localNo, sn):
        self.CellList[localNo - 1].CellLogTxt = rf"{gv.logPath}\{localNo}_{sn}_{datetime.now().strftime('%H%M%S')}.txt"
        self.CellList[localNo - 1].lb_sn.setText(sn)
        self.CellList[localNo - 1].lb_cellNum.setVisible(False)
        self.CellList[localNo - 1].lb_testName.setText('')
        self.CellList[localNo - 1].lbl_failCount.setText('')
        self.CellList[localNo - 1].sequences = self.testSequences
        if self.CellList[localNo - 1].startTest():
            self.CheckSnList.append(sn)


# class RuninMainForm2(QWidget):
#     main_form = None
#     _lock = threading.RLock()
#
#     # def __new__(cls, *args, **kwargs):
#     #
#     #     if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
#     #         return cls.main_form
#     #     with cls._lock:  # 使用with语法，方便抢锁释放锁
#     #         if not cls.main_form:
#     #             cls.main_form = super().__new__(cls, *args, **kwargs)
#     #         return cls.main_form
#
#     def __init__(self):
#         super().__init__()
#         self.gridLayout = None
#         self.timer = None
#         self.RowCount = 10
#         self.ColCount = 8
#         self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_runin.ui'))
#         self.initUI()
#
#     def initUI(self):
#         self.gridLayout = QtWidgets.QGridLayout(self.ui.body)
#         self.gridLayout.setObjectName("gridLayout")
#         for i in range(self.RowCount):
#             for j in range(self.ColCount):
#                 self.create_cell(i, j)
#         # self.timer.stop()
#
#     def create_cell(self, i, j):
#         # widget_cell = Cell(self.ui.body, i + 1, j + 1)
#         # widget_cell.setObjectName(f"widget_{i + 1}{j + 1}")
#         # self.gridLayout.addWidget(widget_cell, i, j)
#         # print(self.gridLayout.rowCount(), self.gridLayout.columnCount())
#
#         objName = f"widget_{i + 1}{j + 1}"
#         setattr(self, objName, Cell(self.ui.body, i + 1, j + 1))
#         widget_cell = getattr(self, objName)
#         widget_cell.setObjectName(objName)
#         self.gridLayout.addWidget(widget_cell, i, j)
#         print(self.gridLayout.rowCount(), self.gridLayout.columnCount())
#         # print(widget_cell.getObjectName())
#
#     def refresh(self):
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.initUI)
#         self.timer.start(10)  # 10 times per sec
#

if __name__ == "__main__":
    app = QApplication([])
    # LoginWin = LoginWind()
    # LoginWin.ui.show()
    runinMainWin = RuninMainForm2()
    runinMainWin.ui.show()
    sys.exit(app.exec_())
