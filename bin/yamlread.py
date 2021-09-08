#!/usr/bin/env python
# coding: utf-8
"""
@File   : yamlread.py
@Author : Steven.Shen
@Date   : 2021/9/7
@Desc   : 
"""
import json
import logging.config
from string import Template

import yaml


class YamlConfig:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file

    def write_config(self, date):
        with open(self.yaml_file, mode='w', encoding='utf-8') as f:
            yaml.safe_dump(date, stream=f, allow_unicode=True, sort_keys=False, indent=4)

    def read_yaml(self):
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            return yaml_data

    def upgrade_yaml(self, value, *args):
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            if len(args) == 1:
                yaml_data[args[0]] = value
            elif len(args) == 2:
                yaml_data[args[0]][args[1]] = value
            elif len(args) == 3:
                yaml_data[f'{args[0]}'][f'{args[1]}'][f'{args[2]}'] = value
            elif len(args) == 4:
                print('4')
                yaml_data[args[0]][args[1]][args[2]][args[4]] = value
            elif len(args) == 5:
                yaml_data[args[0]][args[1]][args[2]][args[4]][args[5]] = value
            else:
                raise Exception('args out of suite_no!')
        with open(self.yaml_file, mode='w', encoding='utf-8') as f:
            yaml.safe_dump(yaml_data, stream=f, allow_unicode=True, sort_keys=False, indent=4)


if __name__ == '__main__':
    obj = YamlConfig('logging.yaml')
    config = obj.read_yaml()
    res = Template(json.dumps(config)).safe_substitute(
        {'log_file': r'F:/pyside2/log/log_file.txt',
         'critical_log': 'F:/pyside2/log/critical_log.txt',
         'errors_log': 'F:/pyside2/log/errors_log.txt'})
    logging.config.dictConfig(yaml.safe_load(res))
    logger = logging.getLogger('testlog')
    logger.error('sdsdsdsdsds')

    YamlConfig('config.yaml').upgrade_yaml(True, 'station', 'debug')

    ss = YamlConfig('config.yaml').read_yaml()['dut']['dut_mode']
    print(ss)
