#!/usr/c/env python
# coding: utf-8
"""
@File   : loadseq.py
@Author : Steven.Shen
@Date   : 2021/10/15
@Desc   : 
"""
import os
import stat
import json
import sys
from openpyxl import load_workbook
from model.basefunc import IsNullOrEmpty, binary_read, get_sha256, binary_write
from .suite import TestSuite
from .step import Step
from conf.globalconf import logger
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)


def serializeToJson(obj, testcase_path_json, key_path):
    """serialize obj to json and encrypt.
    :param obj: the object you want to serialize
    :param testcase_path_json: the path of json
    :param key_path: txt file path that save json SHA256 for encrypt.
    """
    try:
        logger.debug(f"delete old json in script.")
        if os.path.exists(testcase_path_json):
            os.chmod(testcase_path_json, stat.S_IWRITE)
            os.remove(testcase_path_json)
        if os.path.exists(key_path):
            os.chmod(key_path, stat.S_IWRITE)
            os.remove(key_path)
        json.dump(obj, open(testcase_path_json, 'w'), default=lambda o: o.__dict__, sort_keys=True, indent=4)
        srcBytes = get_sha256(testcase_path_json).encode()
        # 产生密钥， 密钥是加密解密必须的
        token = f.encrypt(srcBytes)
        binary_write(key_path, token.decode())
        os.chmod(testcase_path_json, stat.S_IREAD)
        os.chmod(key_path, stat.S_IREAD)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)


def load_testcase_from_excel(testcase_path_excel, sheetName, testcase_path_json, key_path) -> list:
    """load testcase form a sheet in excel and return the suites sequences list,
       if success,serialize the suites list to json.
    :param key_path: save json SHA256 key for decrypt
    :param testcase_path_excel: the path of excel
    :param sheetName: the sheet test_name of excel
    :param testcase_path_json:  serialize and save to json path
    :return : temp_suite[] list
    """
    workbook = None
    temp_suite = None
    suites_list = []
    itemHeader = []
    temp_suite_name = ""
    try:
        workbook = load_workbook(testcase_path_excel, read_only=True)
        worksheet = workbook[sheetName]

        for i in list(worksheet.rows)[0]:  # 获取表头，第一行
            itemHeader.append(i.value)
            if not hasattr(Step, i.value):  # 动态创建Item类的属性
                setattr(Step, i.value, '')

        for i in range(1, worksheet.max_row):  # 一行行的读取excel
            line = list(worksheet.rows)[i]
            if IsNullOrEmpty(line[1].value):  # ItemName为空停止解析
                break
            if not IsNullOrEmpty(line[0].value):  # 新的seqItem
                temp_suite_name = line[0].value
                temp_suite = TestSuite(line[0].value, len(suites_list))
                suites_list.append(temp_suite)

            test_step = Step()
            for header, cell in dict(zip(itemHeader, line)).items():  # 给step对象属性赋值
                test_step.index = temp_suite.totalNumber
                setattr(test_step, header, '' if IsNullOrEmpty(cell.value) else str(cell.value))
                test_step.suite_name = temp_suite_name

            temp_suite.totalNumber = temp_suite.totalNumber + 1
            temp_suite.test_steps.append(test_step)
    except Exception as e:
        logger.exception(f"load testcase fail！{e}")
        sys.exit(1)
    else:
        json.dump(suites_list, open(f'scripts/{sheetName}.json', 'w'),
                  default=lambda o: o.__dict__,
                  sort_keys=True,
                  indent=4)
        serializeToJson(suites_list, testcase_path_json, key_path)
        return suites_list
    finally:
        workbook.close()


def load_testcase_from_json(shaPath, testcase_path_json):
    try:
        sha = f.decrypt(binary_read(shaPath).encode())
        logger.debug(f" txtSHA:{sha}")
        JsonSHA = get_sha256(testcase_path_json)
        logger.debug(f"jsonSHA:{JsonSHA}")
        if sha == JsonSHA:
            return json.load(open(testcase_path_json, 'r'))
        else:
            raise Exception(f"ERROR,json testCase file {testcase_path_json} has been tampered!")
    except Exception as e:
        logger.exception(e)
        sys.exit(1)

# def load_testcase_from_excel1(self, temp_suite=None, workbook=None):
#     suites_list = []
#     itemHeader = []
#     temp_suite_name = ""
#     try:
#         workbook = load_workbook(self.testcase_path_excel, read_only=True)
#         worksheet = workbook[self.sheetName]
#
#         for i in list(worksheet.rows)[0]:  # 获取表头，第一行
#             itemHeader.append(i.test_value)
#             if not hasattr(Step, i.test_value):  # 动态创建Item类的属性
#                 setattr(Step, i.test_value, '')
#         for i in range(1, worksheet.max_row):  # 一行行的读取excel
#             line = list(worksheet.rows)[i]
#             if IsNullOrEmpty(line[1].test_value):  # ItemName为空停止解析
#                 break
#             if not IsNullOrEmpty(line[0].test_value):  # 新的seqItem
#                 temp_suite_name = line[0].test_value
#                 temp_suite = TestSuite(line[0].test_value, len(suites_list))
#                 suites_list.append(temp_suite)
#
#             test_step = Step()
#             for header, cell in dict_(zip(itemHeader, line)).items():  # 给step对象属性赋值
#                 test_step.index = temp_suite.totalNumber
#                 setattr(test_step, header, '' if IsNullOrEmpty(cell.test_value) else str(cell.test_value))
#                 test_step.suite_name = temp_suite_name
#             temp_suite.totalNumber = temp_suite.totalNumber + 1
#             temp_suite.test_steps.append(test_step)
#     except Exception as e:
#         logger.exception(f"load testcase fail！！{e}")
#         sys.exit(1)
#     else:
#         json.dump(suites_list, open(fr'F:\pyside2\scripts\{self.sheetName}.json', 'w'),
#                   default=lambda o: o.__dict__,
#                   sort_keys=True,
#                   indent=4)
#         json_str = json.dumps(suites_list, default=lambda o: o.__dict__, indent=4)
#         data_yaml = yaml.safe_load(json_str)  # 将字符转yaml
#
#         logger.info("load testcase success!")
#         # yaml.safe_dump(suites_list, open(fr'F:\pyside2\scripts\{self.sheetName}.yaml', 'w'),
#         #                default=lambda o: o.__dict__,
#         #                sort_keys=True,
#         #                indent=4)
#         # print([suites_list])
#         with open(fr'F:\pyside2\scripts\{self.sheetName}.yaml', mode='w', encoding='utf-8') as f:
#             yaml.safe_dump(data_yaml, stream=f, allow_unicode=True, sort_keys=False, indent=4)
#         return suites_list
#     finally:
#         workbook.close()
