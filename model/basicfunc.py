#!/usr/bin/env python
# coding: utf-8
"""
@File   : basic func.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import json
import os
import csv
from datetime import datetime
import yaml
import conf.logprint as lg
import hashlib


def save_config(yaml_file, obj):
    with open(yaml_file, mode='r+', encoding='utf-8') as f:
        readall = f.read()
        try:
            js = json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=4)
            ya = yaml.safe_load(js)
            f.seek(0)
            yaml.safe_dump(ya, stream=f, default_flow_style=False, sort_keys=False, indent=4)
        except Exception as e:
            lg.logger.fatal(f"save_config! {e}")
            f.seek(0)
            f.write(readall)
        else:
            pass
            lg.logger.info(f"save conf.yaml success!")


def wrapper(flag):
    def wrapper_inner(func):
        def inners(**kwargs):
            start = None
            if flag:
                start = datetime.now()
            ret = func(**kwargs)
            if flag:
                lg.logger.debug(f'elapsed time:{datetime.now() - start}')
            return ret

        return inners

    return wrapper_inner


def wrapper_time(fun):
    def inner(*args):
        start = datetime.now()
        fun(*args)
        lg.logger.debug(f'elapsed time:{datetime.now() - start}')

    return inner


def create_csv_file(filename, header, updateColumn=False):
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                file = csv.writer(f)
                file.writerow(header)
            lg.logger.debug(f'create_csv_file:{filename}')
        else:
            if updateColumn:
                with open(filename, 'r') as rf:
                    reader = csv.reader(rf)
                    # cl = [row[1] for row in reader]  # 获取第1列
                    rows = [row for row in reader]
                    with open(filename, 'w', newline='') as wf:
                        if [0] != header:
                            rows[0] = header
                            file = csv.writer(wf)
                            file.writerows(rows)
                        lg.logger.info(f'update csvHeader success!')
    except Exception as e:
        lg.logger.fatal(e)


def write_csv_file(filename, row):
    try:
        with open(filename, 'a', newline='') as f:
            file = csv.writer(f)
            file.writerow(row)
    except Exception as e:
        lg.logger.fatal(e)


def IsNullOrEmpty(strObj: str):
    if strObj and len(str(strObj)) > 0:
        return False
    else:
        return True


def binary_read(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
        return content.decode(encoding='UTF-8')


def binary_write(filepath, content):
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf8'))


def get_sha256(filepath) -> str:
    with open(filepath, 'rb') as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        return sha256obj.hexdigest()


if __name__ == '__main__':
    pass
    # create_csv_file('test.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
    # write_csv_file('test.csv', ['1wqw', '2', '3', '4'])
    # print(str(True))
    # ping('192.168.1.101')
    # ping('127.0.0.1')
    # aa = restart_process('EXCEL.EXE')
    # logger.debug(f"ds{aa}")
    # register("demon", "1@1.com")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {})
    # register("demon", "1@1.com",
    #          addr="shanghai")  # test_name:%s, age:%s, others:%s ('demon', '1@1.com', {'addr': 'shanghai'})
