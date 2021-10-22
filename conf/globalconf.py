#!/usr/c/env python
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

from conf.config import Configs


def read_config(yaml_file, objType) -> Configs:
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        obj = objType(yaml_data)
        return obj


def read_yaml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        return yaml_data


def save_config(yaml_file, obj):
    with open(yaml_file, mode='r+', encoding='utf-8') as f:
        readall = f.read()
        try:
            js = json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=4)
            ya = yaml.safe_load(js)
            f.seek(0)
            yaml.safe_dump(ya, stream=f, default_flow_style=False, sort_keys=False, indent=4)
        except Exception as e:
            logger.exception(f"save_config! {e}")
            f.seek(0)
            f.write(readall)
        else:
            logger.info(f"save conf.yaml success!")


current_path = dirname(abspath(__file__))
above_current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# load test global variable
config_yaml_path = join(current_path, 'config.yaml')
c = read_config(config_yaml_path, Configs)

log_folder_date = join(c.station.log_folder, datetime.now().strftime('%Y%m%d'))
try:
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)
except FileNotFoundError:
    log_folder = join(above_current_path, 'log')
    log_folder_date = join(above_current_path, 'log', datetime.now().strftime('%Y%m%d'))
    if not exists(log_folder_date):
        os.makedirs(log_folder_date)
testlog_file = os.path.join(log_folder_date, f"{datetime.now().strftime('%H-%M-%S')}.txt").replace('\\', '/')

# load logger c
logging_yaml = join(current_path, 'logging.yaml')
print(logging_yaml)
log_conf = read_yaml(logging_yaml)
res_log_conf = Template(json.dumps(log_conf)).safe_substitute(
    {'log_file': testlog_file,
     'critical_log': join(log_folder_date, 'critical.log').replace('\\', '/'),
     'errors_log': join(log_folder_date, 'errors.log').replace('\\', '/')})
logging.config.dictConfig(yaml.safe_load(res_log_conf))
logger = logging.getLogger('testlog')


def save_conf_to_yaml():
    save_config(config_yaml_path, c)


if __name__ == '__main__':
    logger.debug('--------------------')
    print(c)
    print(c.station.log_server)
    print(c.dut.dut_ip)
    print(c.count.continue_fail_count)
    print(c.station.station_name)
    c.station.station_name = 'SRF'
    print(c.station.station_name)
    print(c.dut.dut_ip)
    save_config('config.yaml', c)
