#!/usr/bin/env python
# coding: utf-8
"""
@File   : src.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""
import os
import time
import json
import csv
import requests
from threading import Thread
import ui.mainform as mf
import conf.logprint as lg
import conf.globalvar as gv
from model.basicfunc import write_csv_file, create_csv_file


def check_connection(url):
    return True
    # will return "Connected" if the server is running
    try:
        url = url + "ping"
        lg.logger.debug(url)
        response = requests.get(url)
        lg.logger.debug(response.status_code)
        lg.logger.debug(response.text)
        if "Connected" in response.text:
            return True
        else:
            lg.logger.debug("Cannot connect to server")
            return False
    except Exception as a:
        lg.logger.debug(a)
        return False


def upload_Json_to_client(url, log_path):
    return True
    """上传json内容和测试log到客户服务器"""
    json_upload_path = os.path.join(gv.logFolderPath, 'Json', f'{gv.SN}_{time.strftime("%H%M%S")}.json')
    gv.jsonOfResult = json_upload_path
    jsonStr = json.dumps(gv.stationObj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    with open(json_upload_path, 'w') as fw:
        fw.write(jsonStr)
    lg.logger.debug(jsonStr)

    if not check_connection(url):
        return False
    # read_json = open(json_upload_path, "r").read()
    read_json = jsonStr
    read_log = open(log_path, "rb").read()
    lg.logger.debug("%s post:" % json_upload_path)
    lg.logger.debug("%s post:" % log_path)
    if args.station[0] == "MBFT":
        litepoint = open("./Data/litepoint.zip", "rb").read()
        response = requests.post(url, data=read_json,
                                 files={"serial_log.txt": read_log, "mbft_litepoint.zip": litepoint})
    elif args.station[0] == "SRF":
        litepoint = open("./Data/litepoint.zip", "rb").read()
        response = requests.post(url, data=read_json,
                                 files={"serial_log.txt": read_log, "srf_litepoint.zip": litepoint})
    elif args.station[0] == "REPAIR":
        response = requests.post(url, data=read_json)
    else:
        response = requests.post(read_json, files={"serial_log.txt": read_log})
    lg.logger.debug("Result:%s" % response.status_code)
    lg.logger.debug(response.text)
    if response.status_code == 200:
        return True
    else:
        return False


def CollectResultToCsv():
    def thread_update():
        gv.CSVFilePath = fr'{gv.cf.station.log_folder}\CsvData\{time.strftime("%Y-%m-%d--%H")}-00-00_{gv.cf.station.station_no}.csv'
        csvColumnPath = fr'{gv.scriptFolder}\csv_column.txt'
        fix_header = ["DEVICE_TYPE", "STATION_TYPE", "FACILITY_ID", "LINE_ID", "FIXTURE_ID", "DUT_POSITION", "SN",
                      "FW_VERSION", "HW_REVISION", "SW_VERSION", "START_TIME", "TEST_DURATION", "DUT_TEST_RESULT",
                      "FIRST_FAIL", "ERROR_CODE", "TIME_ZONE", "TEST_DEBUG", "JSON_UPLOAD", "MES_UPLOAD"]
        fix_header.extend(gv.csv_list_header)
        updateColumn = gv.finalTestResult and not gv.IsDebug
        create_csv_file(gv.CSVFilePath, fix_header, updateColumn)
        if os.path.exists(csvColumnPath):
            os.remove(csvColumnPath)
        with open(csvColumnPath, 'w') as f:
            header = '\t'.join(fix_header)
            f.write(header)
        fix_header_value = [gv.dut_model, gv.cf.station.station_name, "Luxxxxx", gv.WorkOrder,
                            gv.cf.station.station_no,
                            "1", gv.SN, gv.cf.dut.qsdk_ver, gv.mesPhases.HW_REVISION, gv.version,
                            time.strftime("%Y/%m/%d %H:%M:%S"), str(mf.MainForm.main_form.sec),
                            gv.finalTestResult,
                            gv.mesPhases.first_fail, gv.error_details_first_fail, "UTC", gv.cf.dut.test_mode,
                            gv.mesPhases.JSON_UPLOAD, gv.mesPhases.MES_UPLOAD]
        fix_header_value.extend(gv.csv_list_result)
        lg.logger.debug(f'CollectResultToCsv {gv.CSVFilePath}')
        write_csv_file(gv.CSVFilePath, fix_header_value)

    thread = Thread(target=thread_update)
    thread.start()


def saveTestResult():
    def thread_update():
        reportPath = fr'{gv.OutPutPath}\result.csv'
        create_csv_file(reportPath, gv.tableWidgetHeader)
        if os.path.exists(reportPath):
            all_rows = []
            for row in range(mf.MainForm.main_form.ui.tableWidget.rowCount()):
                row_data = []
                for column in range(mf.MainForm.main_form.ui.tableWidget.columnCount()):
                    item = mf.MainForm.main_form.ui.tableWidget.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                all_rows.append(row_data)

            with open(reportPath, 'a', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerows(all_rows)
        lg.logger.debug(f'saveTestResult to:{reportPath}')

    thread = Thread(target=thread_update)
    thread.start()


def upload_result_to_mes(url):
    return True
    if gv.IsDebug:
        return True
    mes_result = json.dumps(gv.mesPhases, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    lg.logger.debug(f'mes info:{mes_result}')
    response = requests.post(url, mes_result)
    if response.status_code == 200:
        return True
    else:
        lg.logger.debug(f'post fail:{response.content}')
        return False


if __name__ == "__main__":
    pass
    # main()
