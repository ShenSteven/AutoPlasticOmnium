#!/usr/bin/env python
# coding: utf-8
"""
@File   : config.py
@Author : Steven.Shen
@Date   : 2021/10/22
@Desc   : config.yaml 对象数据结构模型
"""


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
    prompt: str
    fail_continue: bool
    mes_shop_floor: str
    mes_result: str
    csv_column: str
    test_software_version: str

    def __init__(self, dict_):
        self.__dict__.update(dict_)


class DutConf:
    dut_ip: str
    dut_com_port: str
    dut_com_baudRate: int
    ssh_port: int
    ssh_username: str
    ssh_password: str
    dut_modes: list
    dut_regex: dict
    data_api: dict
    sn_len: int
    qsdk_ver: str
    test_mode: str

    def __init__(self, dict_):
        self.__dict__.update(dict_)


class CountConf:
    continue_fail_count: int
    continue_fail_limit: int
    total_pass_count: int
    total_fail_count: int
    total_abort_count: int

    def __init__(self, dict_):
        self.__dict__.update(dict_)


class Configs:
    def __init__(self, dict_):
        self.__dict__ = dict_
        self.station = StationConf(dict_['station'])
        self.dut = DutConf(dict_['dut'])
        self.count = CountConf(dict_['count'])


if __name__ == '__main__':
    pass
