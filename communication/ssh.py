#!/usr/bin/env python
# coding: utf-8
"""
@File   : ssh.py
@Author : Steven.Shen
@Date   : 2021/9/6
@Desc   : 
"""
import re
import traceback
import time
import paramiko
from common.basicfunc import IsNullOrEmpty
from communication.communication import CommAbstract


class SSH(CommAbstract):
    def __init__(self, logger, host, username, password, prompt, port=22):
        self.sftp = None
        self.logger = logger
        self.prompt = prompt
        self.ssh = paramiko.SSHClient()
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def open(self, *args):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, self.port, self.username, self.password)
        self.sftp = self.ssh.open_sftp()

    def close(self):
        self.sftp.close()
        self.ssh.close()
        self.logger.debug(f"ssh close success!")

    def read(self):
        pass
        # self.tel.read_all()

    def write(self, date: str):
        self.ssh.exec_command(date)

    def SendCommand(self, command, exceptStr=None, timeout=10, newline=True):
        strRecAll = ''
        start_time = time.time()
        if exceptStr is None:
            exceptStr = self.prompt
        try:
            if newline and not IsNullOrEmpty(command) and not command == '\n':
                command += "\n"
            else:
                pass
            self.logger.debug(f"SSH_SendCmd-->{command}")
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)
            outputBytes = stdout.read() + stderr.read()
            strRecAll = outputBytes.decode('utf8')
            self.logger.debug(strRecAll)
            if re.search(exceptStr, strRecAll):
                self.logger.info(f'send: {command} wait: {exceptStr} success in {round(time.time() - start_time, 3)}s')
                result = True
            else:
                self.logger.error(f'send: {command} wait: {exceptStr} timeout in {round(time.time() - start_time, 3)}s')
                result = False
            return result, strRecAll
        except Exception as e:
            self.logger.fatal(f'{e}, {traceback.format_exc()}')
            return False, strRecAll

        # 用一行命令 进入目录 testdir 并且 查看当前路径
        # stdin, stdout, stderr = ssh.exec_command("cd testdir;pwd")
        # print(stdout.read())
        # put方法上传文件，第1个参数是本地路径，第2个参数是远程路径
        # sftp.put('install.zip', '/home/byhy/install.zip')
        # get方法下载文件，第1个参数是远程路径，第2个参数是本地路径
        # sftp.get('/home/byhy/log.zip', 'd:/log.zip')
