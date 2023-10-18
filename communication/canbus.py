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
