#!/usr/bin/env python
# coding: utf-8
"""
@File   : uds14229.py
@Author : Steven.Shen
@Date   : 7/13/2023
@Desc   : 
"""
import re
import sys
import can
import time
import traceback
from ctypes import *
from enum import Enum
from inspect import currentframe
from common.basicfunc import bytes_to_string, right_round
from communication.peak.plin import PLinApi


def get_datas(logger, filePath_s19):
    s19data = ''
    try:
        with open(filePath_s19, 'rb') as f:
            for line in f:
                if line.decode("utf-8").startswith('S1') or line.decode("utf-8").startswith('S2') or line.decode(
                        "utf-8").startswith('S3'):
                    le = len(line)
                    msg = line[10:(le - 4)]  # Address and checksum are not part of message, and they won't be sent
                    s19data += msg.decode("utf-8")
    except FileNotFoundError:
        logger.debug("File not found")
        raise
    datas = " ".join(re.findall(".{2}", s19data))
    logger.debug(datas)
    return datas


def get_crc_apps19(logger, crc_file_path):
    s19crc = ''
    try:
        logger.debug(crc_file_path)
        with open(crc_file_path, 'rb') as f:
            for line in f:
                le = len(line)
                if le > 13:
                    s19crc = line[10:18].decode("utf-8")
                    s19crc = ' '.join(re.findall(".{2}", s19crc))
                    logger.debug(f'get app s19 crc = {s19crc}')
                    break
    except FileNotFoundError:
        logger.fatal("File not found")
        raise
    return s19crc


class SID(Enum):
    """all uds protocol services"""

    DiagnosticSessionControl = 0x10
    EcuReset = 0x11
    ClearDiagnosticInformation = 0x14
    ReadDTCInformation = 0x19
    ReadDataByIdentifier = 0x22
    ReadMemoryByAddress = 0x23
    ReadScalingDataByIdentifier = 0x24
    SecurityAccess = 0x27
    CommunicationControl = 0x28
    ReadDataByPeriodicIdentifier = 0x2A
    DynamicallyDefineDataIdentifier = 0x2C
    WriteDataByIdentifier = 0x2E
    InputOutputControlByIdentifier = 0x2F
    RoutineControl = 0x31
    RequestDownload = 0x34
    RequestUpload = 0x35
    TransferData = 0x36
    RequestTransferExit = 0x37
    RequestFileTransfer = 0x38
    WriteMemoryByAddress = 0x3D
    TesterPresent = 0x3E
    AccessTimingParameter = 0x83
    SecuredDataTransmission = 0x84
    ControlDTCSetting = 0x85
    ResponseOnEvent = 0x86
    LinkControl = 0x87


class NRC(Enum):
    sub_functionNotSupported = 0x12
    incorrectMessageLengthOrInvalidFormat = 0x13
    conditionsNotCorrect = 0x22
    requestSequenceError = 0x24
    requestOutOfRange = 0x31
    securityAccessDenied = 0x33
    invalidKey = 0x35
    exceededNumberOfAttempts = 0x36
    requiredTimeDelayNotExpired = 0x37
    uploadDownloadNotAccepted = 0x70
    transferDataSuspended = 0x71
    generalProgrammingFailure = 0x72
    wrongBlockSequenceCounter = 0x73
    pending = 0x78


class UDSonLIN:

    def __init__(self, logger, nad, device):
        self.RespDelay = None
        self.ReqDelay = None
        self.Master3C = PLinApi.TLINScheduleSlot()
        self.Slave3D = PLinApi.TLINScheduleSlot()
        self.m_objPLinApi = None
        self.MRtoMRDelay = None
        self.m_hHw = None
        self.m_hClient = None
        self.ReadTxCount = None
        self.NAD = nad
        self.device = device
        self.logger = logger

    def write(self):
        pass

    def read(self):
        pass

    def SendCommand(self):
        pass

    def SFResp(self, _id, rsid, timeout):
        if _id.upper() == '3C':
            _id = '3D'
        pRcvMsg = PLinApi.TLINRcvMsg()
        start_time = time.time()
        self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
        while pRcvMsg.Data[2] != (int(rsid, 16)) or pRcvMsg.Data[1] > 15:
            self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
            if time.time() - start_time > timeout:
                self.logger.error(f"timeout {timeout}s for respond,id")
                return False, ''
            if pRcvMsg.Type != PLinApi.TLIN_MSGTYPE_STANDARD.value:
                continue
            if pRcvMsg.Data[2] == (int('7F', 16)) and pRcvMsg.Data[1] < 16:
                self.logger.debug(
                    f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
                if pRcvMsg.Data[4] == (int("78", 16)):
                    continue
                self.logger.error(f"Negative response!NRC={hex(pRcvMsg.Data[4])}")
                respData = bytes_to_string(pRcvMsg.Data)
                return False, respData
        self.logger.debug(
            f"RX  {_id},{bytes_to_string(pRcvMsg.Data)},{pRcvMsg.Direction},{pRcvMsg.ChecksumType},{'{:02X}'.format(pRcvMsg.Checksum)}")
        return True, bytes_to_string(pRcvMsg.Data)

    def SingleFrame(self, _id, nad, pci, data, timeout=2.0):
        try:
            if self.SetFrameEntry(_id, nad, pci, data):  # send first frame
                RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                return self.SFResp(_id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def MultiFrame(self, _id, nad, pci, data, offset, timeout=2):
        tempData = data.split()
        _len = len(tempData)
        try:
            first_data = ' '.join(tempData[0:offset])
            if self.SetFrameEntry(_id, nad, pci, first_data):  # send first frame
                j = 1
                remainder = (_len - offset) % 6
                quotient = (_len - offset) // 6
                for i in range(quotient + 1):
                    if j == 16:
                        j = 0
                    if i == quotient:
                        if remainder == 0:
                            break
                        else:
                            consecutive_data = ' '.join(tempData[offset + i * 6:offset + i * 6 + remainder])
                    else:
                        consecutive_data = ' '.join(tempData[offset + i * 6:offset + i * 6 + 6])
                    self.ConsecutiveFrame(_id, nad, '{:X}'.format(j), consecutive_data)
                    j = j + 1
                if offset == 5:
                    RSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                else:
                    RSID = '76'  # TransferDataBlock
                return self.SFResp(_id, RSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def ConsecutiveFrame(self, _id, nad, sn, data, log=True, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                         ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        pci = '2' + sn
        self.SetFrameEntry(_id, nad, pci, data, log, direction, ChecksumType)
        return True

    def TransferData(self, _id, nad, file_data, bytesNumOfBlock, timeout=2):
        tempData = file_data.split()
        _len = len(tempData)
        maxBytesNumOfBlock = int(bytesNumOfBlock.replace(" ", ""), 16)
        payloadOfBlock = maxBytesNumOfBlock - 2
        blockNum = _len // payloadOfBlock
        lastBlockNum = _len % payloadOfBlock
        j = 1
        try:
            self.logger.debug(f'Start TransferBlock,Total blockNum: {blockNum}')
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
                self.logger.debug(f'TransferDataBlock:{i}')
                if not self.MultiFrame(_id, nad, pci, blockData, 3, timeout)[0]:
                    self.logger.error('Rx lost!!!')
                    return False
                j = j + 1
            return True
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def SetFrameEntry(self, _id, nad, pci, data, log=True, direction=PLinApi.TLIN_DIRECTION_PUBLISHER,
                      ChecksumType=PLinApi.TLIN_CHECKSUMTYPE_CLASSIC):
        try:
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
                    self.logger.debug(ex)
            linResult = self.m_objPLinApi.SetFrameEntry(self.m_hClient, self.m_hHw, lFrameEntry)
            if linResult == PLinApi.TLIN_ERROR_OK:
                readTxCount = 0
                pRcvMsg = PLinApi.TLINRcvMsg()
                self.m_objPLinApi.ResetClient(self.m_hClient)
                self.m_objPLinApi.UpdateByteArray(self.m_hClient, self.m_hHw, lFrameEntry.FrameId,
                                                  c_ubyte(0), lFrameEntry.Length, lFrameEntry.InitialData)
                while pRcvMsg.FrameId != c_ubyte(int('3C', 16)):
                    time.sleep(self.MRtoMRDelay / 1000)
                    self.m_objPLinApi.Read(self.m_hClient, pRcvMsg)
                    readTxCount += 1
                    if pRcvMsg.Data[1] == lFrameEntry.InitialData[1] \
                            and pRcvMsg.Data[2] == lFrameEntry.InitialData[2] \
                            and pRcvMsg.Data[3] == lFrameEntry.InitialData[3]:
                        if log:
                            self.logger.debug(f"Tx  {_id},{bytes_to_string(pRcvMsg.Data)}")
                        return True
                    if readTxCount == self.ReadTxCount:
                        self.logger.warning(f'readTxCount:{self.ReadTxCount}')
                        break
            self.logger.error(f"Failed to send Consecutive Frame: {_id},{bytes_to_string(lFrameEntry.InitialData)}")
            return False
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def runScheduleDiag(self):
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
            self.SuspendDiagSchedule()
            error_code = self.m_objPLinApi.SetSchedule(self.m_hClient, self.m_hHw, iScheduleNumber, pSchedule,
                                                       len(pSchedule))
            if error_code == PLinApi.TLIN_ERROR_OK:
                error_code = self.m_objPLinApi.StartSchedule(self.m_hClient, self.m_hHw, iScheduleNumber)
                if error_code == PLinApi.TLIN_ERROR_OK:
                    self.logger.info("start schedule success...")
                    time.sleep(0.001)
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
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False


# class LINUdsMsg:
#     def __init__(self):
#         self.ID = 0x3C
#         self.NAD = ''
#         self.PCI_LEN = ''
#         self.SID: SID = SID.EcuReset
#         self.SF = ''
#         self.DID = ''
#         self.Data = ''


class UDSonCAN:
    def __init__(self, logger, can_bus, is_extended_id=False, is_fd=False):
        self.logger = logger
        self.bus = can_bus
        self.is_extended_id = is_extended_id
        self.is_fd = is_fd
        self.RxID = None
        self.TxID = None
        self.SID = None

    def write(self, fid: int, fdata, timeout=2):
        """
        send one can standard frame
        :param fid:
        :param fdata: (bytes | bytearray | int | Iterable[int] | None)
        :param timeout:
        :return:
        """
        with self.bus as bus:
            msg = can.Message(arbitration_id=fid, data=fdata)
            msg.is_extended_id = self.is_extended_id
            msg.is_fd = self.is_fd
            try:
                bus.send(msg, timeout=timeout)
                self.logger.debug(f"Tx  {msg.arbitration_id:X}, {msg.data}.")
                return True
            except can.CanError:
                self.logger.fatal("Message NOT sent")
                return False

    def read(self, respSID, timeout):
        multiFrameDatas = []
        CFSum = 0
        CFCounter = 0
        while True:
            pRcvMsg = self.bus.recv(timeout)
            if pRcvMsg is not None:
                respData = bytes_to_string(pRcvMsg.Data)
                self.logger.debug(f"Rx  {pRcvMsg.arbitration_id:X}, {respData}.")
                if pRcvMsg.arbitration_id == self.TxID:
                    if pRcvMsg.Data[0] <= 15:  # respond is singleFrame
                        if pRcvMsg.Data[1] == (int(respSID, 16)):  # Positive response
                            return True, respData
                        elif pRcvMsg.Data[1] == (int('7F', 16)) and pRcvMsg.Data[2] == self.SID:  # Negative response
                            if pRcvMsg.Data[3] == (int("78", 16)):  # pending
                                continue
                            self.logger.error(f"Negative response!NRC={hex(pRcvMsg.Data[3])}")
                            return False, respData
                        else:
                            return False, ''
                    elif 15 < pRcvMsg.Data[0] < 32:  # respond is FirstFrame of MultiFrame
                        if pRcvMsg.Data[2] == (int(respSID, 16)):  # Positive response
                            multiFrameDatasLen = pRcvMsg.Data[0] + pRcvMsg.Data[1] - 0X1000
                            CFSum = right_round((multiFrameDatasLen - 6) / 7, 0)
                            for j in range(2, 8):
                                multiFrameDatas.append(pRcvMsg.Data[j])
                        elif pRcvMsg.Data[2] == (int('7F', 16)) and pRcvMsg.Data[3] == self.SID:  # Negative response
                            if pRcvMsg.Data[4] == (int("78", 16)):  # pending
                                continue
                            self.logger.error(f"Negative response!NRC={hex(pRcvMsg.Data[3])}")
                        else:
                            return False, ''
                    elif 31 < pRcvMsg.Data[0] < 48:  # respond is Consecutive frames of MultiFrame
                        CFCounter += 1
                        for j in range(1, 8):
                            multiFrameDatas.append(pRcvMsg.Data[j])
                        if CFCounter == CFSum:
                            return True, bytes_to_string(multiFrameDatas)
                    else:
                        self.logger.error(f"unknown frame type!!!")
                        return False, ''
            else:
                return False, ''

    def SendCommand(self, fid: int, data, rSID, timeout):
        if self.write(fid, data, timeout):
            return self.read(rSID, timeout)
        else:
            return False, ''

    # def ReqAndResp(self, fid: int, data, rSID, timeout):
    #     """
    #     send one can standard frame
    #     :param rSID:
    #     :param fid:
    #     :param data: (bytes | bytearray | int | Iterable[int] | None)
    #     :param timeout:
    #     :return:
    #     """
    #     with self.bus as bus:
    #         msg = can.Message(arbitration_id=fid, data=data)
    #         msg.is_extended_id = self.is_extended_id
    #         bus.send(msg, timeout=timeout)
    #         self.logger.debug(f"Tx  :{msg.arbitration_id:X}, {msg.data}.")
    #         # iterate over received messages
    #         # for pRcvMsg in bus:
    #         #     respData = bytes_to_string(pRcvMsg.Data)
    #         #     if pRcvMsg.arbitration_id == self.TxID:
    #         #         if pRcvMsg.Data[1] == (int(rSID, 16)):
    #         #             self.logger.debug(f"Rx  {pRcvMsg.arbitration_id:X}, {pRcvMsg.data}.")
    #         #             return True, bytes_to_string(pRcvMsg.Data)
    #         #         elif pRcvMsg.Data[1] == (int('7F', 16)) and pRcvMsg.Data[2] == self.SID:
    #         #             self.logger.debug(f"RX  {pRcvMsg.arbitration_id:X}, {bytes_to_string(pRcvMsg.Data)}")
    #         #             if pRcvMsg.Data[3] == (int("78", 16)):
    #         #                 continue
    #         #             self.logger.error(f"Negative response!NRC={hex(pRcvMsg.Data[3])}")
    #         #             return False, respData
    #         #         else:
    #         #             pass
    #         #             self.logger.debug(f"Rx3  {pRcvMsg.arbitration_id:X}, {pRcvMsg.data}.")
    #         return False, ''
    #
    #         # or use an asynchronous notifier
    #         # notifier = can.Notifier(bus, [print_msg, can.Logger("logfile.asc"), MyListener(bus)])
    #         # time.sleep(1)
    #         # notifier.stop()

    def SetRxTxID(self, rx_id, grx_id, tx_id):
        if rx_id is '' and grx_id is not '':
            self.RxID = grx_id
        elif rx_id is not '' and grx_id is '':
            self.RxID = rx_id
        else:
            raise ValueError('RxID or GRxID is not correct! Please fill in only one.')
        self.TxID = tx_id

    def SingleFrame(self, rx_id, grx_id, tx_id, pci, data, timeout=2):
        self.SetRxTxID(rx_id, grx_id, tx_id)
        frameData = (pci + " " + data).split()
        self.SID = '{:02X}'.format((int(data.split()[0], 16)))
        PositiveRespSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
        try:
            return self.SendCommand(self.RxID, frameData, PositiveRespSID, timeout)  # send first frame
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def MultiFrame(self, rx_id, grx_id, tx_id, pci, data, timeout=2, maxPayload=6):
        self.SetRxTxID(rx_id, grx_id, tx_id)
        self.SID = '{:02X}'.format((int(data.split()[0], 16)))
        tempData = data.split()
        _len = len(tempData)
        try:
            firstFrameData = (pci + " " + tempData[0:maxPayload]).split()
            if self.write(self.RxID, firstFrameData, timeout):  # send first frame
                j = 1
                remainder = (_len - maxPayload) % 6
                quotient = (_len - maxPayload) // 6
                for i in range(quotient + 1):
                    if j == 16:
                        j = 0
                    if i == quotient:
                        if remainder == 0:
                            break
                        else:
                            consecutive_data = ' '.join(tempData[maxPayload + i * 6:maxPayload + i * 6 + remainder])
                    else:
                        consecutive_data = ' '.join(tempData[maxPayload + i * 6:maxPayload + i * 6 + 6])
                    self.ConsecutiveFrame(self.RxID, '{:X}'.format(j), consecutive_data)
                    j = j + 1
                if maxPayload == 6:
                    PositiveRespSID = '{:02X}'.format((int(data.split()[0], 16) + int("40", 16)))
                else:
                    PositiveRespSID = '76'  # TransferDataBlock
                return self.read(PositiveRespSID, timeout)
            else:
                return False, ""
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False, ""

    def ConsecutiveFrame(self, _id, sn, data):
        pci = '2' + sn
        frameData = (pci + " " + data).split()
        self.write(_id, frameData)
        return True

    def TransferData(self, rx_id, grx_id, tx_id, file_data, bytesNumOfBlock, timeout=2):
        self.SetRxTxID(rx_id, grx_id, tx_id)
        tempData = file_data.split()
        _len = len(tempData)
        maxBytesNumOfBlock = int(bytesNumOfBlock.replace(" ", ""), 16)
        payloadOfBlock = maxBytesNumOfBlock - 2
        blockNum = _len // payloadOfBlock
        lastBlockNum = _len % payloadOfBlock
        j = 1
        try:
            self.logger.debug(f'Start TransferBlock,Total blockNum: {blockNum}')
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
                self.logger.debug(f'TransferDataBlock:{i}')
                if not self.MultiFrame(rx_id, grx_id, tx_id, pci, blockData, 3, timeout)[0]:
                    self.logger.error('Rx lost!!!')
                    return False
                j = j + 1
            return True
        except Exception as ex:
            self.logger.fatal(f'{currentframe().f_code.co_name}:{ex},{traceback.format_exc()}')
            return False

    def CalKey(self, seed, xorMask=0xC0A59221):
        try:
            seeds = seed.split()
            cal = [(int(seeds[0], 16) ^ ((xorMask >> 24) & 0xFF)), (int(seeds[1], 16) ^ ((xorMask >> 16) & 0xFF)),
                   (int(seeds[2], 16) ^ ((xorMask >> 8) & 0xFF)), (int(seeds[3], 16) ^ (xorMask & 0xFF))]
            key1 = ((cal[2] & 0x0F) << 4) | (cal[1] & 0x0F)
            key2 = ((cal[3] & 0x0F) << 4) | ((cal[1] & 0xF0) >> 4)
            key3 = (cal[0] & 0xF0) | ((cal[2] & 0x3C) >> 2)
            key4 = ((cal[0] & 0x0F) << 4) | ((cal[3] & 0x78) >> 3)
            key = '{:02X}'.format(key1) + " " + '{:02X}'.format(key2) + " " + '{:02X}'.format(
                key3) + " " + '{:02X}'.format(key4)
            self.logger.debug(f'get key: {key}')
            return key
        except Exception as ex:
            sys.exit(f'{currentframe().f_code.co_name}:{ex}')
