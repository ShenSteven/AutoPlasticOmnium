#!/usr/bin/env python
# coding: utf-8
"""
@File   : config.py
@Author : Steven.Shen
@Date   : 2021/10/22
@Desc   : config.yaml 配置对象数据结构模型
"""
import yaml


class StationConf:
    privileges: str
    station_all: list
    station_name: str
    station_no: str
    log_folder: str
    log_server: str
    log_server_username: str
    log_server_password: str
    fix_flag: bool
    fix_com_port: str
    fix_com_baudRate: int
    GPIB_address: int
    testcase: str
    fail_continue: bool
    mes_shop_floor: str
    mes_result: str
    rs_url: str
    csv_column: str
    continue_fail_limit: int
    setTimeZone: str

    def __init__(self, dict_):
        self.__dict__.update(dict_)


class DutConf:
    prompt: str
    dut_ip: str
    dut_com_port: str
    dut_com_baudRate: int
    ssh_port: int
    ssh_username: str
    ssh_password: str
    dut_models: list
    dut_regex: dict
    data_api: dict
    sn_len: int
    qsdk_ver: str
    test_mode: str
    debug_skip: list

    def __init__(self, dict_):
        self.__dict__.update(dict_)


class Configs:
    def __init__(self, dict_):
        self.__dict__ = dict_
        self.station = StationConf(dict_['station'])
        self.dut = DutConf(dict_['dut'])
        self.BLF = DutConf(dict_['BLF'])


def read_config(yaml_file, objType) -> Configs:
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        obj = objType(yaml_data)
        return obj


def read_yaml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        return yaml_data


if __name__ == '__main__':
    pass
