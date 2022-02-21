#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
import os
import csv
import sys
import json
import time
import requests
import ui.mainform
import conf.logconf as lg
import conf.globalvar as gv
from PyQt5.QtWidgets import QApplication, QMessageBox
import model.basefunc
from threading import Thread
from traceback import format_exception


def upload_Json_to_client():
    pass
    return True


def CollectResultToCsv():
    def thread_update():
        gv.CSVFilePath = fr'{gv.cf.station.log_folder}\CsvData\{time.strftime("%Y-%m-%d--%H")}-00-00_{gv.cf.station.station_no}.csv'
        csvColumnPath = fr'{gv.scriptFolder}\csv_column.txt'
        fix_header = ["DEVICE_TYPE", "STATION_TYPE", "FACILITY_ID", "LINE_ID", "FIXTURE_ID", "DUT_POSITION", "SN",
                      "FW_VERSION", "HW_REVISION", "SW_VERSION", "START_TIME", "TEST_DURATION", "DUT_TEST_RESULT",
                      "FIRST_FAIL", "ERROR_CODE", "TIME_ZONE", "TEST_DEBUG", "JSON_UPLOAD", "MES_UPLOAD"]
        fix_header.extend(gv.csv_list_header)
        updateColumn = gv.finalTestResult and not gv.IsDebug
        model.basefunc.create_csv_file(gv.CSVFilePath, fix_header, updateColumn)
        if os.path.exists(csvColumnPath):
            os.remove(csvColumnPath)
        with open(csvColumnPath, 'w') as f:
            header = '\t'.join(fix_header)
            f.write(header)
        fix_header_value = [gv.dut_model, gv.cf.station.station_name, "Luxshare", gv.WorkOrder,
                            gv.cf.station.station_no,
                            "1", gv.SN, gv.cf.dut.qsdk_ver, gv.mesPhases.HW_REVISION, gv.test_software_ver,
                            time.strftime("%Y/%m/%d %H:%M:%S"), str(ui.mainform.main_form.sec), gv.finalTestResult,
                            gv.mesPhases.first_fail, gv.error_details_first_fail, "UTC", gv.cf.dut.test_mode,
                            gv.mesPhases.JSON_UPLOAD, gv.mesPhases.MES_UPLOAD]
        fix_header_value.extend(gv.csv_list_result)
        model.basefunc.write_csv_file(gv.CSVFilePath, fix_header_value)

    thread = Thread(target=thread_update)
    thread.start()


def saveTestResult():
    def thread_update():
        reportPath = fr'{gv.OutPutPath}\result.csv'
        model.basefunc.create_csv_file(reportPath, gv.tableWidgetHeader)
        if os.path.exists(reportPath):
            all_rows = []
            for row in range(ui.mainform.main_form.ui.tableWidget.rowCount()):
                row_data = []
                for column in range(ui.mainform.main_form.ui.tableWidget.columnCount()):
                    item = ui.mainform.main_form.ui.tableWidget.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                all_rows.append(row_data)

            with open(reportPath, 'a', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerows(all_rows)
        lg.logger.debug(f'saveTestResult to:{reportPath}')

    thread = Thread(target=thread_update)
    thread.start()


def test_thread():
    try:
        while True:
            if gv.startFlag:
                if gv.IsCycle:
                    while gv.IsCycle:
                        if ui.mainform.main_form.testcase.run(gv.cf.station.fail_continue):
                            gv.PassNumOfCycleTest += 1
                        else:
                            gv.FailNumOfCycleTest += 1
                elif gv.SingleStepTest:
                    lg.logger.debug(f'Suite:{gv.SuiteNo},Step:{gv.StepNo}')
                    result = ui.mainform.main_form.testcase.clone_suites[gv.SuiteNo].steps[gv.StepNo].run(
                        ui.mainform.main_form.testcase.clone_suites[gv.SuiteNo])
                    gv.finalTestResult = result
                    ui.mainform.main_form.SetTestStatus(
                        ui.mainform.TestStatus.PASS if gv.finalTestResult else ui.mainform.TestStatus.FAIL)
                else:
                    result = ui.mainform.main_form.testcase.run(gv.cf.station.fail_continue)
                    result1 = upload_Json_to_client()
                    result2 = upload_result_to_mes(gv.mes_result)
                    gv.finalTestResult = result & result1 & result2
                    ui.mainform.main_form.SetTestStatus(
                        ui.mainform.TestStatus.PASS if gv.finalTestResult else ui.mainform.TestStatus.FAIL)
                    CollectResultToCsv()
                    saveTestResult()
    except Exception as e:
        lg.logger.exception(f"TestThread() Exception:{e}")
        ui.mainform.main_form.SetTestStatus(ui.mainform.TestStatus.ABORT)
    finally:
        lg.logger.debug('finally')


def upload_result_to_mes(url):
    if gv.IsDebug:
        return True
    mes_result = json.dumps(gv.mesPhases, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    lg.logger.debug(mes_result)
    response = requests.post(url, mes_result)
    if response.status_code == 200:
        return True
    else:
        lg.logger.debug(f'post fail:{response.content}')
        return False


def excepthook(cls, exception, traceback):
    lg.logger.exception(format_exception(cls, exception, traceback))
    QMessageBox.critical(None, "Error", "".join(format_exception(cls, exception, traceback)))


added_files = [
    ('ui/main.ui', 'ui'),
    ('ui/images.qrc', 'ui'),
    ('ui/images', 'ui'),
    ('conf/*.yaml', 'conf'),
    ('set.py', '.'),
    ('scripts', 'scripts')
]
# pyinstaller -y --clean --noconsole --debug=all  --distpath=./dist/ -n AutoTestSystem --icon="test.ico" --add-data="ui/main.ui;ui" --add-data="ui/images.qrc;ui" --add-data="ui/images;ui" --add-data="conf/*.yaml;conf" --add-data="scripts;scripts" main.py --runtime-hook="runtimehook.py"
# pyinstaller AutoTestSystem.spec
if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication([])
    print("applicationDirPath:", app.applicationDirPath())
    mainWin = ui.mainform.MainForm()
    mainWin.ui.show()
    try:
        app.exec_()
    except KeyboardInterrupt:
        pass
