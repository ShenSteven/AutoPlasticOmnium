#!/usr/cf/env python
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
from PySide2.QtWidgets import QMessageBox
from openpyxl import load_workbook
import model.suite
import model.step
import conf.globalvar as gv
import conf.logconf as lg


# from cryptography.fernet import Fernet
# key = Fernet.generate_key()
# fernet = Fernet(key)
def thread_excel_convert_to_json(self):
    if not os.path.exists(gv.test_script_json) and not os.path.exists(gv.SHA256Path):
        model.loadseq.excel_convert_to_json(rf"{gv.above_current_path}\scripts\{gv.cf.station.testcase}",
                                            gv.cf.station.station_all)


def excel_convert_to_json(testcase_path_excel, all_stations):
    for station in all_stations:
        test_script_json = f"{gv.scriptFolder}{station}.json"
        SHA256Path = f"{gv.scriptFolder}{station}_key.txt"
        load_testcase_from_excel(testcase_path_excel, station, test_script_json, SHA256Path)


def load_testcase_from_excel(testcase_path_excel, sheetName, test_script_json, key_path) -> list:
    """load testcase form a sheet in excel and return the suites sequences list,
       if success,serialize the suites list to json.
    :param key_path: save json SHA256 key for decrypt
    :param testcase_path_excel: the path of excel
    :param sheetName: the sheet test_name of excel
    :param test_script_json:  serialize and save to json path
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
            if not hasattr(model.step.Step, i.value):  # 动态创建Item类的属性
                setattr(model.step.Step, i.value, '')

        for i in range(1, worksheet.max_row):  # 一行行的读取excel
            line = list(worksheet.rows)[i]
            if model.IsNullOrEmpty(line[1].value):  # ItemName为空停止解析
                break
            if not model.IsNullOrEmpty(line[0].value):  # 新的seqItem
                temp_suite_name = line[0].value
                temp_suite = model.suite.TestSuite(line[0].value, len(suites_list))
                suites_list.append(temp_suite)

            test_step = model.step.Step()
            for header, cell in dict(zip(itemHeader, line)).items():  # 给step对象属性赋值
                test_step.index = temp_suite.totalNumber
                setattr(test_step, header, '' if model.IsNullOrEmpty(cell.value) else str(cell.value))
                test_step.suite_name = temp_suite_name

            temp_suite.totalNumber = temp_suite.totalNumber + 1
            temp_suite.test_steps.append(test_step)
    except Exception as e:
        lg.logger.critical(f"load testcase fail！{e}")
        sys.exit(e.__context__)
    else:
        serializeToJson(suites_list, test_script_json, key_path)
        return suites_list
    finally:
        workbook.close()


def load_testcase_from_json(shaPath, testcase_path_json):
    sha = model.binary_read(shaPath)
    lg.logger.debug(f" txtSHA:{sha}")
    JsonSHA = model.get_sha256(testcase_path_json)
    lg.logger.debug(f"jsonSHA:{JsonSHA}")
    if sha == JsonSHA:
        sequences_dict = json.load(open(testcase_path_json, 'r'))
        sequences_obj_list = []
        for suit_dict in sequences_dict:
            step_obj_list = []
            for step_dict in suit_dict['test_steps']:
                step_obj = model.step.Step(step_dict)
                step_obj_list.append(step_obj)
            suit_obj = model.suite.TestSuite(dict_=suit_dict)
            suit_obj.test_steps = step_obj_list
            sequences_obj_list.append(suit_obj)
        return sequences_obj_list
    else:
        # QMessageBox.critical(gv.main_form.ui, 'ERROR!', f'json testCase file {testcase_path_json} has been tampered!',
        #                      QMessageBox.Ok)
        lg.logger.critical(f"ERROR,json testCase file {testcase_path_json} has been tampered!")


def serializeToJson(obj, testcase_path_json, key_path):
    """serialize obj to json and encrypt.
    :param obj: the object you want to serialize
    :param testcase_path_json: the path of json
    :param key_path: txt file path that save json SHA256 for encrypt.
    """
    lg.logger.debug(f"delete old json in script.")
    if os.path.exists(testcase_path_json):
        os.chmod(testcase_path_json, stat.S_IWRITE)
        os.remove(testcase_path_json)
    if os.path.exists(key_path):
        os.chmod(key_path, stat.S_IWRITE)
        os.remove(key_path)
    json.dump(obj, open(testcase_path_json, 'w'), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    lg.logger.info(f"serializeToJson success.")
    srcBytes = model.get_sha256(testcase_path_json)
    # 产生密钥， 密钥是加密解密必须的
    # token = gv.token.encrypt(srcBytes)
    model.binary_write(key_path, srcBytes)
    os.chmod(testcase_path_json, stat.S_IREAD)
    os.chmod(key_path, stat.S_IREAD)