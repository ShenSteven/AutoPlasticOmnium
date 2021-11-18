#!/usr/cf/env python
# coding: utf-8
"""
@File   : __init__.py.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
import conf.config
import yaml


def read_config(yaml_file, objType) -> conf.config.Configs:
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        obj = objType(yaml_data)
        return obj


def read_yaml(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        return yaml_data
