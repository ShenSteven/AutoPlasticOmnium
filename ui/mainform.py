import copy
import logging
import os
import sys
import stat
import threading
import time
import traceback
from datetime import datetime
from enum import Enum
from os.path import dirname, abspath, join
from threading import Thread
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QRegExp, QMetaObject, QThread
from PyQt5.QtGui import QIcon, QCursor, QBrush, QRegExpValidator, QPixmap
from PyQt5.QtWidgets import QMessageBox, QStyleFactory, QTreeWidgetItem, QMenu, QApplication, QAbstractItemView, \
    QHeaderView, QTableWidgetItem, QLabel, QWidget, QAction, QInputDialog, QLineEdit
import conf.globalvar as gv
from conf.logprint import QTextEditHandler, LogPrint
from model.basicfunc import IsNullOrEmpty, save_config, run_cmd
import sockets.serialport
from model.sqlite import Sqlite
import model.testcase
from peak.peaklin import PeakLin
from model.reporting import upload_Json_to_client, upload_result_to_mes, collect_data_to_csv, saveTestResult
from inspect import currentframe
import model.loadseq
import model.variables
import model.product

# pyrcc5 images.qrc -o images.py
# pyuic5 ui_main.ui -o main_ui.py
from ui.settings import SettingsDialog


class TestStatus(Enum):
    """测试状态枚举类"""
    PASS = 1
    FAIL = 2
    START = 3
    ABORT = 4


class MySignals(QObject):
    """自定义信号类"""
    loadseq = pyqtSignal(str)
    update_tableWidget = pyqtSignal((list,), (str,))
    updateLabel = pyqtSignal([QLabel, str, int, QBrush], [QLabel, str, int], [QLabel, str])
    treeWidgetColor = pyqtSignal([QBrush, int, int, bool])
    timingSignal = pyqtSignal(bool)
    textEditClearSignal = pyqtSignal(str)
    lineEditEnableSignal = pyqtSignal(bool)
    setIconSignal = pyqtSignal(QAction, QIcon)
    updateStatusBarSignal = pyqtSignal(str)
    updateActionSignal = pyqtSignal([QAction, QIcon, str], [QAction, QIcon])
    saveTextEditSignal = pyqtSignal(str)
    controlEnableSignal = pyqtSignal(QAction, bool)
    threadStopSignal = pyqtSignal(str)
    updateConnectStatusSignal = pyqtSignal(bool, str)
    showMessageBox = pyqtSignal([str, str, int])


def update_label(label: QLabel, str_: str, font_size: int = 36, color: QBrush = None):
    def thread_update():
        label.setText(str_)
        if color is not None:
            label.setStyleSheet(f"background-color:{color.color().name()};font: {font_size}pt '宋体';")
        QApplication.processEvents()

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


def updateAction(action_, icon: QIcon = None, text: str = None):
    def thread_update():
        if icon is not None:
            action_.setIcon(icon)
        if text is not None:
            action_.setText(text)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


def on_setIcon(action_, icon: QIcon):
    def thread_update():
        action_.setIcon(icon)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


def on_actionLogFolder():
    def thread_update():
        if os.path.exists(gv.logFolderPath):
            os.startfile(gv.logFolderPath)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


def on_actionException():
    def thread_update():
        if os.path.exists(gv.critical_log):
            os.startfile(gv.critical_log)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


def controlEnable(control, isEnable):
    def thread_update():
        control.setEnabled(isEnable)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()


class MainForm(QWidget):
    main_form = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):

        if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
            return cls.main_form
        with cls._lock:  # 使用with语法，方便抢锁释放锁
            if not cls.main_form:
                cls.main_form = super().__new__(cls, *args, **kwargs)
            return cls.main_form

    def __init__(self):
        super().__init__()
        self.logger = gv.lg.logger
        self.fileHandle = None
        self.SaveScriptDisableFlag = False
        self.SingleStepTest = False
        self.StepNo = -1
        self.SuiteNo = -1
        self.FailNumOfCycleTest = 0
        self.PassNumOfCycleTest = 0
        self.total_abort_count = 0
        self.total_fail_count = 0
        self.total_pass_count = 0
        self.continue_fail_count = 0
        self.my_signals = MySignals()
        self.timer = None
        self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_main.ui'))
        self.ui.setWindowTitle(self.ui.windowTitle() + f' v{gv.version}')
        self.init_create_dirs()
        # MainForm.main_form = self  # 单例模式
        self.sec = 1
        self.testcase: model.testcase.TestCase = model.testcase.TestCase(rf'{gv.excel_file_path}',
                                                                         f'{gv.cf.station.station_name}', self.logger)
        self.testSequences = self.testcase.clone_suites
        self.init_select_station()
        self.init_textEditHandler()
        self.init_lab_factory(gv.cf.station.privileges)
        self.init_tableWidget()
        self.init_childLabel()
        self.init_label_info()
        self.init_status_bar()
        self.init_lineEdit()
        self.init_signals_connect()
        self.ShowTreeView(self.testSequences)
        self.testThread = TestThread(self)
        self.testThread.start()

    def init_create_dirs(self):
        try:
            if not IsNullOrEmpty(gv.cf.station.setTimeZone):
                os.system(f"tzutil /s \"{gv.cf.station.setTimeZone}\"")
            os.makedirs(gv.logFolderPath + r"\Json", exist_ok=True)
            os.makedirs(gv.OutPutPath, exist_ok=True)
            os.makedirs(gv.DataPath, exist_ok=True)
            os.makedirs(gv.cf.station.log_folder + r"\CsvData\Upload", exist_ok=True)
        except Exception as e:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{e}')

    def init_select_station(self):
        for item in gv.cf.station.station_all:
            station_qaction = QAction(self)
            station_qaction.setObjectName(item)
            if item.startswith("FL_"):
                item += "(前左)"
            elif item.startswith("FR_"):
                item += "(前右)"
            elif item.startswith("RL_"):
                item += "(后左)"
            elif item.startswith("RML_"):
                item += "(后中左)"
            elif item.startswith("RMR_"):
                item += "(后中右)"
            elif item.startswith("RR_"):
                item += "(后右)"
            elif item.startswith("RM_"):
                item += "(后右)"
            elif item.startswith("FLB_"):
                item += "(前左保杠)"
            elif item.startswith("FRB_"):
                item += "(前右保杠)"
            elif item.startswith("FLG_"):
                item += "(前左格栅)"
            elif item.startswith("FRG_"):
                item += "(前右格栅)"
            elif item.startswith("ReadVer_"):
                item += "(读版本)"
            station_qaction.setText(item)
            self.ui.menuSelect_Station.addAction(station_qaction)
            station_qaction.triggered.connect(self.on_select_station)

    def init_textEditHandler(self):
        """create log handler for textEdit"""
        textEdit_handler = QTextEditHandler(stream=self.ui.textEdit)
        textEdit_handler.name = 'textEdit_handler'
        log_console = logging.getLogger('testlog').handlers[0]
        if getattr(sys, 'frozen', False):
            logging.getLogger('testlog').removeHandler(log_console)
            textEdit_handler.formatter = gv.lg.logger.handlers[0].formatter
            textEdit_handler.level = gv.lg.logger.handlers[0].level
            self.fileHandle = gv.lg.logger.handlers[0]
        else:
            gv.cf.station.privileges = 'lab'
            textEdit_handler.formatter = gv.lg.logger.handlers[1].formatter
            textEdit_handler.level = gv.lg.logger.handlers[1].level
            self.fileHandle = gv.lg.logger.handlers[1]
        logging.getLogger('testlog').addHandler(textEdit_handler)

    def init_lineEdit(self):
        self.ui.lineEdit.setFocus()
        self.ui.lineEdit.setMaxLength(gv.cf.dut.sn_len)
        # 自定义文本验证器
        reg = QRegExp('^[A-Z0-9]{' + f'{gv.cf.dut.sn_len},' + f'{gv.cf.dut.sn_len}' + '}')
        pValidator = QRegExpValidator(self.ui.lineEdit)
        pValidator.setRegExp(reg)
        # if not gv.IsDebug:
        #     self.ui.lineEdit.setValidator(pValidator)

    def init_childLabel(self):
        self.ui.lb_failInfo = QLabel('Next:O-SFT /Current:O', self.ui.lb_status)
        self.ui.lb_failInfo.setStyleSheet(
            f"background-color:#f0f0f0;font: 11pt '宋体';")
        self.ui.lb_failInfo.setHidden(True)
        self.ui.lb_testTime = QLabel('TestTime:30s', self.ui.lb_errorCode)
        self.ui.lb_testTime.setStyleSheet(
            f"background-color:#f0f0f0;font: 11pt '宋体';")
        self.ui.lb_testTime.setHidden(True)

    def init_tableWidget(self):
        self.ui.tableWidget_2.setHorizontalHeaderLabels(['property', 'value'])
        self.ui.tableWidget.setHorizontalHeaderLabels(gv.tableWidgetHeader)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
        strHeaderQss = "QHeaderView::section { background:#CCCCCC; color:black;min-height:3em;}"
        self.ui.tableWidget.setStyleSheet(strHeaderQss)
        self.ui.tableWidget_2.setStyleSheet(strHeaderQss)

    def init_lab_factory(self, str_):
        if str_ == "lab":
            gv.IsDebug = True
            self.ui.actionPrivileges.setIcon(QIcon(':/images/lab-icon.png'))
        else:
            gv.IsDebug = False
            self.ui.actionPrivileges.setIcon(QIcon(':/images/factory.png'))
            self.ui.actionConvertExcelToJson.setEnabled(False)
            self.ui.actionSaveToScript.setEnabled(False)
            self.ui.actionReloadScript.setEnabled(False)
            self.ui.actionStart.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionClearLog.setEnabled(False)
            if getattr(sys, 'frozen', False):
                self.ui.actionStart.setEnabled(True)
                self.ui.actionConfig.setEnabled(False)
                self.ui.actionOpenScript.setEnabled(False)
                self.ui.actionOpen_TestCase.setEnabled(False)
                self.ui.actionConvertExcelToJson.setEnabled(False)
                self.ui.actionEnable_lab.setEnabled(False)
                self.ui.actionDisable_factory.setEnabled(False)

    def init_label_info(self):
        def GetAllIpv4Address(networkSegment):
            import psutil
            from socket import AddressFamily
            for name, info in psutil.net_if_addrs().items():
                for addr in info:
                    if AddressFamily.AF_INET == addr.family and str(addr.address).startswith(networkSegment):
                        return str(addr.address)

        self.ui.actionproduction.setText(gv.cf.dut.test_mode)
        self.ui.action192_168_1_101.setText(GetAllIpv4Address('10.90.'))

    def init_status_bar(self):
        with Sqlite(gv.database_setting) as db:
            db.execute(f"SELECT VALUE  from COUNT WHERE NAME='continue_fail_count'")
            self.continue_fail_count = db.cur.fetchone()[0]
            db.execute(f"SELECT VALUE  from COUNT WHERE NAME='total_pass_count'")
            self.total_pass_count = db.cur.fetchone()[0]
            db.execute(f"SELECT VALUE  from COUNT WHERE NAME='total_fail_count'")
            self.total_fail_count = db.cur.fetchone()[0]
            db.execute(f"SELECT VALUE  from COUNT WHERE NAME='total_abort_count'")
            self.total_abort_count = db.cur.fetchone()[0]

        self.ui.lb_continuous_fail = QLabel(f'continuous_fail: {self.continue_fail_count}')
        self.ui.lb_count_pass = QLabel(f'PASS: {self.total_pass_count}')
        self.ui.lb_count_fail = QLabel(f'FAIL: {self.total_fail_count}')
        self.ui.lb_count_abort = QLabel(f'ABORT: {self.total_abort_count}')
        try:
            self.ui.lb_count_yield = QLabel('Yield: {:.2%}'.format(self.total_pass_count / (
                    self.total_pass_count + self.total_fail_count + self.total_abort_count)))
        except ZeroDivisionError:
            self.ui.lb_count_yield = QLabel('Yield: 0.00%')
        self.ui.connect_status_image = QLabel('')
        self.ui.connect_status_txt = QLabel('')
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_pass, 2)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_fail, 2)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_abort, 2)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_yield, 16)

    def init_signals_connect(self):
        """connect signals to slots"""
        self.my_signals.timingSignal[bool].connect(self.timing)
        self.my_signals.updateLabel[QLabel, str, int, QBrush].connect(update_label)
        self.my_signals.updateLabel[QLabel, str, int].connect(update_label)
        self.my_signals.updateLabel[QLabel, str].connect(update_label)
        self.my_signals.update_tableWidget[list].connect(self.on_update_tableWidget)
        self.my_signals.update_tableWidget[str].connect(self.on_update_tableWidget)
        self.my_signals.textEditClearSignal[str].connect(self.on_textEditClear)
        self.my_signals.lineEditEnableSignal[bool].connect(self.lineEditEnable)
        self.my_signals.setIconSignal[QAction, QIcon].connect(on_setIcon)
        self.my_signals.updateActionSignal[QAction, QIcon].connect(updateAction)
        self.my_signals.updateActionSignal[QAction, QIcon, str].connect(updateAction)
        self.my_signals.updateStatusBarSignal[str].connect(self.updateStatusBar)
        self.my_signals.saveTextEditSignal[str].connect(self.on_actionSaveLog)
        self.my_signals.controlEnableSignal[QAction, bool].connect(controlEnable)
        self.my_signals.treeWidgetColor[QBrush, int, int, bool].connect(self.update_treeWidget_color)
        self.my_signals.threadStopSignal[str].connect(self.on_actionStop)
        self.my_signals.updateConnectStatusSignal[bool, str].connect(self.on_connect_status)
        self.my_signals.showMessageBox[str, str, int].connect(self.showMessageBox)

        self.ui.actionCheckAll.triggered.connect(self.on_actionCheckAll)
        self.ui.actionUncheckAll.triggered.connect(self.on_actionUncheckAll)
        self.ui.actionStepping.triggered.connect(self.on_actionStepping)
        self.ui.actionLooping.triggered.connect(self.on_actionLooping)
        self.ui.actionEditStep.triggered.connect(self.on_actionEditStep)
        self.ui.actionExpandAll.triggered.connect(self.on_actionExpandAll)
        self.ui.actionCollapseAll.triggered.connect(self.on_actionCollapseAll)
        self.ui.actionBreakpoint.triggered.connect(self.on_actionBreakpoint)

        self.ui.actionOpen_TestCase.triggered.connect(self.on_actionOpen_TestCase)
        self.ui.actionConvertExcelToJson.triggered.connect(self.on_actionConvertExcelToJson)
        self.ui.actionOpenScript.triggered.connect(self.on_actionOpenScript)
        self.ui.actionSaveToScript.triggered.connect(self.on_actionSaveToScript)
        self.ui.actionReloadScript.triggered.connect(self.on_reloadSeqs)
        self.ui.actionConfig.triggered.connect(self.on_actionConfig)
        self.ui.actionPrivileges.triggered.connect(self.on_actionPrivileges)
        self.ui.actionStart.triggered.connect(self.on_actionStart)
        self.ui.actionStop.triggered.connect(self.on_actionStop)
        self.ui.actionOpenLog.triggered.connect(self.on_actionOpenLog)
        self.ui.actionClearLog.triggered.connect(self.on_actionClearLog)
        self.ui.actionLogFolder.triggered.connect(on_actionLogFolder)
        self.ui.actionSaveLog.triggered.connect(self.on_actionSaveLog)
        self.ui.actionCSVLog.triggered.connect(self.on_actionCSVLog)
        self.ui.actionException.triggered.connect(on_actionException)
        self.ui.actionEnable_lab.triggered.connect(self.on_actionEnable_lab)
        self.ui.actionDisable_factory.triggered.connect(self.on_actionDisable_factory)
        self.ui.actionAbout.triggered.connect(self.on_actionAbout)
        self.ui.actionRestart.triggered.connect(self.on_actionRestart)
        self.ui.actionPeakLin.triggered.connect(self.on_peak_lin)

        self.ui.lineEdit.textEdited.connect(self.on_textEdited)
        self.ui.lineEdit.returnPressed.connect(self.on_returnPressed)
        self.ui.treeWidget.customContextMenuRequested.connect(self.on_treeWidgetMenu)
        self.ui.treeWidget.itemChanged.connect(self.on_itemChanged)
        self.ui.treeWidget.itemPressed.connect(self.on_itemActivated)
        self.ui.tableWidget_2.itemChanged.connect(self.on_tableWidget2Edit)

    def init_treeWidget_color(self):
        self.ui.treeWidget.blockSignals(True)
        for i, item in enumerate(self.testSequences):
            self.ui.treeWidget.topLevelItem(i).setBackground(0, Qt.white)
            for j in range(len(self.testSequences[i].steps)):
                self.ui.treeWidget.topLevelItem(i).child(j).setBackground(0, Qt.white)
        self.ui.treeWidget.blockSignals(False)

    def on_itemActivated(self, item, column=0):
        if item.parent() is None:
            # lg.logger.critical('itemActivate')
            self.SuiteNo = self.ui.treeWidget.indexOfTopLevelItem(item)
            self.StepNo = 0
            self.ui.treeWidget.expandItem(item)
            self.ui.actionStepping.setEnabled(False)
            self.ui.actionEditStep.setEnabled(False)
            pp = item.data(column, Qt.DisplayRole).split(' ', 1)[1]
            anchor = f'testSuite:{pp}'
            self.ui.textEdit.scrollToAnchor(anchor)
        else:
            # lg.logger.critical('itemActivate')
            self.SuiteNo = self.ui.treeWidget.indexOfTopLevelItem(item.parent())
            self.StepNo = item.parent().indexOfChild(item)
            self.ui.actionStepping.setEnabled(True)
            self.ui.actionEditStep.setEnabled(True)
            pp = item.parent().data(column, Qt.DisplayRole).split(' ', 1)[1]
            cc = item.data(column, Qt.DisplayRole).split(' ', 1)[1]
            anchor = f'testStep:{pp}-{cc}'
            self.ui.textEdit.scrollToAnchor(anchor)
            self.on_actionEditStep()

    def on_tableWidget_clear(self):
        for i in range(0, self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.removeRow(0)

    def on_update_tableWidget(self, result_tuple):
        def thread_update_tableWidget():
            if isinstance(result_tuple, list):
                row_cnt = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row_cnt)
                column_cnt = self.ui.tableWidget.columnCount()
                for column in range(column_cnt):
                    if IsNullOrEmpty(result_tuple[column]):
                        result_tuple[column] = '--'
                    item = QTableWidgetItem(str(result_tuple[column]))
                    if 'false' in str(result_tuple[-1]).lower() or 'fail' in str(result_tuple[-1]).lower():
                        item.setForeground(Qt.red)
                        # item.setFont(QFont('Times', 12, QFont.Black))
                    self.ui.tableWidget.setItem(row_cnt, column, item)
                    self.ui.tableWidget.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)
                # self.ui.tableWidget.resizeColumnsToContents()
                self.ui.tableWidget.scrollToItem(self.ui.tableWidget.item(row_cnt - 1, 0),
                                                 hint=QAbstractItemView.EnsureVisible)
                # clear all rows if var is str
            elif isinstance(result_tuple, str):
                for i in range(0, self.ui.tableWidget.rowCount()):
                    self.ui.tableWidget.removeRow(0)
            QApplication.processEvents()

        thread = Thread(target=thread_update_tableWidget, daemon=True)
        thread.start()

    def on_reloadSeqs(self):
        if gv.startFlag:
            QMessageBox.information(self, 'Infor', 'Test is running, can not reload!', QMessageBox.Yes)
            return
        self.logger.debug('start reload script,please wait a moment...')
        QApplication.processEvents()

        def thread_convert_and_load_script():
            if os.path.exists(gv.test_script_json):
                os.chmod(gv.test_script_json, stat.S_IWRITE)
                os.remove(gv.test_script_json)
            self.testcase = model.testcase.TestCase(gv.excel_file_path, gv.cf.station.station_name, self.logger)
            self.testSequences = self.testcase.clone_suites

        thread = Thread(target=thread_convert_and_load_script, daemon=True)
        thread.start()
        thread.join()
        if self.testSequences is not None:
            self.ShowTreeView(self.testSequences)
        self.logger.debug('reload finish!')
        self.SaveScriptDisableFlag = False

    def on_itemChanged(self, item, column=0):
        if gv.startFlag:
            return
        if item.parent() is None:
            pNo = self.ui.treeWidget.indexOfTopLevelItem(item)
            isChecked = item.checkState(column) == Qt.Checked
            self.testcase.clone_suites[pNo].isTest = isChecked
            self.ui.treeWidget.blockSignals(True)
            for i in range(0, item.childCount()):
                item.child(i).setCheckState(column, Qt.Checked if isChecked else Qt.Unchecked)
                self.testcase.clone_suites[pNo].steps[i].isTest = isChecked
            self.ui.treeWidget.blockSignals(False)
        else:
            ParentIsTest = []
            pNo = self.ui.treeWidget.indexOfTopLevelItem(item.parent())
            cNO = item.parent().indexOfChild(item)
            self.testcase.clone_suites[pNo].steps[cNO].isTest = item.checkState(column) == Qt.Checked
            for i in range(item.parent().childCount()):
                isChecked = item.parent().child(i).checkState(column) == Qt.Checked
                ParentIsTest.append(isChecked)
            isChecked_parent = any(ParentIsTest)
            self.ui.treeWidget.blockSignals(True)
            self.testcase.clone_suites[pNo].isTest = isChecked_parent
            item.parent().setCheckState(column, Qt.Checked if isChecked_parent else Qt.Unchecked)
            self.ui.treeWidget.blockSignals(False)

    def on_treeWidgetMenu(self):
        if gv.IsDebug:
            menu = QMenu(self.ui.treeWidget)
            menu.addAction(self.ui.actionStepping)
            menu.addAction(self.ui.actionLooping)
            menu.addAction(self.ui.actionBreakpoint)
            # menu.addAction(self.ui.actionEditStep)
            menu.addAction(self.ui.actionCheckAll)
            menu.addAction(self.ui.actionUncheckAll)
            menu.addAction(self.ui.actionExpandAll)
            menu.addAction(self.ui.actionCollapseAll)
            if getattr(self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo], 'breakpoint') == str(False):
                self.ui.actionBreakpoint.setIcon(QIcon(':/images/breakpoint-set.png'))
            else:
                self.ui.actionBreakpoint.setIcon(QIcon(':/images/breakpoint-clear.png'))
            menu.exec_(QCursor.pos())

    def on_actionCheckAll(self):
        self.ShowTreeView(self.testSequences, True)

    def on_actionUncheckAll(self):
        self.ShowTreeView(self.testSequences, False)

    def on_actionStepping(self):
        self.on_returnPressed('stepping')

    def on_actionLooping(self):
        gv.FailNumOfCycleTest = 0
        gv.PassNumOfCycleTest = 0
        gv.IsCycle = True
        self.on_returnPressed()

    def on_actionBreakpoint(self):
        if not getattr(self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo], 'breakpoint'):
            setattr(self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo], 'breakpoint', True)
            self.ui.actionBreakpoint.setIcon(QIcon(':/images/breakpoint-clear.png'))
            self.ui.treeWidget.currentItem().setIcon(0, QIcon(':/images/breakpoint-set.png'))
        else:
            setattr(self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo], 'breakpoint', False)
            self.ui.actionBreakpoint.setIcon(QIcon(':/images/breakpoint-set.png'))
            self.ui.treeWidget.currentItem().setIcon(0, QIcon(':/images/Document-txt-icon.png'))

    def on_actionOpen_TestCase(self):
        def thread_actionOpen_TestCase():
            os.startfile(self.testcase.testcase_path)

        thread = Thread(target=thread_actionOpen_TestCase, daemon=True)
        thread.start()

    def on_actionConvertExcelToJson(self):
        if gv.startFlag:
            QMessageBox.information(self, 'Infor', 'Test is running, can not do it!', QMessageBox.Yes)
            return
        thread = Thread(
            target=model.loadseq.excel_convert_to_json, args=(self.testcase.testcase_path,
                                                              gv.cf.station.station_all, self.logger), daemon=True)
        thread.start()

    def on_actionOpenScript(self):

        def actionOpenScript():
            os.startfile(self.testcase.test_script_json)

        if getattr(sys, 'frozen', False):
            return
        thread = Thread(target=actionOpenScript, daemon=True)
        thread.start()

    def on_select_station(self):
        def select_station():
            action = self.sender()
            if isinstance(action, QAction):
                gv.cf.station.station_name = action.text() if "(" not in action.text() else action.text()[
                                                                                            :action.text().index('(')]
                if gv.cf.station.station_name.startswith('ReadVer_'):
                    gv.IsDebug = True
                gv.cf.station.station_no = gv.cf.station.station_name
                gv.test_script_json = rf'{gv.scriptFolder}\{gv.cf.station.station_name}.json'
                self.testcase.original_suites = model.loadseq.load_testcase_from_json(gv.test_script_json)
                self.testcase.clone_suites = copy.deepcopy(self.testcase.original_suites)
                self.testSequences = self.testcase.clone_suites
                self.logger.debug(f'select {gv.test_script_json} finish!')

        thread = Thread(target=select_station, daemon=True)
        thread.start()
        thread.join()
        if self.testSequences is not None:
            self.ShowTreeView(self.testSequences)

    def on_actionSaveToScript(self):
        if self.SaveScriptDisableFlag:
            QMessageBox.information(self, 'Infor', 'Please save it before start test!', QMessageBox.Yes)
        else:
            thread = Thread(target=model.loadseq.serialize_to_json,
                            args=(self.testcase.clone_suites, gv.test_script_json, self.logger), daemon=True)
            thread.start()

    def on_actionConfig(self):
        settings_wind = SettingsDialog(self)
        settings_wind.exec_()
        if settings_wind.isChange:
            ask = QMessageBox.question(self, "Save configuration to file?",
                                       "The configuration has been changed.Do you want to save it permanently?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ask == QMessageBox.Yes:
                save_config(self.logger, gv.config_yaml_path, gv.cf)
        settings_wind.destroy()

    def on_peak_lin(self):
        if gv.PLin is None:
            gv.PLin = PeakLin(self.logger, self)
            gv.PLin.exec_()
        else:
            gv.PLin.show()

    def on_actionPrivileges(self):
        if gv.IsDebug:
            QMessageBox.information(self, 'Authority', 'This is lab test privileges.', QMessageBox.Yes)
        else:
            QMessageBox.information(self, 'Authority', 'This is factory test privileges.', QMessageBox.Yes)

    def on_actionStart(self):
        if gv.startFlag:
            if not gv.pauseFlag:
                gv.pauseFlag = True
                self.ui.actionStart.setIcon(QIcon(':/images/Start-icon.png'))
                gv.pause_event.clear()
            else:
                gv.pauseFlag = False
                self.ui.actionStart.setIcon(QIcon(':/images/Pause-icon.png'))
                gv.pause_event.set()
        else:
            self.on_returnPressed()

    def on_actionStop(self):
        if gv.IsCycle:
            if gv.startFlag:
                saveTestResult(self.logger)
                if self.FailNumOfCycleTest == 0:
                    gv.finalTestResult = True
                    self.testThread.signal[MainForm, TestStatus].emit(self, TestStatus.PASS)
                else:
                    self.testThread.signal[MainForm, TestStatus].emit(self, TestStatus.FAIL)
                gv.IsCycle = False
        else:
            self.testThread.signal[MainForm, TestStatus].emit(self, TestStatus.ABORT)

    def on_actionClearLog(self):
        if not gv.startFlag:
            self.ui.textEdit.clear()

    def on_actionOpenLog(self):
        def thread_update():
            if os.path.exists(gv.txtLogPath):
                os.startfile(gv.txtLogPath)
            else:
                self.logger.warning(f"no find test log")

        thread = Thread(target=thread_update, daemon=True)
        thread.start()

    def on_actionCSVLog(self):
        def thread_update():
            if os.path.exists(gv.CSVFilePath):
                os.startfile(gv.CSVFilePath)
            else:
                self.logger.warning(f"no find test log")

        thread = Thread(target=thread_update, daemon=True)
        thread.start()

    def on_actionSaveLog(self, info):
        def thread_update():
            if info == 'rename':
                rename_log = gv.txtLogPath.replace('logging',
                                                   str(gv.finalTestResult).upper()).replace('details',
                                                                                            gv.error_details_first_fail)
                self.logger.debug(f"rename test log to: {rename_log}")
                self.fileHandle.close()
                os.rename(gv.txtLogPath, rename_log)
            else:
                gv.txtLogPath = rf'{gv.logFolderPath}\{str(gv.finalTestResult).upper()}_{gv.SN}_' \
                                rf'{gv.error_details_first_fail}_{time.strftime("%H-%M-%S")}.txt'
                content = self.ui.textEdit.toPlainText()
                with open(gv.txtLogPath, 'wb') as f:
                    f.write(content.encode('utf8'))
                self.logger.debug(f"Save test log OK.{gv.txtLogPath}")

        thread = Thread(target=thread_update, daemon=True)
        thread.start()

    def on_actionEnable_lab(self):
        gv.IsDebug = True
        self.ui.actionPrivileges.setIcon(QIcon(':/images/lab-icon.png'))
        self.debug_switch(gv.IsDebug)

    def on_actionDisable_factory(self):
        gv.IsDebug = False
        self.ui.actionPrivileges.setIcon(QIcon(':/images/factory.png'))
        self.debug_switch(gv.IsDebug)

    def on_actionAbout(self):
        QMessageBox.about(self, 'About', 'Python3.11+PyQt5\nTechnical support: StevenShen\nWeChat:chenhlzqbx')

    def on_actionRestart(self):
        def thread_update():
            run_cmd(self.logger,
                    rf'{gv.current_dir}\tool\restart.exe -n AutoPlasticOmnium.exe -p AutoPlasticOmnium.exe')

        thread = Thread(target=thread_update)
        ask = QMessageBox.question(self, "Restart Application?",
                                   "Do you want restart this program?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ask == QMessageBox.Yes:
            thread.start()

    def debug_switch(self, isDebug: bool):
        self.ui.actionConvertExcelToJson.setEnabled(isDebug)
        self.ui.actionSaveToScript.setEnabled(isDebug)
        self.ui.actionReloadScript.setEnabled(isDebug)
        self.ui.actionStart.setEnabled(isDebug)
        self.ui.actionStop.setEnabled(isDebug)
        self.ui.actionClearLog.setEnabled(isDebug)
        self.ui.actionSaveLog.setEnabled(isDebug)
        self.ui.actionConfig.setEnabled(isDebug)
        self.ShowTreeView(self.testSequences)

    def on_actionEditStep(self):
        self.ui.tableWidget_2.blockSignals(True)
        if self.ui.tabWidget.currentWidget() != self.ui.stepInfo:
            self.ui.tabWidget.setCurrentWidget(self.ui.stepInfo)
        for i in range(0, self.ui.tableWidget_2.rowCount()):
            self.ui.tableWidget_2.removeRow(0)
        step_obj = self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo]
        for prop_name in list(dir(step_obj)):
            prop_value = getattr(step_obj, prop_name)
            if isinstance(prop_value, str) and not prop_name.startswith('_'):
                column_cnt = self.ui.tableWidget_2.columnCount()
                row_cnt = self.ui.tableWidget_2.rowCount()
                self.ui.tableWidget_2.insertRow(row_cnt)
                key_pairs = [prop_name, prop_value]
                for column in range(column_cnt):
                    self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeToContents)
                    item = QTableWidgetItem(key_pairs[column])
                    if column == 0:
                        item.setFlags(Qt.ItemIsEnabled)
                        item.setBackground(Qt.lightGray)
                    self.ui.tableWidget_2.setItem(row_cnt, column, item)
        self.ui.tableWidget_2.sortItems(1, order=Qt.DescendingOrder)
        self.ui.tableWidget_2.blockSignals(False)

    def on_tableWidget2Edit(self, item):
        prop_name = self.ui.tableWidget_2.item(item.row(), item.column() - 1).text()
        prop_value = item.text()
        setattr(self.testcase.clone_suites[self.SuiteNo].steps[self.StepNo], prop_name, prop_value)

    def on_actionExpandAll(self):
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.scrollToItem(self.ui.treeWidget.topLevelItem(0), hint=QAbstractItemView.EnsureVisible)

    def on_actionCollapseAll(self):
        self.ui.treeWidget.collapseAll()

    def on_connect_status(self, flag: bool, strs):
        if flag:
            self.ui.connect_status_image.setPixmap(QPixmap(":/images/connect_ok.png"))
        else:
            self.ui.connect_status_image.setPixmap(QPixmap(":/images/disconnect-icon.png"))
        self.ui.connect_status_txt.setText(strs)
        self.ui.statusbar.addPermanentWidget(self.ui.connect_status_image, 1)
        self.ui.statusbar.addPermanentWidget(self.ui.connect_status_txt, 2)

    def ShowTreeView(self, sequences=None, checkall=None):
        if sequences is None:
            return
        self.ui.treeWidget.blockSignals(True)
        self.ui.treeWidget.clear()
        self.ui.treeWidget.setHeaderLabel(f'{gv.cf.station.station_no}')
        for suite in sequences:
            suite_node = QTreeWidgetItem(self.ui.treeWidget)
            suite_node.setData(0, Qt.DisplayRole, f'{suite.index + 1}. {suite.SuiteName}')
            suite_node.setIcon(0, QIcon(':/images/folder-icon.png'))
            if checkall:
                suite_node.setCheckState(0, Qt.Checked)
                suite.isTest = True
            else:
                if checkall is None:
                    suite_node.setCheckState(0, Qt.Checked if suite.isTest else Qt.Unchecked)
                else:
                    suite_node.setCheckState(0, Qt.Unchecked)
                    suite.isTest = False
            if gv.IsDebug:
                suite_node.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            else:
                suite_node.setFlags(Qt.ItemIsSelectable)
            for step in suite.steps:
                step_node = QTreeWidgetItem(suite_node)
                step_node.setData(0, Qt.DisplayRole, f'{step.index + 1}) {step.StepName}')
                if checkall:
                    step_node.setCheckState(0, Qt.Checked)
                    step.isTest = True
                else:
                    if checkall is None:
                        step_node.setCheckState(0, Qt.Checked if step.isTest else Qt.Unchecked)
                    else:
                        step_node.setCheckState(0, Qt.Unchecked)
                        step.isTest = False
                if gv.IsDebug:
                    step_node.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                else:
                    step_node.setFlags(Qt.ItemIsSelectable)
                step_node.setIcon(0, QIcon(':/images/Document-txt-icon.png'))
                suite_node.addChild(step_node)
        self.ui.treeWidget.setStyle(QStyleFactory.create('windows'))
        self.ui.treeWidget.resizeColumnToContents(0)
        self.ui.treeWidget.topLevelItem(0).setExpanded(True)
        self.ui.treeWidget.blockSignals(False)

    # @QtCore.pyqtSlot(QBrush, int, int, bool)
    def update_treeWidget_color(self, color: QBrush, suiteNO_: int, stepNo_: int = -1, allChild=False):
        if stepNo_ == -1:
            if gv.IsCycle or not gv.startFlag:
                return
            self.ui.treeWidget.topLevelItem(suiteNO_).setExpanded(True)
            self.ui.treeWidget.topLevelItem(suiteNO_).setBackground(0, color)
            if allChild:
                for i in range(self.ui.treeWidget.topLevelItem(suiteNO_).childCount()):
                    self.ui.treeWidget.topLevelItem(suiteNO_).child(i).setBackground(0, color)
        else:
            self.ui.treeWidget.topLevelItem(suiteNO_).child(stepNo_).setBackground(0, color)
            self.ui.treeWidget.scrollToItem(self.ui.treeWidget.topLevelItem(suiteNO_).child(stepNo_),
                                            hint=QAbstractItemView.EnsureVisible)

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

    @QtCore.pyqtSlot(str, str, result=list)
    def showQInputDialog(self, title, label):
        results = QInputDialog.getText(self, title, label)
        return list(results)

    def lineEditEnable(self, isEnable):
        def thread_update():
            self.ui.lineEdit.setEnabled(isEnable)
            if isEnable:
                self.ui.lineEdit.setText('')
                self.ui.lineEdit.setFocus()

        thread = Thread(target=thread_update, daemon=True)
        thread.start()

    def on_textEditClear(self, info):
        self.logger.debug(f'{currentframe().f_code.co_name}:{info}')
        self.ui.textEdit.clear()

    def updateStatusBar(self, info):
        def update_status_bar():
            self.logger.debug(f'{currentframe().f_code.co_name}:{info}')
            with model.sqlite.Sqlite(gv.database_setting) as db:
                db.execute(f"UPDATE COUNT SET VALUE='{self.continue_fail_count}' where NAME ='continue_fail_count'")
                db.execute(f"UPDATE COUNT SET VALUE='{self.total_pass_count}' where NAME ='total_pass_count'")
                db.execute(f"UPDATE COUNT SET VALUE='{self.total_fail_count}' where NAME ='total_fail_count'")
                db.execute(f"UPDATE COUNT SET VALUE='{self.total_abort_count}' where NAME ='total_abort_count'")
            self.ui.lb_continuous_fail.setText(f'continuous_fail: {self.continue_fail_count}')
            self.ui.lb_count_pass.setText(f'PASS: {self.total_pass_count}')
            self.ui.lb_count_fail.setText(f'FAIL: {self.total_fail_count}')
            self.ui.lb_count_abort.setText(f'ABORT: {self.total_abort_count}')
            try:
                self.ui.lb_count_yield.setText('Yield: {:.2%}'.format(self.total_pass_count / (
                        self.total_pass_count + self.total_fail_count + self.total_abort_count)))
            except ZeroDivisionError:
                self.ui.lb_count_yield.setText('Yield: 0.00%')
            # QApplication.processEvents()

        thread = Thread(target=update_status_bar, daemon=True)
        thread.start()

    def timerEvent(self, a):
        self.my_signals.updateLabel[QLabel, str, int].emit(self.ui.lb_errorCode, str(self.sec), 20)
        QApplication.processEvents()
        self.sec += 1

    def timing(self, flag):
        if flag:
            self.logger.debug('start timing...')
            self.timer = self.startTimer(1000)
        else:
            self.logger.debug('stop timing...')
            self.killTimer(self.timer)

    def get_stationNo(self):
        """通过串口读取治具中设置的测试工站名字"""
        if not gv.cf.station.fix_flag:
            return
        gv.FixSerialPort = sockets.serialport.SerialPort(gv.cf.station.fix_com_port,
                                                         gv.cf.station.fix_com_baudRate)
        for i in range(0, 3):
            rReturn, revStr = gv.FixSerialPort.SendCommand('AT+READ_FIXNUM%', '\r\n', 1, False)
            if rReturn:
                gv.cf.station.station_no = revStr.replace('\r\n', '').strip()
                gv.cf.station.station_name = gv.cf.station.station_no[0, gv.cf.station.station_no.index('-')]
                self.logger.debug(f"Read fix number success,stationName:{gv.cf.station.station_name}")
                break
        else:
            QMessageBox.Critical(self, 'Read StationNO', "Read FixNum error,Please check it!")
            sys.exit(0)

    def UpdateContinueFail(self, testResult: bool):
        if gv.IsDebug or gv.cf.dut.test_mode.lower() == 'debug':
            return
        if testResult:
            self.continue_fail_count = 0
        else:
            self.continue_fail_count += 1

    def ContinuousFailReset_Click(self):
        """连续fail超过规定值需要TE确认问题并输入密码后才能继续测试"""
        text, ok = QInputDialog.getText(self, 'Reset', 'Please input Reset Password:', echo=QLineEdit.Password)
        if ok:
            if text == 'test123':
                self.continue_fail_count = 0
                self.ui.lb_continuous_fail.setText(f'continuous_fail: {self.continue_fail_count}')
                self.ui.lb_continuous_fail.setStyleSheet(
                    f"background-color:{self.ui.statusbar.palette().window().color().name()};")
                return True
            else:
                QMessageBox.critical(self, 'ERROR!', 'wrong password!')
                return False
        else:
            return False

    def CheckContinueFailNum(self):
        with model.sqlite.Sqlite(gv.database_setting) as db:
            db.execute(f"SELECT VALUE  from COUNT WHERE NAME='continue_fail_count'")
            self.continue_fail_count = db.cur.fetchone()[0]
            self.logger.debug(str(self.continue_fail_count))
        if self.continue_fail_count >= gv.cf.station.continue_fail_limit:
            self.ui.lb_continuous_fail.setStyleSheet(f"background-color:red;")
            if gv.IsDebug:
                return True
            else:
                return self.ContinuousFailReset_Click()
        else:
            self.ui.lb_continuous_fail.setStyleSheet(
                f"background-color:{self.ui.statusbar.palette().window().color().name()};")
            return True

    def on_textEdited(self):
        sn = self.ui.lineEdit.text()

        def JudgeProdMode():
            """通过SN判断机种"""
            if IsNullOrEmpty(sn):
                gv.dut_model = 'unknown'
                return gv.dut_model
            if sn[0] == 'J' or sn[0] == '6':
                gv.dut_mode = gv.cf.dut.dut_models[0]
            elif sn[0] == 'N' or sn[0] == '7':
                gv.dut_mode = gv.cf.dut.dut_models[1]
            elif sn[0] == 'Q' or sn[0] == '8':
                gv.dut_mode = gv.cf.dut.dut_models[2]
            elif sn[0] == 'S' or sn[0] == 'G':
                gv.dut_mode = gv.cf.dut.dut_models[3]
            else:
                gv.dut_model = 'unknown'
            self.ui.actionunknow.setText(gv.dut_model)
            return gv.dut_model

        if JudgeProdMode() != 'unknown' and not gv.IsDebug:
            reg = QRegExp(gv.cf.dut.dut_regex[gv.dut_model])
            pValidator = QRegExpValidator(reg, self)
            self.ui.lineEdit.setValidator(pValidator)

    def on_returnPressed(self, stepping_flag=None):
        if stepping_flag is not None:
            self.SingleStepTest = True
        else:
            self.SingleStepTest = False
        if not gv.dut_model == 'unknown' and not gv.IsDebug:
            str_info = f'无法根据SN判断机种或者SN长度不对! 扫描:{len(self.ui.lineEdit.text())},规定:{gv.cf.dut.sn_len}.'
            QMetaObject.invokeMethod(self, 'showMessageBox', Qt.AutoConnection,
                                     QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
                                     QtCore.Q_ARG(str, 'JudgeMode!'),
                                     QtCore.Q_ARG(str, str_info),
                                     QtCore.Q_ARG(int, 5))
            return
        # if not self.CheckContinueFailNum() and not gv.IsDebug:
        # return

        if gv.IsDebug:
            if not self.SingleStepTest:
                self.init_treeWidget_color()
        else:
            self.testSequences = copy.deepcopy(self.testcase.original_suites)
            self.testcase.clone_suites = self.testSequences
            self.ShowTreeView(self.testSequences)
        gv.SN = self.ui.lineEdit.text()
        self.variable_init(gv.SN)

    def variable_init(self, SN):
        """测试变量初始化"""
        if self.SingleStepTest and self.testcase.Finished:
            pass
        else:
            gv.TestVariables = model.variables.Variables(gv.cf.station.station_name,
                                                         gv.cf.station.station_no, SN,
                                                         gv.cf.dut.dut_ip, gv.cf.station.log_folder)
        gv.stationObj = model.product.JsonObject(SN, gv.cf.station.station_no,
                                                 gv.cf.dut.test_mode,
                                                 gv.cf.dut.qsdk_ver, gv.version)
        gv.mes_result = f'http://{gv.cf.station.mes_result}/api/2/serial/{SN}/station/{gv.cf.station.station_no}/info'
        gv.shop_floor_url = f'http://{gv.cf.station.mes_shop_floor}/api/CHKRoute/serial/{SN}/station/{gv.cf.station.station_name}'
        gv.mesPhases = model.product.MesInfo(SN, gv.cf.station.station_no, gv.version)
        self.init_create_dirs()
        gv.csv_list_header = []
        gv.csv_list_data = []
        gv.daq_data_path = rf'{gv.OutPutPath}\{gv.cf.station.station_no}_DAQ_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
        gv.error_code_first_fail = ''
        gv.error_details_first_fail = ''
        gv.finalTestResult = False
        gv.setIpFlag = False
        gv.DUTMesIP = ''
        gv.MesMac = ''
        gv.sec = 0
        if not self.SingleStepTest:
            self.SuiteNo = -1
            self.StepNo = -1
        gv.WorkOrder = '1'
        gv.startTimeJsonFlag = True
        gv.startTimeJson = datetime.now()
        self.ui.lb_failInfo.setHidden(True)
        self.ui.lb_testTime.setHidden(True)
        self.sec = 1
        gv.txtLogPath = rf'{gv.logFolderPath}\logging_{SN}_details_{time.strftime("%H-%M-%S")}.txt'
        gv.lg = LogPrint(gv.txtLogPath.replace('\\', '/'), gv.critical_log, gv.errors_log)
        self.logger = gv.lg.logger
        self.testcase.logger = self.logger
        self.init_textEditHandler()
        self.testThread.signal[MainForm, TestStatus].emit(self, TestStatus.START)
        self.ui.tabWidget.setCurrentWidget(self.ui.result)


def SetTestStatus(myWind: MainForm, status: TestStatus):
    """设置并处理不同的测试状态"""
    try:
        if status == TestStatus.START:
            if not myWind.testThread.isRunning():
                myWind.testThread = TestThread(myWind)
                myWind.testThread.start()
            myWind.ui.treeWidget.blockSignals(True)
            if not myWind.SingleStepTest:
                myWind.my_signals.textEditClearSignal[str].emit('')
            myWind.my_signals.lineEditEnableSignal[bool].emit(False)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'Testing', 36,
                                                                         Qt.yellow)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode, '', 20,
                                                                         Qt.yellow)
            myWind.my_signals.timingSignal[bool].emit(True)
            gv.startTime = datetime.now()
            myWind.my_signals.setIconSignal[QAction, QIcon].emit(myWind.ui.actionStart,
                                                                 QIcon(':/images/Pause-icon.png'))
            myWind.my_signals.controlEnableSignal[QAction, bool].emit(myWind.ui.actionStop, True)
            gv.startFlag = True
            myWind.logger.debug(f"Start test,SN:{gv.SN},Station:{gv.cf.station.station_no},DUTMode:{gv.dut_model},"
                                f"TestMode:{gv.cf.dut.test_mode},IsDebug:{gv.IsDebug},"
                                f"FTC:{gv.cf.station.fail_continue},SoftVersion:{gv.version}")
            myWind.my_signals.update_tableWidget[str].emit('clear')
            gv.pause_event.set()
        elif status == TestStatus.FAIL:
            myWind.total_fail_count += 1
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'FAIL', 36,
                                                                         Qt.red)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_testTime,
                                                                         str(myWind.sec), 11,
                                                                         Qt.gray)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                         gv.error_details_first_fail, 20, Qt.red)
            myWind.UpdateContinueFail(False)
            if gv.setIpFlag:
                gv.dut_comm.send_command(f"ip {gv.cf.dut.dut_ip} 255.255.255.0", gv.cf.dut.prompt, 1)
        elif status == TestStatus.PASS:
            myWind.total_pass_count += 1
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'PASS', 36,
                                                                         Qt.green)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                         str(myWind.sec), 20,
                                                                         Qt.green)
            myWind.UpdateContinueFail(True)
        elif status == TestStatus.ABORT:
            myWind.total_abort_count += 1
            myWind.testThread.terminate()
            myWind.testThread.wait(1)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_status, 'Abort', 36,
                                                                         Qt.gray)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_testTime,
                                                                         str(myWind.sec), 11,
                                                                         Qt.gray)
            myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                         gv.error_details_first_fail, 20,
                                                                         Qt.gray)
            saveTestResult(myWind.logger)
    except Exception as e:
        myWind.logger.fatal(f"SetTestStatus Exception！！{e},{traceback.format_exc()}")
    finally:
        try:
            myWind.SaveScriptDisableFlag = True
            if status != TestStatus.START:
                myWind.my_signals.setIconSignal[QAction, QIcon].emit(myWind.ui.actionStart,
                                                                     QIcon(':/images/Start-icon.png'))
                myWind.my_signals.controlEnableSignal[QAction, bool].emit(myWind.ui.actionStop, False)
                myWind.my_signals.timingSignal[bool].emit(False)
                myWind.logger.debug(f"Test end,ElapsedTime:{myWind.sec}s.")
                gv.startFlag = False
                myWind.my_signals.lineEditEnableSignal[bool].emit(True)
                myWind.my_signals.updateStatusBarSignal[str].emit('')
                myWind.my_signals.saveTextEditSignal[str].emit('rename')
                if not gv.finalTestResult:
                    myWind.my_signals.updateLabel[QLabel, str, int, QBrush].emit(myWind.ui.lb_errorCode,
                                                                                 gv.error_details_first_fail, 20,
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


class TestThread(QThread):
    signal = pyqtSignal(MainForm, TestStatus)

    def __init__(self, myWind: MainForm):
        super(TestThread, self).__init__()
        self.myWind = myWind
        self.signal[MainForm, TestStatus].connect(SetTestStatus)

    def __del__(self):
        self.wait()

    def run(self):
        """
        进行任务操作，主要的逻辑操作,返回结果
        """
        try:
            while True:
                if gv.startFlag:
                    if gv.IsCycle:
                        while gv.IsCycle:
                            if self.myWind.testcase.run(gv.cf.station.fail_continue):
                                self.myWind.PassNumOfCycleTest += 1
                            else:
                                self.myWind.FailNumOfCycleTest += 1
                            if self.myWind.PassNumOfCycleTest + self.myWind.FailNumOfCycleTest == gv.cf.station.loop_count:
                                self.myWind.logger.debug(
                                    f"***** All loop({gv.cf.station.loop_count}) have completed! *****")
                                self.myWind.my_signals.threadStopSignal[str].emit('stop test.')
                                time.sleep(0.5)
                            else:
                                time.sleep(gv.cf.station.loop_interval)
                    elif self.myWind.SingleStepTest:
                        self.myWind.logger.debug(f'Suite:{self.myWind.SuiteNo},Step:{self.myWind.StepNo}')
                        result = self.myWind.testcase.clone_suites[self.myWind.SuiteNo].steps[
                            self.myWind.StepNo].run(
                            self.myWind.testcase.clone_suites[self.myWind.SuiteNo])
                        gv.finalTestResult = result
                        self.signal[MainForm, TestStatus].emit(self.myWind,
                                                               TestStatus.PASS if gv.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                    else:
                        result = self.myWind.testcase.run(gv.cf.station.fail_continue)
                        result1 = upload_Json_to_client(self.myWind.logger, gv.cf.station.rs_url, gv.txtLogPath)
                        result2 = upload_result_to_mes(self.myWind.logger, gv.mes_result)
                        gv.finalTestResult = result & result1 & result2
                        collect_data_to_csv(self.myWind.logger)
                        saveTestResult(self.myWind.logger)
                        self.signal[MainForm, TestStatus].emit(self.myWind,
                                                               TestStatus.PASS if gv.finalTestResult else TestStatus.FAIL)
                        time.sleep(0.5)
                else:
                    continue
        except Exception as e:
            self.myWind.logger.fatal(f"TestThread() Exception:{e},{traceback.format_exc()}")
            self.signal[MainForm, TestStatus].emit(self.myWind, TestStatus.ABORT)
        finally:
            pass
            # gv.testThread.join(3)
            # lg.logger.debug('finally')


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainForm()
    mainWin.ui.show()
    app.exec_()
