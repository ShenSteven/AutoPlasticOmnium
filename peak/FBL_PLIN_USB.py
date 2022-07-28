# !/usr/bin/env python
# coding: utf-8
"""
@File   : bootloader download.py
@Author : Steven.Shen
@Date   : 2022/7/6
@Desc   :
"""

import binascii
import os
import re
import sys
import time
from ctypes import *
from . import PLinApi
from inspect import currentframe
import conf.logprint as lg


def bytes_to_string(byte_strs):
    str_list = []
    for i in range(8):
        str_list.append('{:02X}'.format(byte_strs[i]))
    return str.join(' ', str_list)


class Bootloader(object):

    def __init__(self):
        self.initialize()
        self.ReqDelay = c_ushort(10)
        self.RespDelay = c_ushort(10)
        self._interval = 0.02
        self.materReq_3C = PLinApi.TLINScheduleSlot()
        self.slaveReq_3D = PLinApi.TLINScheduleSlot()

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
        # initialize a dictionnary to get LIN ID from PID
        self.PIDs = {}
        for i in range(64):
            nPID = c_ubyte(i)
            self.m_objPLinApi.GetPID(nPID)
            self.PIDs[nPID.value] = i

    def displayMenuInput(self, text="Select an action: "):
        if sys.version_info > (3, 0):
            choice = input(str.format("\n * {0}", text))
        else:
            choice = input(str.format("\n * {0}", text))
        # return the response as a upper string
        choice = str(choice).upper()
        lg.logger.debug("\n")
        return choice

    def displayAvailableConnection(self):
        # retrieve a list of available hardware
        hWInfoList = self.getAvailableHardware()
        # display result
        if len(hWInfoList) == 0:
            lg.logger.error("\t<No hardware found>")
        else:
            # for each hardware display it's type, device and channel
            lg.logger.debug(" List of available LIN hardware:")
            for hWInfo in hWInfoList:
                if self.m_hHw.value == hWInfo[3]:
                    if self.m_HwMode.value == PLinApi.TLIN_HARDWAREMODE_MASTER.value:
                        hwType = "master"
                    else:
                        hwType = "slave"
                    # add information if the application is connecter to the hardware
                    isConnected = str.format("(connected as {0}, {1})", hwType, self.m_HwBaudrate.value)
                else:
                    isConnected = ""
                lg.logger.debug(str.format('\t{3}) {0} - dev. {1}, chan. {2} {4}', hWInfo[
                    0], hWInfo[1], hWInfo[2], hWInfo[3], isConnected))
        return len(hWInfoList)

    def connect(self):
        hwlen = self.displayAvailableConnection()
        try:
            if hwlen == 0:
                return False
            if hwlen == 1:
                choice = 1
            else:
                choice = self.displayMenuInput("Select an hardware to connect to: ")
            lHw = PLinApi.HLINHW(int(choice))
            lHwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
            lHwBaudrate = c_ushort(19200)
            if self.doLinConnect(lHw, lHwMode, lHwBaudrate):
                lg.logger.info("Connection successful")
                return True
            else:
                lg.logger.error("Connection failed")
                return False
        except Exception as ex:
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False

    def getAvailableHardware(self):
        res = []
        lwCount = c_ushort(0)
        availableHWs = (PLinApi.HLINHW * 0)()
        self.m_objPLinApi.GetAvailableHardware(availableHWs, 0, lwCount)
        if lwCount == 0:
            # use default value if either no hw is connected or an unexpected error occured
            lwCount = c_ushort(16)
        availableHWs = (PLinApi.HLINHW * lwCount.value)()
        lwBuffSize = c_ushort(lwCount.value * 2)
        linResult = self.m_objPLinApi.GetAvailableHardware(availableHWs, lwBuffSize, lwCount)
        if linResult == PLinApi.TLIN_ERROR_OK:
            # Get information for each LIN hardware found
            lnHwType = c_int(0)
            lnDevNo = c_int(0)
            lnChannel = c_int(0)
            lnMode = c_int(0)
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
                # add information to result list
                res.append([strName, lnDevNo.value, lnChannel.value, lwHw])
        return res

    def doLinConnect(self, hwHandle, hwMode, hwBaudrate):
        result = False
        if self.m_hHw.value != 0:
            if not self.close():
                return result
        if self.m_hClient.value == 0:
            self.m_objPLinApi.RegisterClient("PLIN-API Console", None, self.m_hClient)
        linResult = self.m_objPLinApi.ConnectClient(self.m_hClient, hwHandle)
        if linResult == PLinApi.TLIN_ERROR_OK:
            self.m_hHw = hwHandle
            # read hardware's parameter
            lnMode = c_int(0)
            lnCurrBaud = c_int(0)
            linResult = self.m_objPLinApi.GetHardwareParam(hwHandle, PLinApi.TLIN_HARDWAREPARAM_MODE, lnMode, 0)
            linResult = self.m_objPLinApi.GetHardwareParam(hwHandle, PLinApi.TLIN_HARDWAREPARAM_BAUDRATE, lnCurrBaud, 0)
            if lnMode.value == PLinApi.TLIN_HARDWAREMODE_NONE.value or lnCurrBaud.value != hwBaudrate.value:
                linResult = self.m_objPLinApi.InitializeHardware(self.m_hClient, self.m_hHw, hwMode, hwBaudrate)
            if linResult == PLinApi.TLIN_ERROR_OK:
                self.m_HwMode = hwMode
                self.m_HwBaudrate = hwBaudrate
                # Set the client filter with the mask.
                linResult = self.m_objPLinApi.SetClientFilter(self.m_hClient, self.m_hHw, self.m_lMask)
                linResult = PLinApi.TLIN_ERROR_OK
                result = True
            else:
                self.m_hHw = PLinApi.HLINHW(0)
                result = False
        else:
            self.m_hHw = PLinApi.HLINHW(0)
            lg.logger.error("doLinConnect fail")
            result = False
        if linResult != PLinApi.TLIN_ERROR_OK:
            self.displayError(linResult)
            lg.logger.error("doLinConnect fail")
        return result

    def runSchedule(self):
        try:
            self.materReq_3C.FrameId[0] = c_ubyte(60)
            self.materReq_3C.Delay = self.ReqDelay
            self.materReq_3C.Type = PLinApi.TLIN_SLOTTYPE_MASTER_REQUEST
            self.slaveReq_3D.FrameId[0] = c_ubyte(61)
            self.slaveReq_3D.Delay = self.RespDelay
            self.slaveReq_3D.Type = PLinApi.TLIN_SLOTTYPE_SLAVE_RESPONSE
            for i in range(1, 8):
                self.materReq_3C.FrameId[i] = c_ubyte(0)
                self.slaveReq_3D.FrameId[i] = c_ubyte(0)
            pSchedule = (PLinApi.TLINScheduleSlot * 2)()
            pSchedule[0] = self.materReq_3C
            pSchedule[1] = self.slaveReq_3D
            error_code = self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
            if error_code != PLinApi.TLIN_ERROR_OK:
                self.displayError(error_code)
            error_code = self.m_objPLinApi.SetSchedule(self.m_hClient, self.m_hHw, 7, pSchedule, 2)
            if error_code == PLinApi.TLIN_ERROR_OK:
                error_code = self.m_objPLinApi.StartSchedule(self.m_hClient, self.m_hHw, 7)
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
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False

    def SetFrameEntry(self, id, nad, pci, data, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                      ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        try:
            time.sleep(self._interval)
            framedata = nad + " " + pci + " " + data
            tempdata = framedata.split()
            lFrameEntry = PLinApi.TLINFrameEntry()
            lFrameEntry.Length = c_ubyte(8)
            lFrameEntry.FrameId = c_ubyte(int(id, 16))
            lFrameEntry.ChecksumType = ChecksumType
            lFrameEntry.Direction = direction
            lFrameEntry.Flags = PLinApi.FRAME_FLAG_RESPONSE_ENABLE
            lFrameEntry.InitialData = (c_ubyte * 8)()
            for i in range(8):
                try:
                    lFrameEntry.InitialData[i] = c_ubyte(int(tempdata[i].strip(), 16))
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
                    lg.logger.debug(
                        f"TX  {id},{bytes_to_string(lFrameEntry.InitialData)},{lFrameEntry.Direction},{lFrameEntry.ChecksumType}")
                    return True
                else:
                    self.displayError(linResult)
                    lg.logger.error(f"Failed to UpdateByteArray message:id:{id},{lFrameEntry.InitialData}")
                    return False
            else:
                self.displayError(linResult)
                lg.logger.error(f"Failed to SetFrameEntry message:id:{id},{lFrameEntry.InitialData}")
                return False
        except Exception as ex:
            # self.doLinDisconnect()
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False

    def SingleFrame(self, id, nad, pci, data, timeout=2.0):
        try:
            if self.SetFrameEntry(id, nad, pci, data):  # send first frame
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFResp(id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False, ""

    def MultiFrame(self, id, nad, pci, data, timeout=2):
        tempdata = data.split()
        _len = len(tempdata)
        try:
            first_data = ' '.join(tempdata[0:5])
            # print(first_data)
            if self.SetFrameEntry(id, nad, pci, first_data):  # send first frame
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
                            conse_data = ' '.join(tempdata[5 + i * 6:5 + i * 6 + remainder])
                    else:
                        conse_data = ' '.join(tempdata[5 + i * 6:5 + i * 6 + 6])
                    self.ConsecutiveFrame(id, nad, '{:X}'.format(j), conse_data)
                    j = j + 1
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFResp(id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            # self.doLinDisconnect()
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False, ""

    def TransferData(self, id, nad, filedata, bytesNumOfBlock, timeout=2.0):
        tempdata = filedata.split()
        _len = len(tempdata)
        maxBytesNumOfBlock = int(bytesNumOfBlock.replace(" ", ""), 16)
        payloadOfBlock = maxBytesNumOfBlock - 2
        blockNum = _len // payloadOfBlock  # 36 01, 36 02
        lastblockNum = _len % payloadOfBlock  # 36 01, 36 02
        j = 1
        try:
            for i in range(blockNum + 1):
                if j == 256:
                    j = 0

                if i == blockNum:
                    if lastblockNum == 0:
                        break
                    else:
                        pci = '1' + '{:03X}'.format(lastblockNum + 2) + '36' + '{:02X}'.format(j)
                        pci = " ".join(re.findall(".{2}", pci))
                        blockData = ' '.join(tempdata[i * payloadOfBlock:i * payloadOfBlock + lastblockNum])
                else:
                    pci = '1' + bytesNumOfBlock.replace(' ', '') + '36' + '{:02X}'.format(j)
                    pci = " ".join(re.findall(".{2}", pci))
                    blockData = ' '.join(tempdata[i * payloadOfBlock:i * payloadOfBlock + payloadOfBlock])

                if not self.TransferDataBlock(id, nad, pci, blockData, timeout):
                    return False
                j = j + 1
            return True
        except Exception as ex:
            # self.doLinDisconnect()
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False

    def close(self):
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
                    lfOtherClient = lfOtherClient | (
                            lhClients[i] != self.m_hClient.value)
                    # Set the boolean to true if the handle is the
                    # handle of this application.
                    # Even the boolean is set to true it can never
                    # set to false.
                    lfOwnClient = lfOwnClient | (
                            lhClients[i] == self.m_hClient.value)
            # If another application is also connected to
            # the LIN hardware do not reset the configuration.
            if lfOtherClient == False:
                # No other application connected !
                # Reset the configuration of the LIN hardware.
                linResult = self.m_objPLinApi.ResetHardwareConfig(
                    self.m_hClient, self.m_hHw)
            # If this application is connected to the hardware
            # then disconnect the client. Otherwise not.
            if lfOwnClient == True:
                # Disconnect if the application was connected to a LIN
                # hardware.
                linResult = self.m_objPLinApi.SuspendSchedule(self.m_hClient, self.m_hHw)
                lg.logger.debug("SuspendSchedule....")
                linResult = self.m_objPLinApi.DisconnectClient(self.m_hClient, self.m_hHw)
                if linResult == PLinApi.TLIN_ERROR_OK:
                    self.m_hHw = PLinApi.HLINHW(0)
                    return True
                else:
                    # Error while disconnecting from hardware.
                    self.displayError(linResult)
                    return False
            else:
                return True
        else:
            # m_hHw not connected
            return True

        # Prints a notification
        #

    def displayNotification(self, text="** Invalid choice **", waitSeconds=0.0):
        lg.logger.warning(text)
        time.sleep(waitSeconds)

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

    def SFResp(self, id, rsid, timeout):
        if id.lower() == '3c':
            id = '3d'
        pRcvMsg = PLinApi.TLINRcvMsg()
        start_time = time.time()
        self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
        while pRcvMsg.Data[2] != (int(rsid, 16)) or pRcvMsg.Data[1] > 15:
            self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
            if time.time() - start_time > timeout:
                lg.logger.error(f"timeout {timeout}s for respond,id")
                return False, ''
            if pRcvMsg.Type != PLinApi.TLIN_MSGTYPE_STANDARD:
                continue
            if pRcvMsg.Data[2] == (int('7F', 16)) and pRcvMsg.Data[1] < 16:
                lg.logger.debug(
                    f"RX  {id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
                if pRcvMsg.Data[4] == (int("78", 16)):
                    continue
                lg.logger.error(f"Negative response!NRC={pRcvMsg.Data[4]}")
                respdata = bytes_to_string(pRcvMsg.Data)
                return False, respdata
        lg.logger.debug(
            f"RX  {id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
        return True, bytes_to_string(pRcvMsg.Data)

    def ConsecutiveFrame(self, id, nad, sn, data, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                         ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        time.sleep(self._interval)
        pci = '2' + sn
        self.SetFrameEntry(id, nad, pci, data, direction, ChecksumType)
        return True

    def CalKey(self, seed):
        try:
            xorMask = 0xC0A59221
            seeds = seed.split()
            cal = []
            cal.append((int(seeds[0], 16) ^ ((xorMask >> 24) & 0xFF)))
            cal.append((int(seeds[1], 16) ^ ((xorMask >> 16) & 0xFF)))
            cal.append((int(seeds[2], 16) ^ ((xorMask >> 8) & 0xFF)))
            cal.append((int(seeds[3], 16) ^ ((xorMask) & 0xFF)))
            key1 = ((cal[2] & 0x0F) << 4) | (cal[1] & 0x0F)
            key2 = ((cal[3] & 0x0F) << 4) | ((cal[1] & 0xF0) >> 4)
            key3 = (cal[0] & 0xF0) | ((cal[2] & 0x3C) >> 2)
            key4 = ((cal[0] & 0x0F) << 4) | ((cal[3] & 0x78) >> 3)
            key = '{:02X}'.format(key1) + " " + '{:02X}'.format(key2) + " " + '{:02X}'.format(
                key3) + " " + '{:02X}'.format(key4)
            lg.logger.debug(f'get key: {key}')
            return key
        except Exception as ex:
            # self.doLinDisconnect()
            sys.exit(f'{currentframe().f_code.co_name}:{ex}')

    def TransferDataBlock(self, id, nad, pci, data, timeout):
        tempdata = data.split()
        _len = len(tempdata)
        try:
            first_data = ' '.join(tempdata[0:3])
            if self.SetFrameEntry(id, nad, pci, first_data):  # send first frame
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
                            consedata = ' '.join(tempdata[3 + i * 6:3 + i * 6 + remainder])
                    else:
                        consedata = ' '.join(tempdata[3 + i * 6:3 + i * 6 + 6])

                    self.ConsecutiveFrame(id, nad, '{:X}'.format(j), consedata)
                    j = j + 1
                RSID = '76'
                return self.SFResp(id, RSID, timeout)[0]
            else:
                return False
        except Exception as ex:
            # self.doLinDisconnect()
            lg.logger.exception(f'{currentframe().f_code.co_name}:{ex}')
            return False

    def get_data(self, file_s19_cmd):
        s19data = ''
        try:
            with open(file_s19_cmd, 'rb') as f:
                for line in f:
                    l = len(line)
                    msg = line[10:(l - 4)]  # Address and checksum are not part of message and they won't be send
                    s19data += msg.decode("utf-8")
        except FileNotFoundError:
            lg.logger.debug("File not found")
            raise
        return " ".join(re.findall(".{2}", s19data))

    @staticmethod
    def get_crc_apps19(file_dir_path):
        s19crc = ''
        try:
            for file in os.listdir(file_dir_path):
                if 'crc' in file:
                    with open(os.path.join(file_dir_path, file), 'rb') as f:
                        lg.logger.debug(os.path.join(file_dir_path, file))
                        for line in f:
                            l = len(line)
                            if l > 13:
                                s19crc = line[10:18].decode("utf-8")
                                s19crc = ' '.join(re.findall(".{2}", s19crc))
                                lg.logger.debug(f'get app s19 crc = {s19crc}')
                                break
        except FileNotFoundError:
            # lg.logger.debug("File not found")
            raise
        return s19crc

    def crc32(self, v):
        """
        generates the crc32 hash of the v.
        @return: str, the str value for the crc32 of the v
        """
        return '0x%x' % (binascii.crc32(v) & 0xffffffff)  # 取crc32的八位数据 %x返回16进制


if __name__ == '__main__':
    pass
    # init variables
    # ID = '3C'
    # NAD = '1E'
    # drvStartAdd = '00 0F ED 38'
    # drvLen = '00 00 00 58'
    # drvCRC32 = 'AF A5 00 A3'
    # appStartAdd = '00 00 20 14'
    # appLen = '00 01 BF EC'
    # appCRC32 = 'E8 E4 7E 2B'
    # drvs19 = './image/DFLZ_M4_fld.s19'
    # apps19 = './image/DFLZ_M4_appl_lin.s19'
    # Year = time.strftime('%y', time.localtime())
    # Month = time.strftime('%m', time.localtime())
    # Day = time.strftime('%d', time.localtime())
    #
    # # connect PLIN_USB device
    # app = Bootloader()
    # app.connect()
    # app.runSchedule()
    #
    # # Pre - programming
    # logger('ExtendedSession')
    # app.PLINSingleFrame(ID, NAD, '02', '10 03')
    #
    # logger('CheckPrecondition')
    # app.PLINSingleFrame(ID, NAD, '04', '31 01 FF 02')
    #
    # logger('ControlDTCSettingsOFF')
    # app.PLINSingleFrame(ID, NAD, '02', '85 02')
    #
    # logger('CommunicationControlOFF')
    # app.PLINSingleFrame(ID, NAD, '03', '28 03 03')
    #
    # logger('ProgrammingSession')
    # app.PLINSingleFrame(ID, NAD, '02', '10 02')
    #
    # logger('RequstSeed')
    # resp = app.PLINSingleFrame(ID, NAD, '02', '27 09')
    # seed = resp[-11:]
    # logger(f'get seed: {seed}')
    #
    # logger('CalcKey')
    # key = app.CalKey(seed)
    #
    # logger('SendKey')
    # app.PLINSingleFrame(ID, NAD, '06', f'27 0A {key}')
    #
    # # DrvDownload
    # logger('RequestDownloadDrv')
    # resp = app.PLINMultiFrame(ID, NAD, '10 0B', f'34 00 44 {drvStartAdd} {drvLen}')
    # lenOfBlock = resp[13:17]
    # logger(f'get max lenOfBlock: {lenOfBlock}', '')
    #
    # logger('TransferDataDrv')
    # s19datas = app.get_data(drvs19)
    # s19datas = " ".join(re.findall(".{2}", s19datas))
    # print(s19datas)
    # app.TransferData(ID, NAD, s19datas, lenOfBlock)
    #
    # logger('RequestTransferExit')
    # app.PLINSingleFrame(ID, NAD, '01', '37')
    #
    # logger('CheckIntegrity')
    # app.PLINMultiFrame(ID, NAD, '10 08', f'31 01 F0 01 {drvCRC32}')
    #
    # logger('WriteDataByIdentifier')
    # app.PLINMultiFrame(ID, NAD, '10 0C', f'2E F1 5A {Year} {Month} {Day} 11 aa bb cc dd ee ab')
    #
    # # AppDownload
    # logger('EraseMemory')
    # app.PLINMultiFrame(ID, NAD, '10 0D', f'31 01 FF 00 44 {appStartAdd} {appLen}', 3)
    #
    # logger('RequestDownloadApp')
    # resp = app.PLINMultiFrame(ID, NAD, '10 0B', f'34 00 44 {appStartAdd} {appLen}')
    # lenOfBlock = resp[13:17]
    # logger(f'get max lenOfBlock: {lenOfBlock}', '')
    #
    # logger('TransferDataApp')
    # s19datas = app.get_data(apps19)
    # s19datas = " ".join(re.findall(".{2}", s19datas))
    # print(s19datas)
    # app.TransferData(ID, NAD, s19datas, lenOfBlock)
    #
    # logger('RequestTransferExit')
    # app.PLINSingleFrame(ID, NAD, '01', '37')
    #
    # logger('CheckIntegrity')
    # app.PLINMultiFrame(ID, NAD, '10 08', f'31 01 F0 01 {appCRC32}', 5)
    #
    # # Post-Programming
    # logger('CheckDependencies')
    # app.PLINSingleFrame(ID, NAD, '04', '31 01 FF 01')
    #
    # logger('DefaultSession')
    # app.PLINSingleFrame(ID, NAD, '02', '10 01')
    #
    # logger('ClearDiagnosticInfo')
    # app.PLINSingleFrame(ID, NAD, '04', '14')
    #
    # logger('ECUReset')
    # app.PLINSingleFrame(ID, NAD, '02', '11 01')
