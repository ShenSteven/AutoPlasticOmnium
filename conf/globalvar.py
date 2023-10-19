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
from common.basicfunc import IsNullOrEmpty, ensure_path_sep


def get_about():
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), '__version__.py'), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


IsHide = False
About = get_about()
VERSION = About['__version__']
WIN: bool = platform.system() == 'Windows'
LINUX: bool = platform.system() == 'Linux'
ConfigYamlPath = abspath(join(dirname(__file__), 'config.yaml'))
cfg = conf.config.read_config(ConfigYamlPath, conf.config.Configs)

CurrentDir = main.bundle_dir
OutPutPath = rf'{CurrentDir}{os.sep}OutPut'
DataPath = rf'{CurrentDir}{os.sep}Data'
ScriptFolder = rf'{CurrentDir}{os.sep}scripts'
ExcelFilePath = rf'{ScriptFolder}{os.sep}{cfg.station.testcase}'
DatabaseSetting = rf'{CurrentDir}{os.sep}conf{os.sep}setting.db'
DatabaseResult = rf'{CurrentDir}{os.sep}OutPut{os.sep}result.db'
retPath = fr'{OutPutPath}\result.csv'
LogFolderPath = ''
CriticalLog = ''
ErrorsLog = ''

StepAttr = []
CheckSnList = []
Keywords = []

IsDebug = False
MainWin = None
LoginWin = None

PCan = None
PLin = None
pMsg32 = None
pMsg33 = None


# def set_global_val(name, value):
#     globals()[name] = value
#
#
# def get_global_val(name, defValue=None):
#     try:
#         return globals()[name]
#     except KeyError:
#         return defValue


def CreateSubLogFolder():
    global LogFolderPath, CriticalLog, ErrorsLog
    LogFolderPath = ensure_path_sep(join(cfg.station.logFolder, datetime.now().strftime('%Y%m%d')))
    try:
        if not exists(LogFolderPath):
            os.makedirs(LogFolderPath)
    except FileNotFoundError:
        cfg.station.logFolder = ensure_path_sep(join(CurrentDir, 'TestLog'))
        LogFolderPath = ensure_path_sep(join(cfg.station.logFolder, datetime.now().strftime('%Y%m%d')))
        if not exists(LogFolderPath):
            os.makedirs(LogFolderPath)
    CriticalLog = (join(cfg.station.logFolder, 'critical.log').replace('\\', '/'))
    ErrorsLog = (join(cfg.station.logFolder, 'errors.log').replace('\\', '/'))


CreateSubLogFolder()
# print(critical_log, errors_log)
lg = LogPrint('debug', CriticalLog, ErrorsLog)
if WIN:
    os.environ['PATH'] = os.environ['PATH'] + ";;" + os.path.join(CurrentDir, rf'ffmpeg{os.sep}bin')
else:
    print(os.environ)


def InitCreateDirs(logger=None):
    try:
        if not IsNullOrEmpty(cfg.station.setTimeZone):
            os.system(f"tzutil /s \"{cfg.station.setTimeZone}\"")
        os.makedirs(LogFolderPath + rf"{os.sep}Json", exist_ok=True)
        os.makedirs(OutPutPath, exist_ok=True)
        os.makedirs(DataPath, exist_ok=True)
        os.makedirs(cfg.station.logFolder + rf"{os.sep}CsvData{os.sep}Upload", exist_ok=True)
    except Exception as e:
        raise Exception(f'{currentframe().f_code.co_name}:{e}')


if __name__ == '__main__':
    pass
