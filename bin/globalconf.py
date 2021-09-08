#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalconf.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 加载配置文件中的变量
"""
import json
import os
from datetime import datetime

import yaml
import logging.config
from os.path import dirname, abspath, join, exists
from string import Template
from bin.yamlread import YamlConfig

current_path = dirname(abspath(__file__))
above_current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

log_folder = r'R:/TestLog'
log_folder_date = join(log_folder, datetime.now().strftime('%Y%m%d'))
try:
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)
except FileNotFoundError:
    log_folder = join(above_current_path, 'log')
    log_folder_date = join(above_current_path, 'log', datetime.now().strftime('%Y%m%d'))
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)

# load test global variable
config_yaml = join(current_path, 'config.yaml')
YamlConfig_obj = YamlConfig(config_yaml)
gConfig = YamlConfig_obj.read_yaml()
res_gConfig = Template(json.dumps(gConfig)).safe_substitute(
    {'$test_log_folder': log_folder})
config = json.loads(res_gConfig)
c_station = globals()[f'config']['station']
c_dut = globals()['config']['dut']
c_count = globals()['config']['count_num']

testlog_file = os.path.join(log_folder_date, f"{datetime.now().strftime('%H-%M-%S')}.txt").replace('\\', '/')
# load logger config
logging_yaml = join(current_path, 'logging.yaml')
print(logging_yaml)
log_conf = YamlConfig(logging_yaml).read_yaml()
res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
    {'log_file': testlog_file,
     'critical_log': join(log_folder_date, 'critical_log.txt').replace('\\', '/'),
     'errors_log': join(log_folder_date, 'errors_log.txt').replace('\\', '/')})
logging.config.dictConfig(yaml.safe_load(res_log_conf))
logger = logging.getLogger('testlog')


def save_global_conf():
    YamlConfig_obj.write_config(config)


# def set_global(name, value):
#     globals()[name] = value
#
#
# def get_global(name, defValue=None):
#     try:
#         return globals()[name]
#     except KeyError:
#         return defValue
#
#
# def get_all_global():
#     return globals()


if __name__ == '__main__':
    logger.debug('sdsdsd1111111111111111111111111')
    # c_station['debug'] = True
    print(config)
    print(c_station)
    print(c_dut)
    print(c_count)
    # save_global_conf()
