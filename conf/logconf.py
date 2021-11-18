#!/usr/bin/env python
# coding: utf-8
"""
@File   : logconf.py
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
from os.path import dirname, abspath, join, exists
from PySide2.QtCore import Qt
import conf.globalvar as gv
import conf

current_path = dirname(abspath(__file__))
above_current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# testlog_file path
log_folder_date = join(gv.cf.station.log_folder, datetime.now().strftime('%Y%m%d'))
try:
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)
except FileNotFoundError:
    log_folder = join(above_current_path, 'log')
    log_folder_date = join(above_current_path, 'log', datetime.now().strftime('%Y%m%d'))
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)

log_file = os.path.join(log_folder_date, f"{datetime.now().strftime('%H-%M-%S')}.txt").replace('\\', '/')
critical_log = join(log_folder_date, 'critical.log').replace('\\', '/')
errors_log = join(log_folder_date, 'errors.log').replace('\\', '/')

# load logger config
logging_yaml = join(current_path, 'logging.yaml')
log_conf = conf.read_yaml(logging_yaml)
res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
    {'log_file': log_file,
     'critical_log': critical_log,
     'errors_log': errors_log})
logging.config.dictConfig(yaml.safe_load(res_log_conf))
logger = logging.getLogger('testlog')


class QTextEditHandler(logging.Handler):
    def __init__(self, stream=None):
        logging.Handler.__init__(self)
        if stream is None or stream == 'None':
            stream = sys.stdout
        self.stream = stream

    def emit(self, record):
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
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = getattr(self.stream, 'name', '')
        #  bpo-36015: name can be an int
        name = str(name)
        if name:
            name += ' '
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)


if __name__ == "__main__":
    pass
