#!/usr/bin/env python
# coding: utf-8
"""
@File   : globalconf.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 加载配置文件中的变量
"""
import json
import yaml
import logging.config
from os.path import dirname, abspath, join, exists
from string import Template
from bin.yamlread import YamlConfig

# load logger config
current_path = dirname(abspath(__file__))
logging_yaml = join(current_path, 'logging.yaml')
log_conf = YamlConfig(logging_yaml).read_yaml()
res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
    {'log_file': r'F:/pyside2/log/log_file.txt',
     'critical_log': 'F:/pyside2/log/critical_log.txt',
     'errors_log': 'F:/pyside2/log/errors_log.txt'})
logging.config.dictConfig(yaml.safe_load(res_log_conf))
logger = logging.getLogger('testlog')

# load test global variable
config_yaml = join(current_path, 'config.yaml')
YamlConfig_obj = YamlConfig(config_yaml)
gConfig = YamlConfig_obj.read_yaml()
res_gConfig = Template(json.dumps(gConfig)).safe_substitute(
    {'$test_log_folder': r'D:/TestLog' if exists(r'D:/') else r'C:/TestLog'})
config = json.loads(res_gConfig)
c_station = globals()[f'config']['station']
c_dut = globals()['config']['dut']
c_count = globals()['config']['count_num']


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
