# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lin.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import traceback
from PyQt5.QtWidgets import QDialog  # QMessageBox
from future.moves import collections
import ui.mainform
from ui.ui_lin import Ui_PeakLin
import conf.logprint as lg
import conf.globalvar as gv
import binascii
import os
import re
import sys
import time
from ctypes import *
from . import PLinApi
from inspect import currentframe
from decimal import Decimal, ROUND_UP


def bytes_to_string(byte_strs):
    str_list = []
    for i in range(len(byte_strs)):
        str_list.append('{:02X}'.format(byte_strs[i]))
    return str.join(' ', str_list)


def right_round(num, keep_n):
    if isinstance(num, float):
        num = str(num)
    return Decimal(num).quantize((Decimal('0.' + '0' * keep_n)), rounding=ROUND_UP)


class PeakLin(QDialog, Ui_PeakLin):
    """
    bootloader download, uds.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        Ui_PeakLin.__init__(self)
        self.setupUi(self)
        self.init_signals_connect()
        self.initialize()
        self.ReqDelay = c_ushort(gv.cf.BLF.ReqDelay)
        self.RespDelay = c_ushort(gv.cf.BLF.RespDelay)
        self._interval = gv.cf.BLF.ReqDelay + gv.cf.BLF.RespDelay
        self.Master3C = PLinApi.TLINScheduleSlot()
        self.Slave3D = PLinApi.TLINScheduleSlot()

    def init_signals_connect(self):
        """connect signals to slots"""
        self.refreshBt.clicked.connect(self.refreshHardware)
        self.identifyBt.clicked.connect(self.on_IdentifyHardware)
        self.connectBt.clicked.connect(self.on_DoLinConnect)
        self.releaseBt.clicked.connect(self.on_DoLinDisconnect)
        # self.hardwareCbx.currentTextChanged.connect(self.cbbChannel_SelectedIndexChanged)
        self.hardwareCbx.currentIndexChanged.connect(self.hardwareCbx_IndexChanged)

    def initialize(self):
        # API configuration
        lg.logger.debug("init...")
        self.m_objPLinApi = PLinApi.PLinApi()
        if not self.m_objPLinApi.isLoaded():
            raise Exception("PLin-API could not be loaded ! Exiting...")
        # configure LIN variables
        self.m_hClient = PLinApi.HLINCLIENT(0)
        self.m_hHw = PLinApi.HLINHW(0)
        self.m_HwMode = PLinApi.TLIN_HARDWAREMODE_NONE
        self.m_HwBaudrate = c_ushort(0)
        self.FRAME_FILTER_MASK = c_uint64(0xFFFFFFFFFFFFFFFF)
        self.m_lMask = self.FRAME_FILTER_MASK
        # LIN GUI variables
        # sorted dictionary of available hardware
        d = {'<No available hardware>': PLinApi.HLINHW(0)}
        self.m_dataHws = collections.OrderedDict(sorted(list(d.items()), key=lambda t: t[0]))
        # sorted dictionary of hardware baudrates
        d = {'2400': 2400, '9600': 9600, '10400': 10400, '19200': 19200}
        self.m_dataHwBaudrates = collections.OrderedDict(sorted(list(d.items()), key=lambda t: t[1]))
        for name, value in self.m_dataHwBaudrates.items():
            self.baudrateCbx.insertItem(self.baudrateCbx.count(), name)
        self.baudrateCbx.setCurrentIndex(len(self.m_dataHwBaudrates) - 1)
        # sorted dictionary of hardware mode
        d = {'Master': PLinApi.TLIN_HARDWAREMODE_MASTER, 'Slave': PLinApi.TLIN_HARDWAREMODE_SLAVE}
        self.m_dataHwModes = collections.OrderedDict(sorted(list(d.items()), key=lambda t: t[0]))
        for name, value in self.m_dataHwModes.items():
            self.modeCbx.insertItem(self.modeCbx.count(), name)
            self.modeCbx.setCurrentIndex(len(self.m_dataHwModes) - 1)
        # self.refreshHardware()

    def on_IdentifyHardware(self):
        lHw = self.m_dataHws[self.hardwareCbx.currentText()]
        if lHw.value != 0:
            # makes the corresponding PCAN-USB-Pro's LED blink
            self.m_objPLinApi.IdentifyHardware(lHw)

    def on_DoLinConnect(self):
        if self.doLinConnect():
            self.setConnectionStatus(True)

    def on_DoLinDisconnect(self):
        if self.doLinDisconnect():
            self.setConnectionStatus(False)

    def refreshHardware(self):
        # Get the buffer length needed...
        self.hardwareCbx.blockSignals(True)
        lwCount = c_ushort(0)
        availableHWs = (PLinApi.HLINHW * 0)()
        self.m_objPLinApi.GetAvailableHardware(availableHWs, 0, lwCount)
        if lwCount == 0:
            # use default value if either no hw is connected or an unexpected error occurred
            lwCount = c_ushort(16)
        availableHWs = (PLinApi.HLINHW * lwCount.value)()
        lwBuffSize = c_ushort(lwCount.value * 2)
        # Get all available LIN hardware.
        linResult = self.m_objPLinApi.GetAvailableHardware(availableHWs, lwBuffSize, lwCount)
        if linResult == PLinApi.TLIN_ERROR_OK:
            # clear combobox
            self.m_dataHws.clear()
            self.hardwareCbx.clear()
            # Get information for each LIN hardware found
            lnHwType = c_int(0)
            lnDevNo = c_int(0)
            lnChannel = c_int(0)
            lnMode = c_int(0)
            if lwCount.value == 0:
                strHw = '<No Hardware found>'
                self.m_dataHws[strHw] = PLinApi.HLINHW(0)
                self.hardwareCbx.insertItem(self.hardwareCbx.count(), strHw)
            else:
                for i in range(lwCount.value):
                    lwHw = availableHWs[i]
                    # Read the type of the hardware with the handle lwHw.
                    self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_TYPE, lnHwType, 0)
                    # Read the device number of the hardware with the handle lwHw.
                    self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_DEVICE_NUMBER, lnDevNo, 0)
                    # Read the channel number of the hardware with the handle lwHw.
                    self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_CHANNEL_NUMBER, lnChannel, 0)
                    # Read the mode of the hardware with the handle lwHw (Master,Slave or None).
                    self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_MODE, lnMode, 0)
                    # translate type value to string
                    if lnHwType.value == PLinApi.LIN_HW_TYPE_USB_PRO.value:
                        strName = "PCAN-USB Pro"
                    elif lnHwType.value == PLinApi.LIN_HW_TYPE_USB_PRO_FD.value:
                        strName = "PCAN-USB Pro FD"
                    elif lnHwType.value == PLinApi.LIN_HW_TYPE_PLIN_USB.value:
                        strName = "PLIN-USB"
                    else:
                        strName = "Unknown"
                    # add information to channel combobox
                    strHw = str.format('{0} - dev. {1}, chan. {2}', strName, lnDevNo.value, lnChannel.value)
                    self.m_dataHws[strHw] = PLinApi.HLINHW(lwHw)
                    self.hardwareCbx.insertItem(self.hardwareCbx.count(), strHw)
            # select first item
            # self.hardwareCbx.blockSignals(True)
            self.hardwareCbx.setCurrentIndex(0)
            # self.hardwareCbx.blockSignals(False)
        else:
            ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('Exception!',
                                                                                         f'{currentframe().f_code.co_name}:{self.getFormattedError(linResult)} ',
                                                                                         5)

    def getFormattedError(self, linError):
        # get error string from code
        pTextBuff = create_string_buffer(255)
        linResult = self.m_objPLinApi.GetErrorText(linError, 0x09, pTextBuff, 255)
        # display error message
        if linResult == PLinApi.TLIN_ERROR_OK and len(pTextBuff.value) != 0:
            result = str.format("{0}", bytes.decode(pTextBuff.value))
        else:
            result = str.format(
                "An error occurred. Error-code's text ({0}) couldn't be retrieved", linError)
        return result

    def doLinConnect(self):
        result = False
        if self.m_hHw.value != 0:
            if not self.doLinDisconnect():
                return result

        if self.m_hClient.value == 0:
            # register LIN client
            self.m_objPLinApi.RegisterClient("PLIN-API Example", None, self.m_hClient)
        # Try to connect the application client to the hardware with the local
        # handle.
        # hwHandle = self.m_dataHws[self.cbbChannel['selection']]
        hwHandle = self.m_dataHws[self.hardwareCbx.currentText()]
        linResult = self.m_objPLinApi.ConnectClient(self.m_hClient, hwHandle)
        if linResult == PLinApi.TLIN_ERROR_OK:
            # If the connection successfully assign
            # the local handle to the member handle.
            self.m_hHw = hwHandle
            # read hardware's parameter
            lnMode = c_int(0)
            lnCurrBaud = c_int(0)
            self.m_objPLinApi.GetHardwareParam(hwHandle, PLinApi.TLIN_HARDWAREPARAM_MODE, lnMode, 0)
            linResult = self.m_objPLinApi.GetHardwareParam(hwHandle, PLinApi.TLIN_HARDWAREPARAM_BAUDRATE, lnCurrBaud, 0)
            # check if initialization is required
            # hwMode = self.m_dataHwModes[self.modeCbx.currentText()]
            hwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
            try:
                # convert baudrates selection to int
                hwBaudrate = c_ushort(int(self.baudrateCbx.currentText()))
            except:
                hwBaudrate = c_ushort(0)
            if lnMode.value == PLinApi.TLIN_HARDWAREMODE_NONE.value or lnCurrBaud.value != hwBaudrate.value:
                # Only if the current hardware is not initialized
                # try to Initialize the hardware with mode and baudrate
                linResult = self.m_objPLinApi.InitializeHardware(self.m_hClient, self.m_hHw, hwMode, hwBaudrate)
            if linResult == PLinApi.TLIN_ERROR_OK:
                self.m_HwMode = hwMode
                self.m_HwBaudrate = hwBaudrate
                # Set the client filter with the mask.
                self.m_objPLinApi.SetClientFilter(self.m_hClient, self.m_hHw, self.m_lMask)
                # Read the frame table from the connected hardware.
                # self.readFrameTableFromHw()
                # Reset the last LIN error code to default.
                linResult = PLinApi.TLIN_ERROR_OK
                result = True
                lg.logger.debug(
                    f'connect success, dev- {self.m_hHw.value}, client- {self.m_hClient.value}, mode- {hwMode}')
            else:
                # An error occurred while initializing hardware.
                # Set the member variable to default.
                self.m_hHw = PLinApi.HLINHW(0)
                result = False
        else:
            # The local hardware handle is invalid
            # and/or an error occurs while connecting
            # hardware with client.
            # Set the member variable to default.
            self.m_hHw = PLinApi.HLINHW(0)
            result = False
        if linResult != PLinApi.TLIN_ERROR_OK:
            ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('Exception!',
                                                                                         f'{currentframe().f_code.co_name}:{self.getFormattedError(linResult)} ',
                                                                                         5)
        return result

    def doLinDisconnect(self):
        # If the application was registered with LIN as client.
        if self.m_hHw.value != 0:
            # The client was connected to a LIN hardware.
            # Before disconnect from the hardware check
            # the connected clients and determine if the
            # hardware configuration have to reset or not.
            #
            # Initialize the locale variables.
            lfOtherClient = False
            lfOwnClient = False
            lhClientsSize = c_ushort(255)
            lhClients = (PLinApi.HLINCLIENT * lhClientsSize.value)()
            # Get the connected clients from the LIN hardware.
            linResult = self.m_objPLinApi.GetHardwareParam(
                self.m_hHw, PLinApi.TLIN_HARDWAREPARAM_CONNECTED_CLIENTS, lhClients, lhClientsSize)
            if linResult == PLinApi.TLIN_ERROR_OK:
                # No errors !
                # Check all client handles.
                for i in range(1, lhClientsSize.value):
                    # If client handle is invalid
                    if lhClients[i] == 0:
                        continue
                    # Set the boolean to true if the handle isn't the
                    # handle of this application.
                    # Even the boolean is set to true it can never
                    # set to false.
                    lfOtherClient = lfOtherClient | (lhClients[i] != self.m_hClient.value)
                    # Set the boolean to true if the handle is the
                    # handle of this application.
                    # Even the boolean is set to true it can never
                    # set to false.
                    lfOwnClient = lfOwnClient | (lhClients[i] == self.m_hClient.value)
            # If another application is also connected to
            # the LIN hardware do not reset the configuration.
            if not lfOtherClient:
                # No other application connected !
                # Reset the configuration of the LIN hardware.
                self.m_objPLinApi.ResetHardwareConfig(
                    self.m_hClient, self.m_hHw)
            # If this application is connected to the hardware
            # then disconnect the client. Otherwise, not.
            if lfOwnClient:
                # Disconnect if the application was connected to a LIN
                # hardware.
                self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
                lg.logger.debug("SuspendSchedule....")
                linResult = self.m_objPLinApi.DisconnectClient(self.m_hClient, self.m_hHw)
                if linResult == PLinApi.TLIN_ERROR_OK:
                    self.m_hHw = PLinApi.HLINHW(0)
                    return True
                else:
                    # Error while disconnecting from hardware.
                    ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('Exception!',
                                                                                                 f'{currentframe().f_code.co_name}:{self.getFormattedError(linResult)} ',
                                                                                                 5)
                    return False
            else:
                return True
        else:
            # m_hHw not connected
            return True

    def setConnectionStatus(self, bConnected=True):
        # updates buttons state
        self.connectBt.setEnabled(not bConnected)
        self.releaseBt.setEnabled(bConnected)
        self.refreshBt.setEnabled(not bConnected)
        # Updates ComboBoxs state
        self.baudrateCbx.setEnabled(not bConnected)
        self.modeCbx.setEnabled(not bConnected)
        self.hardwareCbx.setEnabled(not bConnected)
        # Hardware configuration and read mode
        if not bConnected:
            pass
            # self.cbbChannel_SelectedIndexChanged(self.cbbChannel['selection'])
            # self.hardwareCbx.currentTextChanged[str].emit(self.hardwareCbx.currentText())
            # self.hardwareCbx.currentIndexChanged[int].emit(self.hardwareCbx.currentIndex())
        else:
            pass

    def hardwareCbx_IndexChanged(self):
        # lg.logger.debug(lwHw)
        lg.logger.debug(self.hardwareCbx.currentIndex())
        lg.logger.debug(self.hardwareCbx.currentText())
        lwHw = self.m_dataHws[self.hardwareCbx.currentText()]
        if lwHw != 0:
            self.connectBt.setEnabled(True)
            self.identifyBt.setEnabled(True)
            lnMode = c_int(0)
            lnCurrBaud = c_int(0)
            self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_MODE, lnMode, 0)
            self.m_objPLinApi.GetHardwareParam(lwHw, PLinApi.TLIN_HARDWAREPARAM_BAUDRATE, lnCurrBaud, 0)
            # Update hardware mode comboBox
            lg.logger.debug(f'get lnMode = {lnMode.value}')
            # if lnMode.value == PLinApi.TLIN_HARDWAREMODE_MASTER.value:
            self.modeCbx.setCurrentIndex(0)
            # else:
            #     self.modeCbx.setCurrentIndex(1)
            # Assign the Baudrate to the Control.
            if str(lnCurrBaud.value) in self.m_dataHwBaudrates:
                self.baudrateCbx.setCurrentIndex(list(self.m_dataHwBaudrates.keys()).index(str(lnCurrBaud.value)))
            elif lnCurrBaud.value == 0:
                self.baudrateCbx.setCurrentIndex(len(self.m_dataHwBaudrates) - 1)
            else:
                self.baudrateCbx.setCurrentText(str(lnCurrBaud.value))
        else:
            self.connectBt.setEnabled(False)
            self.identifyBt.setEnabled(False)

    def runSchedule(self):
        try:
            iScheduleNumber = 0
            self.Master3C.FrameId[0] = c_ubyte(60)
            self.Master3C.Delay = self.ReqDelay
            self.Master3C.Type = PLinApi.TLIN_SLOTTYPE_MASTER_REQUEST
            self.Slave3D.FrameId[0] = c_ubyte(61)
            self.Slave3D.Delay = self.RespDelay
            self.Slave3D.Type = PLinApi.TLIN_SLOTTYPE_SLAVE_RESPONSE
            for i in range(1, 8):
                self.Master3C.FrameId[i] = c_ubyte(0)
                self.Slave3D.FrameId[i] = c_ubyte(0)
            pSchedule = (PLinApi.TLINScheduleSlot * 2)()
            pSchedule[0] = self.Master3C
            pSchedule[1] = self.Slave3D
            error_code = self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
            lg.logger.debug('SuspendSchedule...')
            if error_code != PLinApi.TLIN_ERROR_OK:
                lg.logger.debug('SuspendSchedule fail...')
                self.displayError(error_code)
                if error_code == PLinApi.TLIN_ERROR_ILLEGAL_CLIENT:
                    self.on_DoLinConnect()
            error_code = self.m_objPLinApi.SetSchedule(self.m_hClient, self.m_hHw, iScheduleNumber, pSchedule,
                                                       len(pSchedule))
            lg.logger.debug('SetSchedule...')
            if error_code == PLinApi.TLIN_ERROR_OK:
                error_code = self.m_objPLinApi.StartSchedule(self.m_hClient, self.m_hHw, iScheduleNumber)
                if error_code == PLinApi.TLIN_ERROR_OK:
                    lg.logger.info("start schedule success...")
                    time.sleep(0.5)
                    return True
                else:
                    self.displayError(error_code)
                    return False
            else:
                self.displayError(error_code)
                error_code = self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
                self.displayError(error_code)
                return False
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def SuspendDiagSchedule(self):
        error_code = self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
        lg.logger.debug('SuspendSchedule...')
        if error_code != PLinApi.TLIN_ERROR_OK:
            lg.logger.debug('SuspendSchedule fail...')
            self.displayError(error_code)
            return False
        else:
            return True

    def SetFrameEntry(self, _id, nad, pci, data, log=True, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                      ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        try:
            time.sleep(gv.cf.BLF.ReqDelay / 1000)
            frameData = nad + " " + pci + " " + data
            tempData = frameData.split()
            lFrameEntry = PLinApi.TLINFrameEntry()
            lFrameEntry.Length = c_ubyte(8)
            lFrameEntry.FrameId = c_ubyte(int(_id, 16))
            lFrameEntry.ChecksumType = ChecksumType
            lFrameEntry.Direction = direction
            lFrameEntry.Flags = PLinApi.FRAME_FLAG_RESPONSE_ENABLE
            lFrameEntry.InitialData = (c_ubyte * 8)()
            for i in range(8):
                try:
                    lFrameEntry.InitialData[i] = c_ubyte(int(tempData[i].strip(), 16))
                except IndexError:
                    lFrameEntry.InitialData[i] = c_ubyte(int('FF', 16))
                except Exception as ex:
                    lg.logger.debug(ex)
            linResult = self.m_objPLinApi.SetFrameEntry(self.m_hClient, self.m_hHw, lFrameEntry)
            if linResult == PLinApi.TLIN_ERROR_OK:
                linResult = self.m_objPLinApi.UpdateByteArray(self.m_hClient, self.m_hHw, lFrameEntry.FrameId,
                                                              c_ubyte(0),
                                                              lFrameEntry.Length, lFrameEntry.InitialData)
                if linResult == PLinApi.TLIN_ERROR_OK:
                    if log:
                        lg.logger.debug(
                            f"TX  {_id},{bytes_to_string(lFrameEntry.InitialData)},{lFrameEntry.Direction},{lFrameEntry.ChecksumType}")
                    return True
                else:
                    self.displayError(linResult)
                    lg.logger.error(f"Failed to UpdateByteArray message:id:{_id},{lFrameEntry.InitialData}")
                    return False
            else:
                self.displayError(linResult)
                lg.logger.error(f"Failed to SetFrameEntry message:id:{_id},{lFrameEntry.InitialData}")
                return False
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def SingleFrame(self, _id, nad, pci, data, timeout=2.0):
        try:
            if self.SetFrameEntry(_id, nad, pci, data):  # send first frame
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFResp(_id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def MultiFrame(self, _id, nad, pci, data, timeout=2):
        tempData = data.split()
        _len = len(tempData)
        try:
            first_data = ' '.join(tempData[0:5])
            if self.SetFrameEntry(_id, nad, pci, first_data):  # send first frame
                j = 1
                remainder = (_len - 5) % 6
                quotient = (_len - 5) // 6
                for i in range(quotient + 1):
                    if j == 16:
                        j = 0
                    if i == quotient:
                        if remainder == 0:
                            break
                        else:
                            conse_data = ' '.join(tempData[5 + i * 6:5 + i * 6 + remainder])
                    else:
                        conse_data = ' '.join(tempData[5 + i * 6:5 + i * 6 + 6])
                    self.ConsecutiveFrame(_id, nad, '{:X}'.format(j), conse_data)
                    j = j + 1
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFResp(_id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def TransferData(self, _id, nad, file_data, bytesNumOfBlock, timeout=2.0):
        tempData = file_data.split()
        _len = len(tempData)
        maxBytesNumOfBlock = int(bytesNumOfBlock.replace(" ", ""), 16)
        payloadOfBlock = maxBytesNumOfBlock - 2
        blockNum = _len // payloadOfBlock
        lastBlockNum = _len % payloadOfBlock
        j = 1
        try:
            for i in range(blockNum + 1):
                if j == 256:
                    j = 0

                if i == blockNum:
                    if lastBlockNum == 0:
                        break
                    else:
                        pci = '1' + '{:03X}'.format(lastBlockNum + 2) + '36' + '{:02X}'.format(j)
                        pci = " ".join(re.findall(".{2}", pci))
                        blockData = ' '.join(tempData[i * payloadOfBlock:i * payloadOfBlock + lastBlockNum])
                else:
                    pci = '1' + bytesNumOfBlock.replace(' ', '') + '36' + '{:02X}'.format(j)
                    pci = " ".join(re.findall(".{2}", pci))
                    blockData = ' '.join(tempData[i * payloadOfBlock:i * payloadOfBlock + payloadOfBlock])

                if not self.TransferDataBlock(_id, nad, pci, blockData, timeout):
                    return False
                j = j + 1
            return True
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def SFResp(self, _id, rsid, timeout):
        if _id.upper() == '3C':
            _id = '3D'
        pRcvMsg = PLinApi.TLINRcvMsg()
        start_time = time.time()
        self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
        while pRcvMsg.Data[2] != (int(rsid, 16)) or pRcvMsg.Data[1] > 15:
            self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
            if time.time() - start_time > timeout:
                lg.logger.error(f"timeout {timeout}s for respond,id")
                return False, ''
            if pRcvMsg.Type != PLinApi.TLIN_MSGTYPE_STANDARD.value:
                continue
            if pRcvMsg.Data[2] == (int('7F', 16)) and pRcvMsg.Data[1] < 16:
                lg.logger.error(
                    f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
                if pRcvMsg.Data[4] == (int("78", 16)):
                    continue
                lg.logger.error(f"Negative response!NRC={hex(pRcvMsg.Data[4])}")
                respData = bytes_to_string(pRcvMsg.Data)
                return False, respData
        lg.logger.debug(
            f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
        return True, bytes_to_string(pRcvMsg.Data)

    def SingleFrameCF(self, _id, nad, pci, data, timeout=2.0):
        try:
            if self.SetFrameEntry(_id, nad, pci, data):  # send first frame
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFRespCF(_id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def SFRespCF(self, _id, rsid, timeout):
        if _id.upper() == '3C':
            _id = '3D'
        pRcvMsg = PLinApi.TLINRcvMsg()
        start_time = time.time()
        self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
        # get FirstFrame
        while pRcvMsg.Data[1] < 16 or pRcvMsg.Data[1] > 31:
            self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
            if time.time() - start_time > timeout:
                lg.logger.error(f"timeout {timeout}s for respond,id")
                return False, ''
            if pRcvMsg.Type != PLinApi.TLIN_MSGTYPE_STANDARD.value:
                continue
        lg.logger.debug(
            f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
        # parse FirstFrame
        if pRcvMsg.Data[3] == (int(rsid, 16)):
            data_len = pRcvMsg.Data[2]
            datas = [pRcvMsg.Data[3], pRcvMsg.Data[4], pRcvMsg.Data[5], pRcvMsg.Data[6], pRcvMsg.Data[7]]
        else:
            lg.logger.error(
                f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
            return False, ''
        # get Consecutive frames
        CFCounter = right_round((data_len - 5) / 6, 0)
        for i in range(0, int(CFCounter)):
            time.sleep(self._interval / 1000)
            self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
            lg.logger.debug(
                f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
            for j in range(2, 8):
                datas.append(pRcvMsg.Data[j])

        return True, bytes_to_string(datas)

    def ConsecutiveFrame(self, _id, nad, sn, data, log=True, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                         ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        time.sleep(self._interval / 1000)
        pci = '2' + sn
        self.SetFrameEntry(_id, nad, pci, data, log, direction, ChecksumType)
        return True

    def CalKey(self, seed):
        try:
            xorMask = 0xC0A59221
            seeds = seed.split()
            cal = [(int(seeds[0], 16) ^ ((xorMask >> 24) & 0xFF)), (int(seeds[1], 16) ^ ((xorMask >> 16) & 0xFF)),
                   (int(seeds[2], 16) ^ ((xorMask >> 8) & 0xFF)), (int(seeds[3], 16) ^ (xorMask & 0xFF))]
            key1 = ((cal[2] & 0x0F) << 4) | (cal[1] & 0x0F)
            key2 = ((cal[3] & 0x0F) << 4) | ((cal[1] & 0xF0) >> 4)
            key3 = (cal[0] & 0xF0) | ((cal[2] & 0x3C) >> 2)
            key4 = ((cal[0] & 0x0F) << 4) | ((cal[3] & 0x78) >> 3)
            key = '{:02X}'.format(key1) + " " + '{:02X}'.format(key2) + " " + '{:02X}'.format(
                key3) + " " + '{:02X}'.format(key4)
            lg.logger.debug(f'get key: {key}')
            return key
        except Exception as ex:
            sys.exit(f'{currentframe().f_code.co_name}:{ex}')

    def TransferDataBlock(self, _id, nad, pci, data, timeout):
        tempData = data.split()
        _len = len(tempData)
        try:
            first_data = ' '.join(tempData[0:3])
            if self.SetFrameEntry(_id, nad, pci, first_data):  # send first frame
                j = 1
                remainder = (_len - 3) % 6
                quotient = (_len - 3) // 6
                for i in range(quotient + 1):
                    if j == 16:
                        j = 0
                    if i == quotient:
                        if remainder == 0:
                            break
                        else:
                            consedata = ' '.join(tempData[3 + i * 6:3 + i * 6 + remainder])
                    else:
                        consedata = ' '.join(tempData[3 + i * 6:3 + i * 6 + 6])

                    self.ConsecutiveFrame(_id, nad, '{:X}'.format(j), consedata, False)
                    j = j + 1
                RSID = '76'
                return self.SFResp(_id, RSID, timeout)[0]
            else:
                return False
        except Exception as ex:
            lg.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def plin_write(self, frameId, data, timeout=None):
        # initialize LIN message to sent
        pMsg = PLinApi.TLINMsg()
        # set frame id to Protected ID
        nPID = c_ubyte(int(frameId, 16))
        self.m_objPLinApi.GetPID(nPID)
        pMsg.FrameId = c_ubyte(nPID.value)
        pMsg.Direction = PLinApi.TLIN_DIRECTION_PUBLISHER
        pMsg.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_ENHANCED
        data_bytes = data.split()
        pMsg.Length = c_ubyte(len(data_bytes))
        for i in range(len(data_bytes)):
            try:
                pMsg.Data[i] = c_ubyte(int(data_bytes[i].strip(), 16))
            except Exception as ex:
                lg.logger.exception(ex)
        # set checksum
        self.m_objPLinApi.CalculateChecksum(pMsg)
        # write LIN message
        linResult = self.m_objPLinApi.Write(self.m_hClient, self.m_hHw, pMsg)
        if linResult == PLinApi.TLIN_ERROR_OK:
            self.displayNotification("Message successfully written")
            return True, ''
        else:
            self.displayError(linResult)
            lg.logger.error("Failed to write message")
            return False, ''

    def get_datas(self, file_s19_cmd):
        s19data = ''
        try:
            with open(file_s19_cmd, 'rb') as f:
                for line in f:
                    le = len(line)
                    msg = line[10:(le - 4)]  # Address and checksum are not part of message and they won't be send
                    s19data += msg.decode("utf-8")
        except FileNotFoundError:
            lg.logger.debug("File not found")
            raise
        datas = " ".join(re.findall(".{2}", s19data))
        lg.logger.debug(datas)
        return datas

    @staticmethod
    def get_crc_apps19(file_dir_path):
        s19crc = ''
        try:
            for file in os.listdir(file_dir_path):
                if 'crc' in file:
                    with open(os.path.join(file_dir_path, file), 'rb') as f:
                        lg.logger.debug(os.path.join(file_dir_path, file))
                        for line in f:
                            le = len(line)
                            if le > 13:
                                s19crc = line[10:18].decode("utf-8")
                                s19crc = ' '.join(re.findall(".{2}", s19crc))
                                lg.logger.debug(f'get app s19 crc = {s19crc}')
                                break
        except FileNotFoundError:
            lg.logger.fatal("File not found")
            raise
        return s19crc

    def crc32(self, v):
        """
        generates the crc32 hash of the v.
        @return: str, the str value for the crc32 of the v
        """
        return '0x%x' % (binascii.crc32(v) & 0xffffffff)  # 取crc32的八位数据 %x返回16进制

    def displayError(self, linError, isInput=False, waitTime=0):
        # get error string from code
        pTextBuff = create_string_buffer(255)
        linResult = self.m_objPLinApi.GetErrorText(linError, 0x09, pTextBuff, 255)
        # display error message
        if linResult == PLinApi.TLIN_ERROR_OK and len(pTextBuff.value) != 0:
            self.displayNotification(str.format("** Error ** - {0} ", bytes.decode(pTextBuff.value)), waitTime)
        else:
            self.displayNotification(str.format("** Error ** - code={0}", linError), waitTime)
        if isInput:
            # wait for user approval
            # self.displayMenuInput("** Press <enter> to continue **")
            sys.exit()

    def displayNotification(self, text="** Invalid choice **", waitSeconds=0.0):
        lg.logger.warning(text)
        time.sleep(waitSeconds)
