#!/usr/bin/env python
# coding: utf-8
"""
@File   : uds14229.py
@Author : Steven.Shen
@Date   : 7/13/2023
@Desc   : 
"""
import traceback
from enum import Enum
from inspect import currentframe


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

    def __init__(self, nad, device, logger):
        self.NAD = nad
        self.device = device
        self.logger = logger

    def initialize(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def singleFrame(self):
        pass

    def multiFrame(self):
        pass

    def setFrame(self, _id, nad, pci, data, log=True):
        pass

    def TransferData(self):
        pass


class LINUdsMsg:
    def __init__(self):
        self.ID = 0x3C
        self.NAD = ''
        self.PCI_LEN = ''
        self.SID: SID = SID.EcuReset
        self.SF = ''
        self.DID = ''
        self.Data = ''


class UDSonCAN:
    pass
