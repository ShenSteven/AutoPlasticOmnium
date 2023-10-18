#!/usr/bin/env python
# coding: utf-8
"""
@File   : peakcan.py
@Author : Steven.Shen
@Date   : 4/11/2023
@Desc   : 
"""
import platform
import threading
from inspect import currentframe

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from communication.peak.pcan.PCANBasic import *
import bll.mainform
from PyQt5.QtWidgets import QDialog, QMessageBox, QStackedLayout, QFormLayout
# from PCANBasic import *  ## PCAN-Basic library import
from communication.peak.ui_peak import Ui_PeakGui

IS_WINDOWS = platform.system() == 'Windows'
DISPLAY_UPDATE_MS = 100

if IS_WINDOWS:
    ENABLE_CAN_FD = True
    try:
        import win32event

        WINDOWS_EVENT_SUPPORT = True
    except ImportError:
        WINDOWS_EVENT_SUPPORT = False
else:
    ENABLE_CAN_FD = False
    # check driver version before enabling FD
    try:
        with open("/sys/class/pcan/version") as f:
            version = f.readline()
            if int(version[0]) >= 8:
                ENABLE_CAN_FD = True
    except Exception:
        ENABLE_CAN_FD = False
    WINDOWS_EVENT_SUPPORT = False


class PeakCan(QDialog, Ui_PeakGui):
    def __init__(self, logger, parent=None):
        QDialog.__init__(self, parent)
        Ui_PeakGui.__init__(self)
        self.stackedLayout = None
        self.StringVar = None
        self.logger = logger
        self.setupUi(self)
        self.initialize()
        self.set_signals_connect()
        # self.ReqDelay = c_ushort(ReqDelay)
        # self.RespDelay = c_ushort(RespDelay)
        # self.ReadTxCount = ReadTxCount
        # self.MRtoMRDelay = MRtoMRDelay
        # self.SchedulePeriod = SchedulePeriod
        # self._interval = ReqDelay + RespDelay
        # self.Master3C = PLinApi.TLINScheduleSlot()
        # self.Slave3D = PLinApi.TLINScheduleSlot()

    def InitializeBasicComponents(self):
        self.exit = -1
        self.m_objPCANBasic = PCANBasic()
        self.m_PcanHandle = PCAN_NONEBUS
        self.m_LastMsgsList = []

        self.m_IsFD = False
        self.m_CanRead = False

        if WINDOWS_EVENT_SUPPORT:
            self.m_ReadThread = None
            self.m_Terminated = False
            self.m_ReceiveEvent = win32event.CreateEvent(None, 0, 0, None)

        self._lock = threading.RLock()

        self.m_NonPnPHandles = {'PCAN_ISABUS1': PCAN_ISABUS1, 'PCAN_ISABUS2': PCAN_ISABUS2,
                                'PCAN_ISABUS3': PCAN_ISABUS3, 'PCAN_ISABUS4': PCAN_ISABUS4,
                                'PCAN_ISABUS5': PCAN_ISABUS5, 'PCAN_ISABUS6': PCAN_ISABUS6,
                                'PCAN_ISABUS7': PCAN_ISABUS7, 'PCAN_ISABUS8': PCAN_ISABUS8,
                                'PCAN_DNGBUS1': PCAN_DNGBUS1}

        self.m_BAUDRATES = {'1 MBit/sec': PCAN_BAUD_1M, '800 kBit/sec': PCAN_BAUD_800K, '500 kBit/sec': PCAN_BAUD_500K,
                            '250 kBit/sec': PCAN_BAUD_250K,
                            '125 kBit/sec': PCAN_BAUD_125K, '100 kBit/sec': PCAN_BAUD_100K,
                            '95,238 kBit/sec': PCAN_BAUD_95K, '83,333 kBit/sec': PCAN_BAUD_83K,
                            '50 kBit/sec': PCAN_BAUD_50K, '47,619 kBit/sec': PCAN_BAUD_47K,
                            '33,333 kBit/sec': PCAN_BAUD_33K, '20 kBit/sec': PCAN_BAUD_20K,
                            '10 kBit/sec': PCAN_BAUD_10K, '5 kBit/sec': PCAN_BAUD_5K}

        self.m_HWTYPES = {'ISA-82C200': PCAN_TYPE_ISA, 'ISA-SJA1000': PCAN_TYPE_ISA_SJA,
                          'ISA-PHYTEC': PCAN_TYPE_ISA_PHYTEC, 'DNG-82C200': PCAN_TYPE_DNG,
                          'DNG-82C200 EPP': PCAN_TYPE_DNG_EPP, 'DNG-SJA1000': PCAN_TYPE_DNG_SJA,
                          'DNG-SJA1000 EPP': PCAN_TYPE_DNG_SJA_EPP}

        self.m_IOPORTS = {'0100': 0x100, '0120': 0x120, '0140': 0x140, '0200': 0x200, '0220': 0x220, '0240': 0x240,
                          '0260': 0x260, '0278': 0x278,
                          '0280': 0x280, '02A0': 0x2A0, '02C0': 0x2C0, '02E0': 0x2E0, '02E8': 0x2E8, '02F8': 0x2F8,
                          '0300': 0x300, '0320': 0x320,
                          '0340': 0x340, '0360': 0x360, '0378': 0x378, '0380': 0x380, '03BC': 0x3BC, '03E0': 0x3E0,
                          '03E8': 0x3E8, '03F8': 0x3F8}

        self.m_INTERRUPTS = {'3': 3, '4': 4, '5': 5, '7': 7, '9': 9, '10': 10, '11': 11, '12': 12, '15': 15}

        if IS_WINDOWS or (not IS_WINDOWS and ENABLE_CAN_FD):
            self.m_PARAMETERS = {'Device ID': PCAN_DEVICE_ID, '5V Power': PCAN_5VOLTS_POWER,
                                 'Auto-reset on BUS-OFF': PCAN_BUSOFF_AUTORESET, 'CAN Listen-Only': PCAN_LISTEN_ONLY,
                                 'Debugs Log': PCAN_LOG_STATUS, 'Receive Status': PCAN_RECEIVE_STATUS,
                                 'CAN Controller Number': PCAN_CONTROLLER_NUMBER, 'Trace File': PCAN_TRACE_STATUS,
                                 'Channel Identification (USB)': PCAN_CHANNEL_IDENTIFYING,
                                 'Channel Capabilities': PCAN_CHANNEL_FEATURES,
                                 'Bit rate Adaptation': PCAN_BITRATE_ADAPTING,
                                 'Get Bit rate Information': PCAN_BITRATE_INFO,
                                 'Get Bit rate FD Information': PCAN_BITRATE_INFO_FD,
                                 'Get CAN Nominal Speed Bit/s': PCAN_BUSSPEED_NOMINAL,
                                 'Get CAN Data Speed Bit/s': PCAN_BUSSPEED_DATA, 'Get IP Address': PCAN_IP_ADDRESS,
                                 'Get LAN Service Status': PCAN_LAN_SERVICE_STATUS,
                                 'Reception of Status Frames': PCAN_ALLOW_STATUS_FRAMES,
                                 'Reception of RTR Frames': PCAN_ALLOW_RTR_FRAMES,
                                 'Reception of Error Frames': PCAN_ALLOW_ERROR_FRAMES,
                                 'Interframe Transmit Delay': PCAN_INTERFRAME_DELAY}
        else:
            self.m_PARAMETERS = {'Device ID': PCAN_DEVICE_ID, '5V Power': PCAN_5VOLTS_POWER,
                                 'Auto-reset on BUS-OFF': PCAN_BUSOFF_AUTORESET, 'CAN Listen-Only': PCAN_LISTEN_ONLY,
                                 'Debugs Log': PCAN_LOG_STATUS}

    def set_signals_connect(self):
        """connect signals to slots"""
        print('set_signals_connect')
        self.refreshBt_2.clicked.connect(self.refreshHardware)
        # self.identifyBt.clicked.connect(self.on_IdentifyHardware)
        self.connectBt_2.clicked.connect(self.on_DoCanConnect)
        self.releaseBt_2.clicked.connect(self.on_DoCanDisconnect)
        self.checkBox.toggled.connect(self.on_checkBox)
        self.refreshBt_2.clicked.connect(self.refreshHardware)
        self.checkBox.clicked.connect(self.on_checkBox)
        self.hardwareCbx_2.currentIndexChanged.connect(self.hardwareCbx_IndexChanged)

    def initialize(self):
        self.tabWidget.setCurrentWidget(self.tabCan)
        self.m_objPCANBasic = PCANBasic()

        # self.stackedLayout = QStackedLayout(self.widget_3)
        # self.frame_4 = QtWidgets.QFrame(self.widget_3)
        # self.verticalLayout.addWidget(self.frame_4)
        # for i in range(self.frame_3.layout().count()):
        #     self.frame_3.layout().itemAt(i).widget().hide()
        #     print(self.frame_3.layout().itemAt(i).widget().objectName())
        # self.label_rate = QtWidgets.QLabel(self.frame_3)
        # self.label_rate.setObjectName("label_rate")
        # self.label_rate.setText('Bit rate:')
        # self.textEdit = QtWidgets.QTextEdit(self.frame_3)
        # self.formlayout = QFormLayout(self.frame_3)
        # self.formlayout.addRow(self.label_rate, self.textEdit)

        # self.stackedLayout.addWidget(self.frame_3)
        # self.stackedLayout.addWidget(self.frame_4)
        # self.gridLayout_3.addWidget(self.widget_3, 1, 0, 1, 4)
        # self.stackedLayout.d
        # self.widget_3.setVisible(False)
        # self.label_4.setEnabled(False)
        # self.label_4.setVisible(False)
        # self.label_4.destroy()

    def refreshHardware(self):
        items = []
        self.hardwareCbx_2.clear()
        for name, value in self.m_NonPnPHandles.items():
            # Includes all no-Plug&Play Handles
            items.append(self.FormatChannelName(value.value))

        result = self.m_objPCANBasic.GetValue(PCAN_NONEBUS, PCAN_ATTACHED_CHANNELS)
        if result[0] == PCAN_ERROR_OK:
            # Include only connectable channels
            for channel in result[1]:
                if channel.channel_condition & PCAN_CHANNEL_AVAILABLE:
                    items.append(
                        self.FormatChannelName(channel.channel_handle, channel.device_features & FEATURE_FD_CAPABLE))

        items.sort()
        for name in items:
            self.hardwareCbx_2.insertItem(self.hardwareCbx_2.count(), name)
        self.hardwareCbx_2.setCurrentIndex(self.hardwareCbx_2.count() - 1)

    def on_DoCanConnect(self):
        if self.doCanConnect() == PCAN_ERROR_OK:
            self.setConnectionStatus(True)

    def on_DoCanDisconnect(self):
        pass

    def on_checkBox(self):
        if self.checkBox.checkState() == Qt.Checked:
            # del self.gridLayout_3
            # del self.label_4
            # del self.label_5
            # del self.label_7
            # del self.label_8
            for i in range(self.frame_3.layout().count()):
                self.frame_3.layout().itemAt(i).widget().deleteLater()
                print(self.frame_3.layout().itemAt(i).widget().objectName())
            self.label_rate = QtWidgets.QLabel(self.frame_3)
            self.label_rate.setObjectName("label_rate")
            self.label_rate.setText('Bit rate:')
            self.textEdit = QtWidgets.QTextEdit(self.frame_3)
            # self.formlayout = QFormLayout(self.frame_3)
            # self.formlayout.addRow(self.label_rate, self.textEdit)
            # self.frame_3.setLayout(self.formlayout)
        else:
            self.stackedLayout.setCurrentIndex(0)
            # self.widget_3.setVisible(False)

    def hardwareCbx_IndexChanged(self):
        pass

    def FormatChannelName(self, handle, isFD=False):
        if handle < 0x100:
            devDevice = TPCANDevice(handle >> 4)
            byChannel = handle & 0xF
        else:
            devDevice = TPCANDevice(handle >> 8)
            byChannel = handle & 0xFF
        if isFD:
            self.StringVar.append(f"{self.GetDeviceName(devDevice.value)}: FD {byChannel} {'{:02X}'.format(handle)}")
        else:
            self.StringVar.append(f"{self.GetDeviceName(devDevice.value)}: {byChannel} {'{:02X}'.format(handle)}")
        return self.StringVar

    def GetDeviceName(self, handle):
        switcher = {
            PCAN_NONEBUS.value: "PCAN_NONEBUS",
            PCAN_PEAKCAN.value: "PCAN_PEAKCAN",
            PCAN_ISA.value: "PCAN_ISA",
            PCAN_DNG.value: "PCAN_DNG",
            PCAN_PCI.value: "PCAN_PCI",
            PCAN_USB.value: "PCAN_USB",
            PCAN_PCC.value: "PCAN_PCC",
            PCAN_VIRTUAL.value: "PCAN_VIRTUAL",
            PCAN_LAN.value: "PCAN_LAN"
        }
        return switcher.get(handle, "UNKNOWN")

    def setConnectionStatus(self, bConnected=True):
        # updates buttons state
        self.connectBt_2.setEnabled(not bConnected)
        self.releaseBt_2.setEnabled(bConnected)
        self.refreshBt_2.setEnabled(not bConnected)
        # Updates ComboBoxs state
        self.baudrateCbx_2.setEnabled(not bConnected)
        self.modeCbx_2.setEnabled(not bConnected)
        self.hardwareCbx_2.setEnabled(not bConnected)
        # Hardware configuration and read mode
        if not bConnected:
            pass
            # self.cbbChannel_SelectedIndexChanged(self.cbbChannel['selection'])
            # self.hardwareCbx.currentTextChanged[str].emit(self.hardwareCbx.currentText())
            # self.hardwareCbx.currentIndexChanged[int].emit(self.hardwareCbx.currentIndex())
        else:
            pass

    def doCanConnect(self):
        baudrate = self.m_BAUDRATES[self.baudrateCbx_2.currentText()]
        hwtype = self.m_HWTYPES[self.baudrateCbx_3.currentText()]
        ioport = int(self.modeCbx_2.currentText(), 16)
        interrupt = int(self.modeCbx_3.currentText())

        # Connects a selected PCAN-Basic channel
        if self.m_IsFD:
            result = self.m_objPCANBasic.InitializeFD(self.m_PcanHandle, bytes(self.m_BitrateTXT.get(), 'utf-8'))
        else:
            result = self.m_objPCANBasic.Initialize(self.m_PcanHandle, baudrate, hwtype, ioport, interrupt)

        if result != PCAN_ERROR_OK:
            if result != PCAN_ERROR_CAUTION:
                QMessageBox.critical(self, "Error!", self.GetFormatedError(result), QMessageBox.Yes)
                # bll.mainform.MainForm.main_form.mySignals.showMessageBox[str, str, int].emit('Exception!',
                #                                                                              f'{currentframe().f_code.co_name}:{self.GetFormatedError(result)} ',
                #                                                                              5)
                self.logger.error(f"Exception!{self.GetFormatedError(result)}", )
                return False
            else:
                self.logger.warning('The bitrate being used is different than the given one')
                return True
        else:
            # Prepares the PCAN-Basic's PCAN-Trace file
            self.ConfigureTraceFile()
            return True

    def GetFormatedError(self, error):
        # Gets the text using the GetErrorText API function
        # If the function success, the translated error is returned. If it fails,
        # a text describing the current error is returned.
        stsReturn = self.m_objPCANBasic.GetErrorText(error, 0)
        if stsReturn[0] != PCAN_ERROR_OK:
            return "An error occurred. Error-code's text ({0:X}h) couldn't be retrieved".format(error)
        else:
            return stsReturn[1]

    def ConfigureTraceFile(self):
        # Configure the maximum size of a trace file to 5 megabytes
        #
        iBuffer = 5
        stsResult = self.m_objPCANBasic.SetValue(self.m_PcanHandle, PCAN_TRACE_SIZE, iBuffer)
        if stsResult != PCAN_ERROR_OK:
            self.logger.warning(self.GetFormatedError(stsResult))

        # Configure the way how trace files are created:
        # * Standard name is used
        # * Existing file is ovewritten,
        # * Only one file is created.
        # * Recording stopts when the file size reaches 5 megabytes.
        #
        iBuffer = TRACE_FILE_SINGLE | TRACE_FILE_OVERWRITE
        stsResult = self.m_objPCANBasic.SetValue(self.m_PcanHandle, PCAN_TRACE_CONFIGURE, iBuffer)
        if stsResult != PCAN_ERROR_OK:
            self.logger.warning(self.GetFormatedError(stsResult))
