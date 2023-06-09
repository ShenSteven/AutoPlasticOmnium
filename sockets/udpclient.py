#!/usr/bin/env python
# coding: utf-8
"""
@File   : udpclient.py
@Author : Steven.Shen
@Date   : 4/3/2023
@Desc   : 
"""
import json
import re
import socket
import time
import traceback
from common.basicfunc import IsNullOrEmpty
from sockets.communication import CommAbstract


class UDPClient(CommAbstract):
    def __init__(self, logger, host, port, prompt):
        self.client_socket = None
        self.logger = logger
        self.BUFF_LEN = 1024
        self.SERVER_ADDR = (host, port)
        self.prompt = prompt
        self.host = host
        self.port = port

    def open(self, *args):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(2)

    def close(self):
        self.client_socket.close()
        self.logger.debug(f"ssh close success!")

    def read(self):
        pass

    def write(self, date: str):
        pass

    def SendCommand(self, message, exceptStr=None, timeout=2, newline=True):
        strRecAll = ''
        start_time = time.time()
        self.client_socket.settimeout(timeout)
        if exceptStr is None:
            exceptStr = self.prompt
        if isinstance(message, dict):
            send_bytes = json.dumps(message).encode('utf8')
        else:
            send_bytes = message.encode('utf8')
        self.client_socket.sendto(send_bytes, self.SERVER_ADDR)
        try:
            recv_bytes, server = self.client_socket.recvfrom(self.BUFF_LEN)
            strRecAll = json.loads(recv_bytes.decode('utf8'))
            self.logger.debug(strRecAll)
            if IsNullOrEmpty(exceptStr):
                return True, strRecAll
            if re.search(exceptStr, strRecAll):
                self.logger.info(f'send: {message} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                self.logger.error(f'send: {message} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except socket.timeout:
            self.logger.fatal(f'"接收消息超时", {traceback.format_exc()}')
            return False, strRecAll
        except Exception as e:
            self.logger.fatal(f'{e}, {traceback.format_exc()}')
            return False, strRecAll
