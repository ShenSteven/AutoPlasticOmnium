#!/usr/bin/env python
# coding: utf-8
"""
@File   : logprint.py
@Author : Steven.Shen
@Date   : 2021/11/4
@Desc   : 
"""
import json
import sys
from string import Template
import yaml
import logging.config
from os.path import join, abspath, dirname
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget
import conf.config


class LogPrint:
    def __init__(self, log_file, critical_log, errors_log):
        self.logger = None
        self.reconfig_logger(log_file, critical_log, errors_log)

    def reconfig_logger(self, log_file, critical_log, errors_log):
        logging_yaml = abspath(join(dirname(__file__), 'logging.yaml'))
        log_conf = conf.config.read_yaml(logging_yaml)
        res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
            {'log_file': log_file, 'critical_log': critical_log, 'errors_log': errors_log})
        logging.config.dictConfig(yaml.safe_load(res_log_conf))
        self.logger = logging.getLogger('testlog')


class QTextEditHandler(logging.Handler, QWidget):
    """继承logging.Handler类，并重写emit方法，创建打印到控件QTextEdit的handler class，并按照日志级别设置字体颜色."""
    mySignal = pyqtSignal(str)

    def __init__(self, stream=None):
        logging.Handler.__init__(self)
        QWidget.__init__(self)
        if stream is None or stream == 'None':
            stream = sys.stdout
        self.stream = stream
        self.mySignal[str].connect(self.append_scrollbar)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.mySignal[str].emit(msg)
        except RecursionError:  # See issue 36272
            raise
        except RuntimeError:
            print('logprint.emit():RuntimeError')
        except Exception:
            self.handleError(record)
            raise

    def append_scrollbar(self, msg):
        """
        CRITICAL = 50
        FATAL = CRITICAL
        ERROR = 40
        WARNING = 30
        INFO = 20
        DEBUG = 10
        NOTSET = 0
        """
        if 'NOTSET' in msg:  #
            self.stream.setTextColor(Qt.blue)
        elif 'DEBUG' in msg:  # debug info
            self.stream.setTextColor(Qt.black)
        elif 'INFO' in msg:  # pass
            self.stream.setTextColor(Qt.blue)
        elif 'WARNING' in msg:  # warn
            self.stream.setTextColor(Qt.darkYellow)
        elif 'ERROR' in msg:  # fail
            self.stream.setTextColor(Qt.red)
        elif 'CRITICAL' in msg or 'FATAL' in msg:  # except
            self.stream.setTextColor(Qt.darkRed)
        self.stream.append(msg)
        self.stream.ensureCursorVisible()


if __name__ == "__main__":
    pass
