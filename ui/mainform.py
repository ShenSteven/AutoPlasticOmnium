import copy
import logging
import os
import sys
from datetime import datetime
from enum import Enum
from os.path import dirname, abspath, join
from threading import Thread
from PySide2.QtCore import Qt, Signal, QObject, QRegExp, SIGNAL
from PySide2.QtGui import QIcon, QCursor, QBrush, QRegExpValidator
from PySide2.QtWidgets import QMessageBox, QStyleFactory, QTreeWidgetItem, QMenu, QApplication, QTextEdit, \
    QAbstractItemView, QHeaderView, QTableWidgetItem, QLabel, QWidget
from PySide2.QtUiTools import QUiLoader
import conf
import conf.globalvar as gv
import model.product
import ui.images  # pyside2-rcc images.qrc -o images.py
from sokets.serialport import SerialPort
import conf.logconf as lg
import model.testcase


class MySignals(QObject):
    loadseq = Signal(str)
    update_tableWidget = Signal(tuple)
    log_print = Signal(QTextEdit, str, QBrush)
    update_treeWidgetItem_backColor = Signal(QBrush, int, int)
    update_label = Signal([QLabel, str, int, QBrush], [QLabel, str, int], [QLabel, str])


my_signals = MySignals()
sec = 0


def update_label(label: QLabel, str_: str, font_size: int = 36, color: QBrush = None):
    def thread_update():
        label.setText(str_)
        if color is not None:
            lg.logger.debug(color.color().colorNames())
            label.setStyleSheet(f"background-color:{color.color().name()};font: {font_size}pt '宋体';")

    thread = Thread(target=thread_update)
    thread.start()


def init_create_dirs():
    if not model.IsNullOrEmpty(gv.cf.station.setTimeZone):
        os.system(f"tzutil /s \"{gv.cf.station.setTimeZone}\"")
    gv.logFolderPath = f"{gv.cf.station.log_folder}\{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(gv.logFolderPath + r"\Json", exist_ok=True)
    os.makedirs(gv.current_path + r"\OutPut", exist_ok=True)
    os.makedirs(gv.current_path + r"\Data", exist_ok=True)
    os.makedirs(gv.cf.station.log_folder + r"\CsvData\Upload", exist_ok=True)


class MainForm(QWidget):
    # main_form = None

    def __init__(self):
        super().__init__()
        init_create_dirs()
        self.a = 1
        self.testcase: model.testcase.TestCase
        self.testSequences = []
        self.ui = QUiLoader().load(join(dirname(abspath(__file__)), 'main.ui'))
        # self.main_form = self
        gv.main_form = self
        self.init_textEditHandler()
        self.init_lineEdit()
        self.init_lab_factory(gv.cf.station.privileges)
        self.init_tableWidget()
        self.init_childLabel()
        self.init_label_info()
        self.init_status_bar()
        self.init_signals_connect()
        self.test()

    def test(self):
        # QMessageBox.about(self.ui, '统计结果', ss)
        # te.setTextColor(QColor('red'))  # 改变字体颜色
        # QTextEditHandler.clear()           #文本清除
        my_signals.update_tableWidget[tuple].emit(("SN", "ItemName", "Spec", "Limit_min", "tValue", "Limit_max",
                                                   "ElapsedTime", "StartTime", "fail"))
        # self.ui.statusbar.showMessage("xxxxxxxxxxxxxx!", 20000)
        # self.ui.statusbar.setSizeGripEnabled(False)
        # my_signals.update_treeWidgetItem_backColor[QBrush, int, int].emit(Qt.red, 3, 1)
        # self.ui.lb_status.setStyleSheet("background-color:red;font: 36pt '宋体';")
        self.ui.lb_status.setText('PASS')
        my_signals.update_label[QLabel, str, int, QBrush].emit(self.ui.lb_errorCode, '12.3.MMC.device', 20, Qt.red)
        my_signals.update_label[QLabel, str].emit(self.ui.lb_errorCode, '12')
        print(self.ui.statusbar.palette().window().color().name())

    def init_lineEdit(self):

        self.ui.lineEdit.setMaxLength(gv.cf.dut.sn_len)
        self.ui.lineEdit.setFocus()
        # reg = QRegExp('[A-Z0-9]+$')
        # pValidator = QRegExpValidator(self.ui.lineEdit)  # 自定义文本验证器
        # pValidator.setRegExp(reg)
        # self.ui.lineEdit.setValidator(pValidator)

    def verify_lineEdit(self):
        print('verify_lineEdit')
        sn = self.ui.lineEdit.text()

        def JudgeProdMode():
            if model.IsNullOrEmpty(sn):
                self.ui.statusbar.showMessage("xxxxxxxxxxxxxx!", 30000)
                gv.dut_mode = 'unknown'
                return gv.dut_mode

            if sn[0] == 'J' or sn[0] == '6':
                gv.dut_mode = gv.cf.dut.dut_modes[0]
            elif sn[0] == 'N' or sn[0] == '7':
                gv.dut_mode = gv.cf.dut.dut_modes[1]
            elif sn[0] == 'Q' or sn[0] == '8':
                gv.dut_mode = gv.cf.dut.dut_modes[2]
            elif sn[0] == 'S' or sn[0] == 'G':
                gv.dut_mode = gv.cf.dut.dut_modes[3]
            else:
                gv.dut_mode = 'unknown'
            self.ui.actionunknow.setText(gv.dut_mode)
            return gv.dut_mode

        if JudgeProdMode() != 'unknown':
            print('set_RegEx')
            reg = QRegExp(gv.cf.dut.dut_regex[gv.dut_mode])
            pValidator = QRegExpValidator(reg, self)  # 自定义文本验证器
            # pValidator.setRegExp(reg)
            self.ui.lineEdit.setValidator(pValidator)

    def init_signals_connect(self):
        my_signals.loadseq[str].connect(self.load_seqs)
        my_signals.loadseq[str].emit("Convert excel testcase to json script.")
        my_signals.update_label[QLabel, str, int, QBrush].connect(update_label)
        my_signals.update_label[QLabel, str, int].connect(update_label)
        my_signals.update_label[QLabel, str].connect(update_label)
        # self.ui.lineEdit.returnPressed.connect(self.time_start())
        self.ui.treeWidget.itemClicked.connect(self.handle_itemClicked)
        self.ui.treeWidget.customContextMenuRequested.connect(self.handle_treeWidgetMenu)
        my_signals.update_treeWidgetItem_backColor[QBrush, int, int].connect(self.update_treeWidgetItem_backColor)
        self.ui.actionCheckAll.triggered.connect(self.handle_actionCheckAll)
        self.ui.actionUncheckAll.triggered.connect(self.handle_actionUncheckAll)
        self.ui.actionStepping.triggered.connect(self.handle_actionStepping)
        self.ui.actionLooping.triggered.connect(self.handle_actionLooping)
        self.ui.actionEditStep.triggered.connect(self.handle_actionEditStep)
        self.ui.actionOpen_TestCase.triggered.connect(self.handle_actionOpen_TestCase)
        self.ui.actionConvertExcelToJson.triggered.connect(self.handle_actionConvertExcelToJson)
        self.ui.actionOpenScript.triggered.connect(self.handle_actionOpenScript)
        self.ui.lineEdit.textEdited.connect(self.verify_lineEdit)  # textEdited #textChanged
        self.ui.lineEdit.returnPressed.connect(self.on_returnPressed)

    def init_childLabel(self):
        self.ui.lb_failInfo = QLabel('Next:O-SFT /Current:O', self.ui.lb_status)
        self.ui.lb_failInfo.setStyleSheet(
            f"background-color:{self.ui.lb_status.palette().window().color().name()};font: 11pt '宋体';")
        # self.ui.lb_failInfo.setHidden(True)
        self.ui.lb_testTime = QLabel('TestTime:30s', self.ui.lb_errorCode)
        self.ui.lb_testTime.setStyleSheet(
            f"background-color:{self.ui.lb_errorCode.palette().window().color().name()};font: 11pt '宋体';")
        # self.ui.lb_testTime.setHidden(True)

    def init_tableWidget(self):
        self.ui.tableWidget.setHorizontalHeaderLabels(["SN", "ItemName", "Spec", "Limit_min", "tValue", "Limit_max",
                                                       "ElapsedTime", "StartTime", "tResult"])
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
        strHeaderQss = "QHeaderView::section { background:blue; color:white;min-height:3em;}"
        self.ui.tableWidget.setStyleSheet(strHeaderQss)
        my_signals.update_tableWidget[tuple].connect(self.update_tableWidget)

    def init_lab_factory(self, str_):
        if gv.cf.station.privileges == "lab":
            gv.IsDebug = True
            self.ui.actionprivileges.setIcon(QIcon(join(dirname(abspath(__file__)), 'images/lab-icon.png')))
        else:
            gv.IsDebug = False
            self.ui.actionConvertExcelToJson.setEnabled(False)
            self.ui.actionSaveToScript.setEnabled(False)
            self.ui.actionReloadScript.setEnabled(False)
            self.ui.actionprivileges.setIcon(QIcon(join(dirname(abspath(__file__)), 'images/factory.png')))
            self.ui.actionStart.setEnabled(False)
            self.ui.actionStop.setEnabled(False)
            self.ui.actionClearLog.setEnabled(False)

    def get_stationNo(self):
        if not gv.cf.station.fix_flag:
            return
        gv.FixSerialPort = SerialPort(gv.cf.station.fix_com_port, gv.cf.station.fix_com_baudRate)
        for i in range(0, 3):
            rReturn, revStr = gv.FixSerialPort.SendCommand('AT+READ_FIXNUM%', '\r\n', 1, False)
            if rReturn:
                gv.cf.station.station_no = revStr.replace('\r\n', '').strip()
                gv.cf.station.station_name = gv.cf.station.station_no[0, gv.cf.station.station_no.index('-')]
                print(f"Read fix number success,stationName:{gv.cf.station.station_name}")
                break
            else:
                if i == 2:
                    QMessageBox.Critical(self.ui, 'Read StationNO', "Read FixNum error,Please check it!")
                    sys.exit(0)

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
        self.ui.lb_continuous_fail = QLabel(f'continuous_fail: {gv.cf.count.continue_fail_count}')
        self.ui.lb_count_pass = QLabel(f'PASS: {gv.cf.count.total_pass_count}')
        self.ui.lb_count_fail = QLabel(f'FAIL: {gv.cf.count.total_fail_count}')
        self.ui.lb_count_abort = QLabel(f'ABORT: {gv.cf.count.total_abort_count}')
        try:
            self.ui.lb_count_yield = QLabel('Yield: {:.2%}'.format(gv.cf.count.total_pass_count / (
                    gv.cf.count.total_pass_count + gv.cf.count.total_fail_count + gv.cf.count.total_abort_count)))
        except ZeroDivisionError:
            self.ui.lb_count_yield = QLabel('Yield: 0.00%')
        self.ui.statusbar.addPermanentWidget(self.ui.lb_continuous_fail, 3)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_pass, 1)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_fail, 1)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_abort, 2)
        self.ui.statusbar.addPermanentWidget(self.ui.lb_count_yield, 16)

    def ContinuousFailReset_Click(self):
        pass

    def CheckContinueFailNum(self):
        if gv.cf.count.continue_fail_count >= gv.cf.count.continue_fail_limit:
            self.ui.lb_continuous_fail.setStyleSheet(f"background-color:red;")
            self.ContinuousFailReset_Click()
            return False
        else:
            self.ui.lb_continuous_fail.setStyleSheet(
                f"background-color:{self.ui.statusbar.palette().window().color().name()};")
            return True

    def on_returnPressed(self):
        print('press---------')
        # lg.logger.debug("hahhaha")
        if gv.dut_mode == 'unknown' or len(self.ui.lineEdit.text()) != gv.cf.dut.sn_len:
            QMessageBox.critical(self, 'JudgeMode',
                                 f"无法根据SN判断机种或者SN长度不正确! 扫描:{len(self.ui.lineEdit.text())},"
                                 f"规定:{gv.cf.dut.sn_len}.",
                                 QMessageBox.Yes, QMessageBox.Yes)
            return
        if not self.CheckContinueFailNum() and not gv.IsDebug and gv.cf.dut.test_mode.lower() != 'debug':
            return
        if gv.IsDebug:
            for i, item in enumerate(self.testSequences):
                for j in range(len(self.testSequences[i].steps)):
                    self.ui.treeWidget.topLevelItem(i).child(j).setBackground(0, Qt.white)
        else:
            self.testSequences = copy.deepcopy(self.testcase.original_suites)
            self.testcase.clone_suites = self.testSequences
            self.create_model(self.testSequences)
        if __debug__:
            print('debugging.....')
        else:
            gv.cf = conf.read_config(join(gv.current_path, 'config.yaml'), conf.config.Configs)

    def variable_init(self):
        testThread = Thread()
        if not testThread.is_alive():
            testThread = Thread()
            testThread.start()
        gv.SN = self.ui.lineEdit.text()
        gv.mes_result = f"http://{gv.cf.station.mes_result}/api/2/serial/{gv.SN}/station/{gv.cf.station.station_no}/info"
        gv.shop_floor_url = f"http://{gv.cf.station.mes_shop_floor}/api/CHKRoute/serial/{gv.SN}/station/{gv.cf.station.station_name}"
        gv.mesPhases = model.product.MesInfo(gv.SN, gv.cf.station.station_no, gv.cf.station.test_software_version)
        init_create_dirs()
        list_csv = []
        list_csvHeader = []
        gv.error_code_first_fail = ''
        gv.error_details_first_fail = ''
        gv.finalTestResult = False
        gv.setIpFlag = False
        gv.DUTMesIP = ''
        gv.MesMac = ''
        gv.sec = 0
        gv.SuiteNo = 0
        gv.StepNo = 0
        gv.WorkOrder = '1'
        gv.startTimeJsonFalg = True
        gv.startTimeJson = datetime.now()
        # update_label(self.ui.lb_failInfo, '', 9, self.ui.lb_failInfo.parent().palette().window().color().name())
        # update_label(self.ui.lb_testTime, '', 9, self.ui.lb_testTime.parent().palette().window().color().name())
        self.ui.lb_failInfo.setHidden(True)
        self.ui.lb_testTime.setHidden(True)
        self.set_test_status(TestStatus.START)

    def set_test_status(self, status: Enum):
        try:
            if status == TestStatus.START:
                self.ui.textEdit.clear()
                self.ui.lineEdit.setEnabled(False)
                update_label(self.ui.lb_status, 'Testing', 36, Qt.yellow)
                update_label(self.ui.lb_errorCode, '', 20, Qt.yellow)
                gv.startTime = datetime.now()
                self.start_time()
                self.ui.actionStart.setIcon(QIcon(join(dirname(abspath(__file__)), 'images/Pause-icon.png')))
                gv.SingleStepTest = False
                gv.StartFlag = True
                # lg.logger.debug(f"Start test...SN:{gv.SN},Station:{gv.cf.station.station_no},DUTMode:{gv.dut_mode},"
                #                 f"TestMode:{gv.cf.dut.test_mode},IsDebug:{gv.IsDebug},FTC:{gv.cf.station.fail_continue},"
                #                 f"SoftVersion:{gv.test_software_ver}")
                self.ui.tableWidget.clear()
            elif status == TestStatus.FAIL:
                gv.cf.count.total_fail_count += 1
                update_label(self.ui.lb_status, 'FAIL', 36, Qt.red)
                update_label(self.ui.lb_errorCode, gv.error_details_first_fail, 20, Qt.red)
                update_label(self.ui.lb_testTime, str(self.sec), 11,
                             self.ui.lb_testTime.parent().palette().window().color().name())
                self.UpdateContinueFail(False)
                if gv.setIpFlag:
                    gv.dut_comm.send_command(f"luxsetip {gv.cf.dut.dut_ip} 255.255.255.0", )
            elif status == TestStatus.PASS:
                gv.cf.count.total_pass_count += 1
                update_label(self.ui.lb_status, 'PASS', 36, Qt.green)
                update_label(self.ui.lb_errorCode, str(self.sec), 20, Qt.green)
                self.UpdateContinueFail(True)
            elif status == TestStatus.ABORT:
                gv.cf.count.total_abort_count_count += 1
                update_label(self.ui.lb_status, 'Abort', 36, Qt.gray)
                update_label(self.ui.lb_errorCode, gv.error_details_first_fail, 20, Qt.gray)
                update_label(self.ui.lb_testTime, str(self.sec), 11,
                             self.ui.lb_testTime.parent().palette().window().color().name())


        except:
            pass
        else:
            pass


        finally:
            try:
                if status == TestStatus.PASS or status == TestStatus.FAIL or status == TestStatus.ABORT:
                    self.ui.actionStart.setIcon(QIcon(join(dirname(abspath(__file__)), 'images/Start-icon.png')))
                    if gv.dut_comm is not None:
                        gv.dut_comm.close()
                    if gv.cf.station.fix_flag:
                        gv.FixSerialPort.SendCommand('AT+TESTEND%', 'OK')
                    # SFTP
            except:
                pass
            finally:
                try:
                    if status != TestStatus.START:
                        self.time_stop()
                        # lg.logger.debug(f"Test end,ElapsedTime:{self.sec}s.")
                        gv.StartFlag = False
                        self.ui.lineEdit.setEnabled(True)
                        self.init_status_bar()
                        # save config
                        if gv.finalTestResult:
                            update_label(self.ui.lb_errorCode, gv.error_details_first_fail, 20, Qt.red)
                except:
                    pass

    def UpdateContinueFail(self, testResult: bool):
        pass

    def update_tableWidget(self, result_tuple: tuple):
        def thread_update_tableWidget():
            row_cnt = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_cnt)
            column_cnt = self.ui.tableWidget.columnCount()
            for column in range(column_cnt):
                item = QTableWidgetItem(str(result_tuple[column]))
                if 'false' in str(result_tuple[-1]).lower() or 'fail' in str(result_tuple[-1]).lower():
                    item.setForeground(Qt.red)
                    # item.setFont(QFont('Times', 12, QFont.Black))
                self.ui.tableWidget.setItem(row_cnt, column, item)

        thread = Thread(target=thread_update_tableWidget())
        thread.start()

    def load_seqs(self, info):
        print(info)

        def thread_convert_and_load_script():
            self.testcase = model.testcase.TestCase(rf"{gv.above_current_path}\scripts\{gv.cf.station.testcase}",
                                                    f'{gv.cf.station.station_name}')
            self.testSequences = self.testcase.clone_suites
            if self.testSequences is not None:
                self.create_model(self.testSequences, gv.IsDebug)

        thread = Thread(target=thread_convert_and_load_script)
        thread.start()

    def handle_itemChanged(self, checked_item):
        self.ui.textEdit.insertHtml('  itemChanged  ')
        if gv.StartFlag:
            return
        if checked_item.parent() is None:
            pNo = self.ui.treeWidget.indexOfTopLevelItem(checked_item)
            isChecked: bool = True if checked_item.checkState(0) == Qt.Checked else False
            self.testcase.original_suites[pNo].isTest = isChecked
            self.ui.treeWidget.itemChanged.disconnect()
            for i in range(0, checked_item.childCount()):
                checked_item.child(i).setCheckState(0, Qt.Checked if isChecked else Qt.Unchecked)
                self.testcase.original_suites[pNo].test_steps[i].isTest = isChecked
            self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)
        else:
            ParentIsTest = []
            pNo = self.ui.treeWidget.indexOfTopLevelItem(checked_item.parent())
            iNo = checked_item.parent().indexOfChild(checked_item)
            isChecked = True if checked_item.checkState(0) == Qt.Checked else False
            self.testcase.original_suites[pNo].test_steps[iNo].isTest = isChecked
            for i in range(checked_item.parent().childCount()):
                isChecked_all = True if checked_item.parent().child(i).checkState(0) == Qt.Checked else False
                ParentIsTest.append(isChecked_all)
            isChecked_parent = any(ParentIsTest)
            self.ui.treeWidget.itemChanged.disconnect()
            self.testcase.original_suites[pNo].isTest = isChecked_parent
            checked_item.parent().setCheckState(0, Qt.Checked if isChecked_parent else Qt.Unchecked)
            self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)

    def handle_itemClicked(self, clicked_item):
        """mouse left-click event, In Qt, it is always a left button that emits the clicked() signal.
        :param clicked_item:
        """
        if clicked_item.parent() is not None:
            ss = clicked_item.parent().data(0, Qt.DisplayRole).split(' ', 1)[1]
            self.ui.textEdit.insertHtml('- ' * 9 + f"<a name='testSuite:{ss}'>Start testSuite:{ss}</a>" + '- ' * 9)
            self.ui.textEdit.scrollToAnchor(f'testSuite:{ss}')

        else:
            self.ui.textEdit.insertHtml('click')

    def handle_treeWidgetMenu(self):
        menu = QMenu(self.ui.treeWidget)
        menu.addAction(self.ui.actionCheckAll)
        menu.addAction(self.ui.actionUncheckAll)
        menu.addAction(self.ui.actionStepping)
        menu.addAction(self.ui.actionLooping)
        menu.addAction(self.ui.actionEditStep)
        menu.exec_(QCursor.pos())

    def handle_actionCheckAll(self):
        self.create_model(self.testcase.original_suites, True)

    def handle_actionUncheckAll(self):
        self.create_model(self.testcase.original_suites, False)

    def handle_actionStepping(self):
        pass

    def handle_actionLooping(self):
        pass

    def handle_actionEditStep(self):
        pass

    def handle_actionOpen_TestCase(self):
        def thread_actionOpen_TestCase():
            os.system(self.testcase.testcase_path_excel)

        thread = Thread(target=thread_actionOpen_TestCase)
        thread.start()

    def handle_actionConvertExcelToJson(self):
        import model.loadseq
        thread = Thread(
            target=model.loadseq.excel_convert_to_json(self.testcase.testcase_path_excel,
                                                       gv.cf.station.station_all))
        thread.start()

    def handle_actionOpenScript(self):
        def thread_actionOpenScript():
            os.system(self.testcase.test_script_json)

        thread = Thread(target=thread_actionOpenScript)
        thread.start()

    def create_model(self, sequences=None, checkall=True):
        if sequences is None:
            return
        self.ui.treeWidget.clear()
        self.ui.treeWidget.setHeaderLabel(f'{gv.cf.station.station_no}')
        for suite in sequences:
            root_node = QTreeWidgetItem(self.ui.treeWidget)
            root_node.setData(0, Qt.DisplayRole, f'{suite.index + 1}. {suite.SeqName}')
            root_node.setIcon(0, QIcon(join(dirname(abspath(__file__)), 'images/folder-icon.png')))
            if gv.IsDebug:
                if checkall:
                    root_node.setCheckState(0, Qt.Checked)
                else:
                    root_node.setCheckState(0, Qt.Unchecked)
            for step in suite.test_steps:
                step_node = QTreeWidgetItem(root_node)
                step_node.setData(0, Qt.DisplayRole, f'{step.index + 1}) {step.ItemName}')
                if gv.IsDebug:
                    if checkall:
                        step_node.setCheckState(0, Qt.Checked)
                    else:
                        step_node.setCheckState(0, Qt.Unchecked)
                step_node.setIcon(0, QIcon(join(dirname(abspath(__file__)), 'images/Document-txt-icon.png')))
                step_node.setFlags(Qt.ItemIsEnabled)
                root_node.addChild(step_node)
        self.ui.treeWidget.setStyle(QStyleFactory.create('windows'))
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.resizeColumnToContents(0)
        # self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)

    def update_treeWidgetItem_backColor(self, color: QBrush, suiteNO_: int, stepNo_: int):
        def thread_update():
            self.ui.treeWidget.topLevelItem(suiteNO_).child(stepNo_).setBackground(0, color)

        thread = Thread(target=thread_update)
        thread.start()

    def timerEvent(self, a):
        # print("=========")
        global sec
        my_signals.update_label[QLabel, str, int].emit(self.ui.lb_errorCode, str(sec), 20)
        self.a += 1
        sec += 1

    def time_start(self):
        print("开始")
        self.timer = self.startTimer(1000)

    def time_stop(self):
        print("停止")
        self.killTimer(self.timer)

    def init_textEditHandler(self):
        textEdit_handler = lg.QTextEditHandler(stream=self.ui.textEdit)
        textEdit_handler.formatter = lg.logger.handlers[0].formatter
        textEdit_handler.level = 10
        textEdit_handler.name = 'textEdit_handler'
        logging.getLogger('testlog').addHandler(textEdit_handler)


class TestStatus(Enum):
    PASS = 1
    FAIL = 2
    START = 3
    ABORT = 4


if __name__ == "__main__":
    pass
    app = QApplication([])
    mainWin = MainForm()
    mainWin.ui.show()
    app.exec_()
