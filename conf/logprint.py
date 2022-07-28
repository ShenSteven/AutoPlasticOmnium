#!/usr/bin/env python
# coding: utf-8
"""
@File   : logprint.py
@Author : Steven.Shen
@Date   : 2021/11/4
@Desc   : 
"""
import json
import os
import sys
from string import Template

import yaml
from datetime import datetime
import logging.config
from os.path import join, exists, abspath, dirname
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget
import conf.globalvar as gv
import conf.config

# test log_file path
gv.logFolderPath = join(gv.cf.station.log_folder, datetime.now().strftime('%Y%m%d'))
try:
    if not exists(gv.logFolderPath):
        os.makedirs(gv.logFolderPath)
except FileNotFoundError:
    gv.cf.station.log_folder = join(gv.current_dir, 'testlog')
    gv.logFolderPath = join(gv.cf.station.log_folder, datetime.now().strftime('%Y%m%d'))
    if not exists(gv.logFolderPath):
        os.makedirs(gv.logFolderPath)

log_file = os.path.join(gv.logFolderPath, f"file_handler_{datetime.now().strftime('%H-%M-%S')}.txt").replace('\\', '/')
critical_log = join(gv.cf.station.log_folder, 'critical.log').replace('\\', '/')
errors_log = join(gv.cf.station.log_folder, 'errors.log').replace('\\', '/')

# load logger config
logging_yaml = abspath(join(dirname(__file__), 'logging.yaml'))
log_conf = conf.config.read_yaml(logging_yaml)
res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
    {'log_file': log_file, 'critical_log': critical_log, 'errors_log': errors_log})
logging.config.dictConfig(yaml.safe_load(res_log_conf))
logger = logging.getLogger('testlog')


class QTextEditHandler(logging.Handler, QWidget):
    """继承logging.Handler类，并重写emit方法，创建打印到控件QTextEdit的handler class，并按照日志级别设置字体颜色."""
    mySignal = pyqtSignal()

    def __init__(self, stream=None):
        logging.Handler.__init__(self)
        QWidget.__init__(self)
        if stream is None or stream == 'None':
            stream = sys.stdout
        self.stream = stream
        self.mySignal.connect(self.scrollbarTo)

    def emit(self, record):
        # return
        try:
            msg = self.format(record)
            stream = self.stream
            if 'INFO' in msg:  # pass
                self.stream.setTextColor(Qt.blue)
            elif 'DEBUG' in msg:  # debug info
                self.stream.setTextColor(Qt.black)
            elif 'ERROR' in msg:  # fail
                self.stream.setTextColor(Qt.red)
            elif 'CRITICAL' in msg:  # except
                self.stream.setTextColor(Qt.darkRed)
            elif 'WARNING' in msg:  # warn
                self.stream.setTextColor(Qt.darkYellow)
            elif 'NOTSET' in msg:  #
                self.stream.setTextColor(Qt.blue)
            stream.append(msg)
            self.mySignal.emit()
        except RecursionError:  # See issue 36272
            print('RecursionError')
            raise
        except Exception:
            self.handleError(record)
            raise

    def scrollbarTo(self):
        self.stream.ensureCursorVisible()


if __name__ == "__main__":
    pass
