#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalvar.py
@Author : Steven.Shen
@Date   : 2021/9/8
@Desc   : 全局变量
"""
import os
from datetime import datetime
from inspect import currentframe
from os.path import join, abspath, dirname, exists
import conf.config
import platform
from conf.logprint import LogPrint
import main
from model.basicfunc import IsNullOrEmpty


def get_about():
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), '__version__.py'), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


about = get_about()
version = about['__version__']
win = platform.system() == 'Windows'
linux = platform.system() == 'Linux'
config_yaml_path = abspath(join(dirname(__file__), 'config.yaml'))
cf = conf.config.read_config(config_yaml_path, conf.config.Configs)

current_dir = main.bundle_dir
OutPutPath = rf'{current_dir}\OutPut'
DataPath = rf'{current_dir}\Data'
scriptFolder = rf'{current_dir}\scripts'
excel_file_path = rf'{scriptFolder}\{cf.station.testcase}'
test_script_json = rf'{scriptFolder}\{cf.station.station_name}.json'
database_setting = rf'{current_dir}\conf\setting.db'
database_result = rf'{current_dir}\OutPut\result.db'
max_step_count = 0
items = []

logFolderPath = ''
critical_log = ''
errors_log = ''
CheckSnList = []

IsDebug = False
mainWin = None
loginWin = None

PLin = None
pMsg32 = None
pMsg33 = None


def set_global_val(name, value):
    globals()[name] = value


def get_global_val(name, defValue=None):
    try:
        return globals()[name]
    except KeyError:
        return defValue


def create_sub_log_folder():
    global logFolderPath, critical_log, errors_log
    logFolderPath = join(cf.station.log_folder, datetime.now().strftime('%Y%m%d'))
    try:
        if not exists(logFolderPath):
            os.makedirs(logFolderPath)
    except FileNotFoundError:
        cf.station.log_folder = join(current_dir, 'testlog')
        logFolderPath = join(cf.station.log_folder, datetime.now().strftime('%Y%m%d'))
        if not exists(logFolderPath):
            os.makedirs(logFolderPath)
    critical_log = join(cf.station.log_folder, 'critical.log').replace('\\', '/')
    errors_log = join(cf.station.log_folder, 'errors.log').replace('\\', '/')


create_sub_log_folder()
lg = LogPrint('debug', critical_log, errors_log)


def init_create_dirs(logger):
    try:
        if not IsNullOrEmpty(cf.station.setTimeZone):
            os.system(f"tzutil /s \"{cf.station.setTimeZone}\"")
        os.makedirs(logFolderPath + r"\Json", exist_ok=True)
        os.makedirs(OutPutPath, exist_ok=True)
        os.makedirs(DataPath, exist_ok=True)
        os.makedirs(cf.station.log_folder + r"\CsvData\Upload", exist_ok=True)
    except Exception as e:
        logger.fatal(f'{currentframe().f_code.co_name}:{e}')


if __name__ == '__main__':
    pass
