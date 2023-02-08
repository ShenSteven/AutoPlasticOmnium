#!/usr/bin/env python
# coding: utf-8
"""
@File   : rmainform.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import re
import socket
import sys
import time
from inspect import currentframe

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from os.path import dirname, abspath, join
from PyQt5.uic import loadUi
import model.testcase
import model.loadseq
from model.mysignals import on_actionLogFolder
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
        try:
            self.ScanFixName = self.ui.lineEdit.text()
            runin_mr = re.match(re.compile('RUNIN-[0-9]{4}(A|B)'), self.ScanFixName, flags=0)
            ort_mr = re.match(re.compile('ORT-[0-9]{4}(A|B)'), self.ScanFixName, flags=0)
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
        QMainWindow.__init__(self, parent)
        Ui_RuninMain.__init__(self)
        super().__init__(parent)
        self.dut_model = None
        self.logger = gv.lg.logger
        self.CellList = []
        self.CheckSnList = []
        self.RowCount = gv.cf.RUNIN.row
        self.ColCount = gv.cf.RUNIN.col
        self.setupUi(self)
        self.lb_ip.setText('IP: ' + socket.gethostbyname(socket.gethostname()))
        self.lb_station.setText(gv.cf.station.station_no)
        self.lb_testMode.setText(gv.cf.dut.test_mode)
        self.lb_info.setText('Please can sn.')
        self.setWindowTitle('RUNIN/ORT ' + gv.version)
        self.initCellUi()
        self.lineEdit.returnPressed.connect(self.locationInput)
        self.lineEdit_2.textEdited.connect(self.on_textEdited)
        self.lineEdit_2.returnPressed.connect(self.start_cell)
        self.bt_openLog.clicked.connect(on_actionLogFolder)

    def initCellUi(self):
        if not getattr(sys, 'frozen', False):
            model.loadseq.excel_convert_to_json(f'{gv.excel_file_path}', gv.cf.station.station_all, self.logger)
        for row in range(self.RowCount):
            for col in range(self.ColCount):
                widget_cell = Cell(self.body, row + 1, col + 1)
                widget_cell.setObjectName(f"widget_{row + 1}{col + 1}")
                self.gridLayout.addWidget(widget_cell, row, col, 1, 1)
                self.CellList.append(widget_cell)
        self.lineEdit.setFocus()

    def locationInput(self):
        try:
            if len(self.lineEdit.text().strip()) == 3:
                self.lineEdit_2.setFocus()
            else:
                QMessageBox.critical(None, "Exception", "Location length error")
                self.clear_input()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))
            self.logger.critical(f'{currentframe().f_code.co_name}: str(e)')
            self.clear_input()

    def start_cell(self):
        try:
            scanSN = self.lineEdit_2.text().strip()
            localNo = int(self.lineEdit.text().strip()[1:])
            if getattr(sys, 'frozen', True):
                if scanSN in self.CheckSnList:
                    self.lineEdit_2.setStyleSheet("background-color: rgb(255, 85, 255);")
                    self.lb_info.setText('SN is repetitive!')
                    self.clear_input()
                    return

                if not self.CellList[localNo - 1].startFlag:
                    self.clear_input()
                    gv.init_create_dirs(self.logger)
                    self.init_cell_param(localNo, scanSN)
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.lineEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.lb_info.setText('')
                else:
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 0);")
                    self.lineEdit_2.setStyleSheet("background-color: rgb(255, 255, 0);")
                    self.lb_info.setText('Location is testing!')
                    self.clear_input()
            else:
                if len(scanSN) != gv.cf.dut.sn_len:
                    self.lineEdit_2.setStyleSheet("background-color: rgb(255, 0, 0);")
                    self.lb_info.setText('SN length error!')
                    self.clear_input()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))
            self.clear_input()

    def on_textEdited(self):
        def JudgeProdMode():
            """通过SN判断机种"""
            sn = self.lineEdit_2.text()
            if sn[0] == 'J' or sn[0] == '6':
                self.dut_model = gv.cf.dut.dut_models[0]
            elif sn[0] == 'N' or sn[0] == '7':
                self.dut_model = gv.cf.dut.dut_models[1]
            elif sn[0] == 'Q' or sn[0] == '8':
                self.dut_model = gv.cf.dut.dut_models[2]
            elif sn[0] == 'S' or sn[0] == 'G':
                self.dut_model = gv.cf.dut.dut_models[3]
            else:
                self.dut_model = 'unknown'

        """验证dut sn的正则规则"""
        if JudgeProdMode() != 'unknown' and not gv.IsDebug:
            reg = QRegExp(gv.cf.dut.dut_regex[self.dut_model])
            pValidator = QRegExpValidator(reg, self)
            self.lineEdit_2.setValidator(pValidator)

    def init_cell_param(self, localNo, sn):
        self.CellList[
            localNo - 1].CellLogTxt = rf"{gv.logFolderPath}\logging_{localNo}_{sn}_details_{time.strftime('%H-%M-%S')}.txt"
        self.CellList[localNo - 1].lb_sn.setText(sn)
        self.CellList[localNo - 1].lb_cellNum.setVisible(False)
        self.CellList[localNo - 1].lb_testName.setText('')
        self.CellList[localNo - 1].lbl_failCount.setText('')
        self.CellList[localNo - 1].logger = rf"{gv.logFolderPath}\{localNo}_{sn}_{time.strftime('%H%M%S')}.txt"
        self.CellList[localNo - 1].dut_model = self.dut_model
        self.CellList[localNo - 1].lb_model.setText(self.dut_model)
        if self.CellList[localNo - 1].startTest():
            self.CheckSnList.append(sn)

    def clear_input(self):
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    # LoginWin = LoginWind()
    # LoginWin.ui.show()
    runinMainWin = RuninMainForm()
    runinMainWin.show()
    sys.exit(app.exec_())
