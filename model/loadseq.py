#!/usr/bin/env python
# coding: utf-8
"""
@File   : loadseq.py
@Author : Steven.Shen
@Date   : 2021/10/15
@Desc   : 
"""
import os
import sqlite3
import stat
import json
import sys
from inspect import currentframe

from openpyxl import load_workbook
import model.suite
import model.step
import model.sqlite
from .basicfunc import IsNullOrEmpty, get_sha256
import conf.globalvar as gv
import ui.mainform


def excel_convert_to_json(testcase_path_excel, all_stations):
    import conf.logprint as lg
    lg.logger.debug("Start convert excel testcase to json script,please wait a moment...")
    for station in all_stations:
        load_testcase_from_excel(testcase_path_excel, station, rf"{gv.scriptFolder}\{station}.json")
    lg.logger.debug("convert finish!")


def load_testcase_from_excel(testcase_path, sheet_name, test_script_path) -> list:
    """load test sequence form a sheet in Excel and return the suites sequences list,
    if success,serialize the suites list to json.
    :param testcase_path: the path of Excel
    :param sheet_name: the sheet test_name of Excel
    :param test_script_path:  serialize and save to json path
    :return : temp_suite[] list
    """
    workbook = None
    temp_suite = None
    suites_list = []
    item_header = []
    temp_suite_name = ""
    try:
        # lg.logger.debug('start load_testcase_from_excel...')
        workbook = load_workbook(testcase_path, read_only=True)
        worksheet = workbook[sheet_name]
        for i in list(worksheet.rows)[0]:  # 获取表头，第一行
            item_header.append(i.value)

        for i in range(1, worksheet.max_row):  # 一行行的读取excel
            line = list(worksheet.rows)[i]
            if IsNullOrEmpty(line[1].value):  # StepName为空停止解析
                break
            if not IsNullOrEmpty(line[0].value):  # 实例化test suite
                temp_suite_name = line[0].value
                temp_suite = model.suite.TestSuite(line[0].value, len(suites_list))
                suites_list.append(temp_suite)
            # 给step对象属性赋值
            test_step = model.step.Step()
            for header, cell in dict(zip(item_header, line)).items():
                test_step.index = temp_suite.totalNumber
                test_step.suiteIndex = temp_suite.index
                setattr(test_step, header, '' if IsNullOrEmpty(cell.value) else str(cell.value))
                # setattr(test_step, header, cell.value)
                test_step.SuiteName = temp_suite_name

            temp_suite.totalNumber += 1
            temp_suite.steps.append(test_step)
    except Exception as e:
        ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('ERROR!',
                                                                                     f'{currentframe().f_code.co_name}:{e} ',
                                                                                     5)
        sys.exit(e)
    else:
        serialize_to_json(suites_list, test_script_path)
        return suites_list
    finally:
        workbook.close()


def load_testcase_from_json(json_path, verify=False):
    """用json反序列化方式加载测试用例序列"""
    if verify:
        with model.sqlite.Sqlite(gv.database_setting) as db:
            db.execute(f"SELECT SHA256  from SHA256_ENCRYPTION WHERE NAME='{json_path}'")
            sha256 = db.cur.fetchone()[0]
            print(f"  dbSHA:{sha256}")
        JsonSHA = get_sha256(json_path)
        print(f"jsonSHA:{JsonSHA}")
        if sha256 == JsonSHA:
            return deserialize_from_json(json_path)
        else:
            ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('ERROR!',
                                                                                         f'{currentframe().f_code.co_name}:script {json_path} has been tampered!',
                                                                                         5)
            sys.exit(f'{currentframe().f_code.co_name}:script {json_path} has been tampered!')
    else:
        return deserialize_from_json(json_path)


def deserialize_from_json(json_path):
    try:
        """Deserialize form json.
        :param json_path: json file path.
        :return:object
        """
        with open(json_path, 'r') as rf:
            sequences_dict = json.load(rf)
        sequences_obj_list = []
        for suit_dict in sequences_dict:
            step_obj_list = []
            for step_dict in suit_dict['steps']:
                step_obj = model.step.Step(step_dict)
                step_obj_list.append(step_obj)
            suit_obj = model.suite.TestSuite(dict_=suit_dict)
            suit_obj.steps = step_obj_list
            sequences_obj_list.append(suit_obj)
        return sequences_obj_list
    except Exception as e:
        ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('Exception!',
                                                                                     f'{currentframe().f_code.co_name}:{e} ',
                                                                                     5)
        sys.exit(e)


def wrapper_save_sha256(fun):
    """get sha256 of json script in oder to verify MD5"""

    def inner(*args):
        fun(*args)
        sha256 = get_sha256(args[1])
        with model.sqlite.Sqlite(gv.database_setting) as db:
            try:
                db.execute(f"INSERT INTO SHA256_ENCRYPTION (NAME,SHA256) VALUES ('{args[1]}', '{sha256}')")
            except sqlite3.IntegrityError:
                db.execute(f"UPDATE SHA256_ENCRYPTION SET SHA256='{sha256}' WHERE NAME ='{args[1]}'")
        # os.chmod(args[1], stat.S_IREAD)

    return inner


@wrapper_save_sha256
def serialize_to_json(obj, json_path):
    """serialize obj to json and encrypt.
    :param obj: the object you want to serialize
    :param json_path: the path of json
    """
    try:
        import conf.logprint as lg
        lg.logger.debug(f"delete old json in scripts.")
        if os.path.exists(json_path):
            os.chmod(json_path, stat.S_IWRITE)
            os.remove(json_path)
        with open(json_path, 'w') as wf:
            json.dump(obj, wf, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        lg.logger.debug(f"serializeToJson success! {json_path}.")
    except Exception as e:
        ui.mainform.MainForm.main_form.my_signals.showMessageBox[str, str, int].emit('Exception!',
                                                                                     f'{currentframe().f_code.co_name}:{e} ',
                                                                                     5)
        sys.exit(e)
