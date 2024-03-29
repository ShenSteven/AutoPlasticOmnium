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
from inspect import currentframe

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

import conf.globalvar as gv
import dataaccess.sqlite
import models.loadseq
import models.testcase
from common.mysignals import on_actOpenFile
from runin.cell import Cell
from runin.ui_login import Ui_Login
from runin.ui_runin import Ui_RuninMain


class LoginWind(QMainWindow, Ui_Login):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        Ui_Login.__init__(self)
        self.setupUi(self)
        self.runinWin = None
        self.AbFace = ''
        self.ScanFixName = ''
        self.FixtureNumber = ''
        # self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_login.ui'))
        self.lineEdit.returnPressed.connect(self.onSignIn)

    def onSignIn(self):
        try:
            self.ScanFixName = self.lineEdit.text()
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
                self.lineEdit.setText('')
                self.lineEdit.setFocus()
                self.label_2.setText("RUNIN/ORT-xxxxX")
                self.FixtureNumber = ''
                self.AbFace = ''
                return

            self.lineEdit.Enabled = False
            # gv.cf.station.station_name = self.FixtureNumber[0:self.FixtureNumber.index('-')]
            gv.cfg.station.stationNo = self.FixtureNumber + self.AbFace
            self.runinWin = RuninMainForm()
            self.runinWin.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))


class RuninMainForm(QMainWindow, Ui_RuninMain):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        Ui_RuninMain.__init__(self)
        super().__init__(parent)
        self.logger = gv.lg.logger
        self.CellList = []
        self.RowCount = gv.cfg.RUNIN.row
        self.ColCount = gv.cfg.RUNIN.col
        self.setupUi(self)
        self.lb_ip.setText('IP: ' + socket.gethostbyname(socket.gethostname()))
        self.lb_station.setText(gv.cfg.station.stationNo + ' / ' + gv.cfg.station.stationName)
        self.lb_testMode.setText(gv.cfg.dut.testMode)
        self.lb_info.setText('Please scan sn.')
        self.setWindowTitle('RUNIN/ORT ' + gv.VERSION)
        self.initCellUi()
        self.lineEdit_1.returnPressed.connect(self.locationInput)
        self.lineEdit.textEdited.connect(self.on_textEdited)
        self.lineEdit.returnPressed.connect(self.start_cell)
        self.bt_openLog.clicked.connect(lambda: on_actOpenFile(gv.LogFolderPath))

    def initCellUi(self):
        gv.InitCreateDirs(self.logger)
        dataaccess.sqlite.init_sqlite_database(self.logger, gv.DatabaseSetting)
        if not getattr(sys, 'frozen', False):
            models.loadseq.excel_convert_to_json(f'{gv.ExcelFilePath}', gv.cfg.station.stationAll, self.logger)
        for row in range(self.RowCount):
            for col in range(self.ColCount):
                widget_cell = Cell(self.body, row + 1, col + 1)
                widget_cell.setObjectName(f"widget_{row + 1}{col + 1}")
                self.gridLayout.addWidget(widget_cell, row, col, 1, 1)
                self.CellList.append(widget_cell)
        self.lineEdit_1.setFocus()
        self.lineEdit.setMaxLength(gv.cfg.dut.snLen)

    def locationInput(self):
        try:
            if len(self.lineEdit_1.text().strip()) == 3:
                self.lineEdit.setFocus()
            else:
                QMessageBox.critical(None, "Exception", "Location length error")
                self.clear_input()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))
            self.logger.critical(f'{currentframe().f_code.co_name}: str(e)')
            self.clear_input()

    def start_cell(self):
        try:
            scanSN = self.lineEdit.text().strip()
            localNo = int(self.lineEdit_1.text().strip()[1:])
            if getattr(sys, 'frozen', True):
                if scanSN in gv.CheckSnList:
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 85, 255);")
                    self.lb_info.setText('SN is repetitive!')
                    self.clear_input()
                    return

                if not self.CellList[localNo - 1].startFlag:
                    self.clear_input()
                    self.init_cell_param(localNo, scanSN)
                    self.lineEdit_1.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.lb_info.setText('')
                else:
                    self.lineEdit_1.setStyleSheet("background-color: rgb(255, 255, 0);")
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 0);")
                    self.lb_info.setText('Location is testing!')
                    self.clear_input()
            else:
                if len(scanSN) != gv.cfg.dut.snLen:
                    self.lineEdit.setStyleSheet("background-color: rgb(255, 0, 0);")
                    self.lb_info.setText('SN length error!')
                    self.clear_input()
        except Exception as e:
            QMessageBox.critical(None, "Exception", str(e))
            self.clear_input()

    def on_textEdited(self):
        def JudgeProdMode():
            """通过SN判断机种"""
            sn = self.lineEdit.text()
            if sn[0] == 'J' or sn[0] == '6':
                self.dutModel = gv.cfg.dut.dutModels[0]
            elif sn[0] == 'N' or sn[0] == '7':
                self.dutModel = gv.cfg.dut.dutModels[1]
            elif sn[0] == 'Q' or sn[0] == '8':
                self.dutModel = gv.cfg.dut.dutModels[2]
            elif sn[0] == 'S' or sn[0] == 'G':
                self.dutModel = gv.cfg.dut.dutModels[3]
            else:
                self.dutModel = 'unknown'

        """验证dut sn的正则规则"""
        if JudgeProdMode() != 'unknown' and not gv.IsDebug:
            reg = QRegExp(gv.cfg.dut.dutSNRegex[self.dutModel])
            pValidator = QRegExpValidator(reg, self)
            self.lineEdit.setValidator(pValidator)

    def init_cell_param(self, localNo, sn):
        self.CellList[localNo - 1].lb_sn.setText(sn)
        self.CellList[localNo - 1].lbl_failCount.setText('')
        self.CellList[localNo - 1].dutModel = self.dutModel
        self.CellList[localNo - 1].lb_model.setText(self.dutModel)
        if self.CellList[localNo - 1].startTest():
            gv.CheckSnList.append(sn)

    def clear_input(self):
        self.lineEdit_1.setText('')
        self.lineEdit.setText('')
        self.lineEdit_1.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    # LoginWin = LoginWind()
    # LoginWin.show()
    runinMainWin = RuninMainForm()
    runinMainWin.show()
    sys.exit(app.exec_())
