#!/usr/bin/env python
# coding: utf-8
"""
@File   : canbus.py
@Author : Steven.Shen
@Date   : 5/16/2023
@Desc   : 
"""
import time
import can
from abc import ABC
from can import Listener
from can.message import Message


class CanBus:
    is_extended_id: bool = False
    is_remote_frame: bool = False
    is_error_frame: bool = False
    is_fd: bool = False
    is_rx: bool = False

    def __init__(self, logger=None, interface=None, channel=None, context=None, **kwargs):
        self.logger = logger
        self.bus = can.Bus(interface=interface, channel=channel, config_context=context, ignore_config=False,
                           **kwargs)

    def open(self, *args):
        pass

    def close(self):
        self.bus.shutdown()

    def read(self):
        print('Waiting for RX CAN messages ...')
        try:
            while True:
                msg = self.bus.recv(1)
                if msg is not None:
                    print(msg)
        except KeyboardInterrupt:
            pass

    def send_one(self, fid: int, data, timeout):
        """
        send one can standard frame
        :param fid:
        :param data: (bytes | bytearray | int | Iterable[int] | None)
        :param timeout:
        :return:
        """
        with self.bus as bus:
            msg = can.Message(arbitration_id=fid, data=data)
            msg.is_extended_id = self.is_extended_id
            msg.is_remote_frame = self.is_remote_frame
            msg.is_error_frame = self.is_error_frame
            msg.is_fd = self.is_fd
            msg.is_rx = self.is_rx
            try:
                bus.send(msg, timeout=timeout)
                # self.logger.debug(f"Message sent on {bus.channel_info}:id:{msg.arbitration_id:X}, {msg.data}")
                print(f"Message sent on {bus.channel_info}, id:{msg.arbitration_id:X}, {msg.data}")
            except can.CanError:
                self.logger.fatal("Message NOT sent")

    def simple_periodic_send(self, fid, data, period, timeout=2):
        """
        Sends a message every period with no explicit timeout Sleeps for 2 seconds then stops the task.
        :param fid: frame ID
        :param data: frame data field
        :param period: Unit: second
        :param timeout: Unit: second
        :return:
        """
        # self.logger.debug(f"Starting to send a message every {period * 1000}ms for {timeout}s")
        print(f"Starting to send a message every {period * 1000}ms for {timeout}s")
        msg = can.Message(arbitration_id=fid, data=data)
        msg.is_extended_id = self.is_extended_id
        msg.is_remote_frame = self.is_remote_frame
        msg.is_error_frame = self.is_error_frame
        msg.is_fd = self.is_fd
        msg.is_rx = self.is_rx
        task = self.bus.send_periodic(msg, period)
        assert isinstance(task, can.CyclicSendTaskABC)
        time.sleep(timeout)
        task.stop()
        # self.logger.debug("stopped periodic cyclic send")
        print("stopped periodic cyclic send")

    def limited_periodic_send(self, fid, data, period, duration):
        """
        Send using LimitedDurationCyclicSendTaskABC.
        :param fid: frame ID
        :param data: frame data field
        :param period: Unit: second
        :param duration: Unit: second
        :return:
        """
        self.logger.debug("Starting to send a message every 200ms for 1s")
        msg = can.Message(arbitration_id=fid, data=data)
        msg.is_extended_id = self.is_extended_id
        msg.is_remote_frame = self.is_remote_frame
        msg.is_error_frame = self.is_error_frame
        msg.is_fd = self.is_fd
        msg.is_rx = self.is_rx
        task = self.bus.send_periodic(msg, period, duration, store_task=False)
        if not isinstance(task, can.LimitedDurationCyclicSendTaskABC):
            self.logger.debug("This interface doesn't seem to support LimitedDurationCyclicSendTaskABC")
            task.stop()
            return
        time.sleep(2)
        self.logger.debug("Cyclic send should have stopped as duration expired")

    def SendCommand(self, fid, data, timeout=10, exceptStr=None):
        """

        :param fid:
        :param data:
        :param timeout:
        :param exceptStr:
        :return:
        """
        with self.bus as bus:
            msg = can.Message(arbitration_id=fid, data=data)
            msg.is_extended_id = self.is_extended_id
            msg.is_remote_frame = self.is_remote_frame
            msg.is_error_frame = self.is_error_frame
            msg.is_fd = self.is_fd
            msg.is_rx = self.is_rx
            try:
                bus.send(msg, timeout=timeout)
                self.logger.debug(f"Message sent on {bus.channel_info}, id:{msg.arbitration_id:X}, {msg.data}")
                # iterate over received messages
                for msg in bus:
                    self.logger.debug(f"Message received: {msg.arbitration_id:X}: {msg.data}")
                # or use an asynchronous notifier
                notifier = can.Notifier(bus, [print_msg, can.Logger("logfile.asc"), MyListener(bus)])
                time.sleep(1)
                notifier.stop()
            except can.CanError:
                self.logger.fatal("Message NOT sent")


class MyListener(Listener, ABC):
    def __init__(self, bus):
        super(MyListener, self).__init__()
        self.bus = bus

    def on_message_received(self, msg: Message) -> None:
        """
        example
        when receive message 0x123，transmit message 0x456
        """
        if msg.arbitration_id == 0x123:
            transmit_msg = can.Message(arbitration_id=0x456,
                                       dlc=8,
                                       data=[0 for _ in range(8)],
                                       is_extended_id=False)
            self.bus.send(transmit_msg)


def print_msg(msg):
    print(msg)


if __name__ == "__main__":
    pass
    # import conf.globalvar as gv
    # bus = can.Bus(interface='vector', channel=1, bitrate=500000, app_name='python-can')
    # msg = can.Message(arbitration_id=0x341, data=[0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    # bus.send(msg)
    bus_test = CanBus(None, interface='vector', channel=1, bitrate=500000, app_name='python-can')
    while True:
        bus_test.simple_periodic_send(0x341, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.01)
        bus_test.simple_periodic_send(0x341, [0x82, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.01)
        bus_test.simple_periodic_send(0x341, [0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.01)
        bus_test.simple_periodic_send(0x341, [0x84, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.01)
        bus_test.simple_periodic_send(0x341, [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.01)
    # bus = can.interface.Bus('virtual_ch', bustype='virtual')
    # logger = can.Logger("logfile.asc")  # save log to asc file
    # listeners = [
    #     print_msg,  # Callback function, print the received messages
    #     logger,  # save received messages to asc file
    #     MyListener(bus)  # my listener
    # ]
    # notifier = can.Notifier(bus, listeners)
    # running = True
    # while running:
    #     input()
    #     running = False
    #
    # # It's important to stop the notifier in order to finish the writting of asc file
    # notifier.stop()
    # # stops the bus
    # bus.shutdown()

    CRC_FINAL_XOR_CRC8 = 0xFF
    Crc_Table8 = [
        0x00, 0x1d, 0x3a, 0x27,
        0x74, 0x69, 0x4e, 0x53,
        0xe8, 0xf5, 0xd2, 0xcf,
        0x9c, 0x81, 0xa6, 0xbb,
        0xcd, 0xd0, 0xf7, 0xea,
        0xb9, 0xa4, 0x83, 0x9e,
        0x25, 0x38, 0x1f, 0x02,
        0x51, 0x4c, 0x6b, 0x76,
        0x87, 0x9a, 0xbd, 0xa0,
        0xf3, 0xee, 0xc9, 0xd4,
        0x6f, 0x72, 0x55, 0x48,
        0x1b, 0x06, 0x21, 0x3c,
        0x4a, 0x57, 0x70, 0x6d,
        0x3e, 0x23, 0x04, 0x19,
        0xa2, 0xbf, 0x98, 0x85,
        0xd6, 0xcb, 0xec, 0xf1,
        0x13, 0x0e, 0x29, 0x34,
        0x67, 0x7a, 0x5d, 0x40,
        0xfb, 0xe6, 0xc1, 0xdc,
        0x8f, 0x92, 0xb5, 0xa8,
        0xde, 0xc3, 0xe4, 0xf9,
        0xaa, 0xb7, 0x90, 0x8d,
        0x36, 0x2b, 0x0c, 0x11,
        0x42, 0x5f, 0x78, 0x65,
        0x94, 0x89, 0xae, 0xb3,
        0xe0, 0xfd, 0xda, 0xc7,
        0x7c, 0x61, 0x46, 0x5b,
        0x08, 0x15, 0x32, 0x2f,
        0x59, 0x44, 0x63, 0x7e,
        0x2d, 0x30, 0x17, 0x0a,
        0xb1, 0xac, 0x8b, 0x96,
        0xc5, 0xd8, 0xff, 0xe2,
        0x26, 0x3b, 0x1c, 0x01,
        0x52, 0x4f, 0x68, 0x75,
        0xce, 0xd3, 0xf4, 0xe9,
        0xba, 0xa7, 0x80, 0x9d,
        0xeb, 0xf6, 0xd1, 0xcc,
        0x9f, 0x82, 0xa5, 0xb8,
        0x03, 0x1e, 0x39, 0x24,
        0x77, 0x6a, 0x4d, 0x50,
        0xa1, 0xbc, 0x9b, 0x86,
        0xd5, 0xc8, 0xef, 0xf2,
        0x49, 0x54, 0x73, 0x6e,
        0x3d, 0x20, 0x07, 0x1a,
        0x6c, 0x71, 0x56, 0x4b,
        0x18, 0x05, 0x22, 0x3f,
        0x84, 0x99, 0xbe, 0xa3,
        0xf0, 0xed, 0xca, 0xd7,
        0x35, 0x28, 0x0f, 0x12,
        0x41, 0x5c, 0x7b, 0x66,
        0xdd, 0xc0, 0xe7, 0xfa,
        0xa9, 0xb4, 0x93, 0x8e,
        0xf8, 0xe5, 0xc2, 0xdf,
        0x8c, 0x91, 0xb6, 0xab,
        0x10, 0x0d, 0x2a, 0x37,
        0x64, 0x79, 0x5e, 0x43,
        0xb2, 0xaf, 0x88, 0x95,
        0xc6, 0xdb, 0xfc, 0xe1,
        0x5a, 0x47, 0x60, 0x7d,
        0x2e, 0x33, 0x14, 0x09,
        0x7f, 0x62, 0x45, 0x58,
        0x0b, 0x16, 0x31, 0x2c,
        0x97, 0x8a, 0xad, 0xb0,
        0xe3, 0xfe, 0xd9, 0xc4
    ]

    message320_DataID = []
    message320_Data = []


    def RollingCounterCRC8(data, length, startValue):
        Crc_Value = CRC_FINAL_XOR_CRC8 ^ startValue
        for i in range(length):
            Crc_Value = Crc_Table8[Crc_Value ^ data[i]]
        crcValueNew = Crc_Value ^ CRC_FINAL_XOR_CRC8
        return crcValueNew


    u8_Mes320Bz = 0


    def grate_frame():
        # Rolling counter
        Env_Var_Mes320Crc = 1
        global u8_Mes320Bz
        if u8_Mes320Bz >= 14:
            u8_Mes320Bz = 0
        else:
            u8_Mes320Bz += 1

        sum_CRC = 0
        if Env_Var_Mes320Crc == 1:
            message320_DataID[0] = 0x20
            message320_DataID[1] = 0x03
            sum_CRC = RollingCounterCRC8(message320_DataID, 2, 0xFF)
            message320_Data[0] = u8_Mes320Bz
            message320_Data[1] = 0x0C
            message320_Data[2] = 0
            message320_Data[3] = 0
            message320_Data[4] = 0
            message320_Data[5] = 0
            message320_Data[6] = 0

            sum_CRC = RollingCounterCRC8(message320_Data, 7, sum_CRC)
            sum_CRC = sum_CRC ^ 0xFF

        u8_Mes320Crc = sum_CRC
