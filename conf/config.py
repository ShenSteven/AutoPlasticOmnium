#!/usr/bin/env python
# coding: utf-8
"""
@File   : config.py
@Author : Steven.Shen
@Date   : 2021/10/22
@Desc   : config.yaml 配置对象数据结构模型
"""
import json

import yaml


class Conf:
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

    def __init__(self, dict_=None):
        if dict_ is not None:
            self.__dict__.update(dict_)

    def __getitem__(self, i):
        if i >= len(self.__dict__.items()):
            raise IndexError("out of index")
        item = list(self.__dict__.items())[i]
        return item


class Configs:
    def __init__(self, dict_=None):
        if dict_ is not None:
            self.__dict__.update(dict_)
        self.station = Conf(dict_['station'])
        self.dut = Conf(dict_['dut'])
        self.BLF = Conf(dict_['BLF'])
        self.RUNIN = Conf(dict_['RUNIN'])

    def __getitem__(self, i):
        if i >= len(self.__dict__.items()):
            raise IndexError("out of index")
        item = list(self.__dict__.items())[i]
        return item


def read_config(yaml_file, objType) -> Configs:
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.unsafe_load(f)
        obj = objType(yaml_data)
        return obj


def save_config(obj, path):
    with open(path, 'r+', encoding='utf-8') as rf:
        readall = rf.read()
        try:
            with open(path, 'w', encoding='utf-8') as wf:
                yaml.dump(dict(obj), wf, sort_keys=False, indent=4)
        except Exception as e:
            print(f"save_config! {e}")
            rf.seek(0)
            rf.write(readall)
            raise
        else:
            print(f"save conf.yaml success!")


def read_yaml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        return yaml_data


if __name__ == '__main__':
    pass
    cf = read_config('config.yaml', Configs)
    cf.station.station_all.append('LTT9')
    save_config(cf, 'config.yaml')
