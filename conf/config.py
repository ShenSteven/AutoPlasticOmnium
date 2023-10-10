#!/usr/bin/env python
# coding: utf-8
"""
@File   : config.py
@Author : Steven.Shen
@Date   : 2021/10/22
@Desc   : config.yaml 配置对象数据结构模型
"""
import yaml


class Conf:
    privileges: str
    stationAll: list
    stationName: str
    stationNo: str
    logFolder: str
    logServer: str
    logServerUser: str
    logServerPwd: str
    fixFlag: bool
    fixComPort: str
    fixComBaudRate: int
    GPIBPort: int
    testcase: str
    failContinue: bool
    mesShopFloor: str
    mesServer: str
    rs_url: str
    continueFailLimit: int
    setTimeZone: str

    prompt: str
    dutIP: str
    dutComPort: str
    dutComBaudRate: int
    sshUser: str
    sshPwd: str
    dutModels: list
    dutSNRegex: dict
    dataAPI: dict
    snLen: int
    sdkVer: str
    testMode: str
    debugSkip: list

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
        self.LTT = Conf(dict_['LTT'])

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
    cf.station.stationAll.append('LTT9')
    save_config(cf, 'config.yaml')
