#!/usr/bin/env python
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
import model.suite
import model.step
import conf.globalvar as gv
import conf.logconf as lg
import ui.mainform
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5 import QtCore
import model.sqlite
import sqlite3


def excel_convert_to_json(testcase_path_excel, all_stations):
    lg.logger.debug("Start convert excel testcase to json script.")
    for station in all_stations:
        test_script_json = rf"{gv.scriptFolder}\{station}.json"
        load_testcase_from_excel(testcase_path_excel, station, test_script_json)
    lg.logger.debug("convert finish!")


def load_testcase_from_excel(testcase_path_excel, sheetName, test_script_json) -> list:
    """load testcase form a sheet in excel and return the suites sequences list,
       if success,serialize the suites list to json.
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
        lg.logger.debug('start load_testcase_from_excel...')
        workbook = load_workbook(testcase_path_excel, read_only=True)
        worksheet = workbook[sheetName]

        for i in list(worksheet.rows)[0]:  # 获取表头，第一行
            itemHeader.append(i.value)
            if not hasattr(model.step.Step, i.value):  # 动态创建step类的属性
                setattr(model.step.Step, i.value, '')

        for i in range(1, worksheet.max_row):  # 一行行的读取excel
            line = list(worksheet.rows)[i]
            if model.IsNullOrEmpty(line[1].value):  # ItemName为空停止解析
                break
            if not model.IsNullOrEmpty(line[0].value):  # 实例化test suite
                temp_suite_name = line[0].value
                temp_suite = model.suite.TestSuite(line[0].value, len(suites_list))
                suites_list.append(temp_suite)

            test_step = model.step.Step()
            for header, cell in dict(zip(itemHeader, line)).items():  # 给step对象属性赋值
                test_step.index = temp_suite.totalNumber
                test_step.suite_index = temp_suite.index
                setattr(test_step, header, '' if model.IsNullOrEmpty(cell.value) else str(cell.value))
                test_step.suite_name = temp_suite_name

            temp_suite.totalNumber += 1
            temp_suite.steps.append(test_step)
    except Exception as e:
        lg.logger.critical(f"load testcase fail！{e}")
        sys.exit(e.__context__)
    else:
        serializeToJson(suites_list, test_script_json)
        return suites_list
    finally:
        workbook.close()


def load_testcase_from_json(testcase_path_json):
    with model.sqlite.Sqlite(gv.database_setting) as db:
        db.execute(f"SELECT SHA256  from SHA256_ENCRYPTION WHERE NAME='{testcase_path_json}'")
        sha256 = db.cur.fetchone()[0]
        lg.logger.debug(f"  dbSHA:{sha256}")
    JsonSHA = model.get_sha256(testcase_path_json)
    lg.logger.debug(f"jsonSHA:{JsonSHA}")
    if sha256 == JsonSHA:
        sequences_dict = json.load(open(testcase_path_json, 'r'))
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
    else:
        QMetaObject.invokeMethod(ui.mainform.main_form, 'showMessageBox', Qt.AutoConnection,
                                 QtCore.Q_RETURN_ARG(QMessageBox.StandardButton),
                                 QtCore.Q_ARG(str, 'ERROR!'),
                                 QtCore.Q_ARG(str, f'script {testcase_path_json} has been tampered!'),
                                 QtCore.Q_ARG(int, 5))
        lg.logger.critical(f"ERROR,json testCase file {testcase_path_json} has been tampered!")
        sys.exit(0)


def serializeToJson(obj, testcase_path_json):
    """serialize obj to json and encrypt.
    :param obj: the object you want to serialize
    :param testcase_path_json: the path of json
    """
    lg.logger.debug(f"delete old json in scripts.")
    if os.path.exists(testcase_path_json):
        os.chmod(testcase_path_json, stat.S_IWRITE)
        os.remove(testcase_path_json)
    json.dump(obj, open(testcase_path_json, 'w'), default=lambda o: o.__dict__, sort_keys=True, indent=4)
    lg.logger.info(f"serializeToJson success! {testcase_path_json}.")
    sha256 = model.get_sha256(testcase_path_json)
    with model.sqlite.Sqlite(gv.database_setting) as db:
        try:
            db.execute(f"INSERT INTO SHA256_ENCRYPTION (NAME,SHA256) VALUES ('{testcase_path_json}', '{sha256}')")
        except sqlite3.IntegrityError:
            db.execute(f"UPDATE SHA256_ENCRYPTION SET SHA256='{sha256}' WHERE NAME ='{testcase_path_json}'")
    os.chmod(testcase_path_json, stat.S_IREAD)
