#!/usr/bin/env python
# coding: utf-8
"""
@File   : test step.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
import traceback
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QAction
import model.product
import model.sqlite
import model.keyword
from .basicfunc import IsNullOrEmpty
import conf.globalvar as gv
import ui.mainform as mf


class Step:
    """测试步骤类
    Attributes:
        suiteIndex: 测试套序列号
        index: 当前测试step序列号
        # stepResult: 测试项测试结果
        start_time: 测试项的开始时
        finish_time: 测试结束时间
        start_time_json = None
        error_code = '': 错误码
        error_details = ''：错误码详细描述
        status = 'exception'  # pass,fail,exception
        testValue = None: 测试得到的值
        elapsedTime = 0: 测试步骤耗时
        _isTest：bool 决定步骤是否测试，默认都测试
        _command：test command after parse variant.
        ### excel header variant ###
        SuiteName: str = ''：测试套名字
        StepName: str = None: 当前测试step名字
        ErrorCode: str = None: 测试错误码
        Retry: int = None: 测试失败retry次数
        Timeout: int = None: 测试步骤超时时间
        SubStr1: str = None: 截取字符串 如截取abc中的b SubStr1=a，SubStr2=cf
        SubStr2: str = None
        IfElse: str = None: 测试步骤结果是否做为if条件，决定else步骤是否执行
        For: str = None: 循环测试for(6)开始6次循环，END FOR结束
        Model: str = None: 机种，根据机种决定哪些用例不跑，哪些用例需要跑
        CmdOrParam: str = None: 发送的测试命令
        ExpectStr: str = None: 期待的提示符，用来判断反馈是不是结束了
        CheckStr1: str = None: 检查反馈是否包含CheckStr1
        CheckStr2: str = None: 检查反馈是否包含CheckStr2
        SPEC: str = None: 测试定义的Spec
        LSL: str = None: 最小限值
        USL: str = None: 最大限值
        ErrorDetails: str = None: 测试错误码详细描述
        Unit: str = None: 测试值单位
        MesVar: str = None: 上传MES信息的变量名字
        ByPF: str = None: 手动人为控制测试结果 1=pass，0||空=fail
        FTC: str = None: 失败继续 fail to continue。1=继续，0||空=不继续
        Keyword: str = None: 测试步骤对应的关键字，执行对应关键字下的代码段
        Json: str = None: 测试结果是否生成Json数据上传给客户
        EeroName: str = None: 客户定义的测试步骤名字
        param1: str = None
    """

    def __init__(self, dict_=None):
        self.wind = None
        self.logger = None
        self.breakpoint: bool = False
        self.suiteIndex: int = 0
        self.index: int = 0
        self.testValue = None
        self.start_time = None
        self.finish_time = None
        self.start_time_json = None
        self.error_code = ''
        self.error_details = ''
        self.status: str = 'exception'  # pass/fail/exception
        self.elapsedTime = 0
        self._isTest = True
        self.suiteVar = ''
        # Excel Column
        self.SuiteName: str = ''
        self.StepName: str = ''
        self.EeroName: str = ''
        self.Keyword: str = ''
        self.ErrorCode: str = ''
        self.ErrorDetails: str = ''
        self.Retry: int = 0
        self.Timeout: int = 0
        self.IfElse: str = ''
        self.For: str = ''
        self.SubStr1: str = ''
        self.SubStr2: str = ''
        self.Model: str = ''
        self.CmdOrParam: str = ''
        self.ExpectStr: str = ''
        self.CheckStr1: str = ''
        self.CheckStr2: str = ''
        self.NoContain: str = ''
        self.SPEC: str = ''
        self.LSL: str = ''
        self.USL: str = ''
        self.Unit: str = ''
        self.MesVar: str = ''
        self.ByPF: str = ''
        self.FTC: str = ''
        self.Json: str = ''
        self.SetGlobalVar: str = ''
        self.param1: str = ''
        self.TearDown: str = ''
        # PLIN
        self.ID: str = ''
        self.NAD: str = ''
        self.PCI_LEN: str = ''

        if dict_ is not None:
            self.__dict__.update(dict_)

    @property
    def isTest(self):
        if mf.MainForm.main_form is not None:
            if str(self.IfElse).lower() == 'else':
                self._isTest = not mf.MainForm.main_form.testcase.IfCond
            if not IsNullOrEmpty(self.Model) and mf.MainForm.main_form.dut_model.lower() not in self.Model.lower():
                self._isTest = False
            if mf.MainForm.main_form.SingleStepTest:
                self._isTest = True
            return self._isTest
        else:
            if str(self.IfElse).lower() == 'else':
                self._isTest = not self.wind.testcase.IfCond
            if not IsNullOrEmpty(self.Model) and self.wind.dut_model.lower() not in self.Model.lower():
                self._isTest = False
            if self.wind.SingleStepTest:
                self._isTest = True
            return self._isTest

    @isTest.setter
    def isTest(self, value):
        self._isTest = value

    @property
    def command(self):
        return self.parse_var(self.CmdOrParam)

    @property
    def spec(self):
        return self.parse_var(self.SPEC)

    @property
    def _NAD(self):
        return self.parse_var(self.NAD)

    @property
    def _PCI_LEN(self):
        return self.parse_var(self.PCI_LEN)

    # @staticmethod
    def parse_var(self, value):
        """当CmdOrParam中有变量时，把命令中的<>字符替换成对应的变量值"""
        if mf.MainForm.main_form.TestVariables is None and self.wind.TestVariables:
            return value
        for a in re.findall(r'<(.*?)>', value):
            if mf.MainForm.main_form.TestVariables is not None:
                varVal = getattr(mf.MainForm.main_form.TestVariables, a)
            else:
                varVal = getattr(self.wind.TestVariables, a)
            if varVal is None:
                raise Exception(f'Variable:{a} not found in globalVal!!')
            else:
                value = re.compile(f'<{a}>').sub(varVal, value, count=1)

        if value == 'quit' or value == '0x03':
            value = chr(0x03).encode('utf8')
        return value

    def set_json_start_time(self, test_case):
        if IsNullOrEmpty(self.Json):
            if not test_case.startTimeJsonFlag:
                return
            test_case.startTimeJson = datetime.now()
            test_case.startTimeJsonFlag = False
        else:
            if test_case.startTimeJsonFlag:
                self.start_time_json = datetime.now()
            else:
                self.start_time_json = test_case.startTimeJson
                test_case.startTimeJsonFlag = True

    def setColor(self, color: QBrush):
        """set treeWidget item color"""
        if mf.MainForm.main_form is not None:
            mf.MainForm.main_form.my_signals.treeWidgetColor.emit(color, self.suiteIndex, self.index, False)

    def run(self, test_case, testSuite, suiteItem: model.product.SuiteItem = None):
        """run test step"""
        self.wind = test_case.myWind
        if self.logger is None:
            self.logger = testSuite.logger
        self.SuiteName = testSuite.SuiteName
        self.suiteIndex = testSuite.index
        self.suiteVar = testSuite.suiteVar
        if IsNullOrEmpty(self.EeroName):
            self.EeroName = self.StepName
        info = ''
        test_result = False
        self.set_json_start_time(test_case)
        self.start_time = datetime.now()

        try:
            if self.isTest:
                self.setColor(Qt.yellow)
                self.logger.debug(f"<a name='testStep:{self.SuiteName}-{self.StepName}'>Start:{self.StepName},"
                                  f"Keyword:{self.Keyword},Retry:{self.Retry},Timeout:{self.Timeout}s,"
                                  f"SubStr:{self.SubStr1}*{self.SubStr2},MesVer:{self.MesVar},FTC:{self.FTC}</a>")
                self.init_online_limit()
            else:
                if not gv.IsCycle:
                    self.setColor(Qt.gray)
                test_result = True
                self.status = str(test_result)
                return True

            if self.breakpoint or gv.pauseFlag:
                gv.pauseFlag = True
                if mf.MainForm.main_form is not None:
                    mf.MainForm.main_form.my_signals.setIconSignal[QAction, QIcon].emit(
                        mf.MainForm.main_form.ui.actionStart, QIcon(':/images/Start-icon.png'))
                gv.pause_event.clear()
            else:
                gv.pause_event.set()

            for retry in range(self.Retry, -1, -1):
                if gv.pause_event.wait():
                    test_result, info = model.keyword.testKeyword(test_case, self, testSuite)
                if test_result:
                    break
            self.setColor(Qt.green if test_result else Qt.red)
            self.set_errorCode_details(test_result, info)
            self.print_test_info(test_case, test_result)
            self.process_teardown(test_result)
            self.status = self.process_if_bypass(test_case, test_result)
            self.set_errorCode_details(True if self.status == 'True' else False, info)
            self.record_first_fail(test_case, True if self.status == 'True' else False)
            self.generate_report(test_case, test_result, suiteItem)
            self.process_mesVer(test_case)
        except Exception as e:
            self.logger.fatal(f" step run Exception！！{e},{traceback.format_exc()}")
            self.setColor(Qt.darkRed)
            self.status = False
            return False
        else:
            return True if self.status == 'True' else False
        finally:
            if not IsNullOrEmpty(self.SetGlobalVar):
                if bool(self.status):
                    setattr(test_case.myWind.TestVariables, self.SetGlobalVar, self.testValue)
                    self.logger.debug(f"setGlobalVar:{self.SetGlobalVar} = {self.testValue}")
                else:
                    self.logger.debug(f"Step test fail, don't setGlobalVar:{self.SetGlobalVar}")
            self.record_date_to_db(test_case, test_result)
            self.clear()

    def record_date_to_db(self, test_case, test_result):
        """ record test date to DB."""
        if self.isTest and self.Json.lower() == 'y':
            with model.sqlite.Sqlite(gv.database_result) as db:
                self.logger.debug('INSERT test result to result.db table RESULT.')
                db.execute(
                    f"INSERT INTO RESULT (ID,SN,STATION_NAME,STATION_NO,MODEL,SUITE_NAME,ITEM_NAME,SPEC,LSL,"
                    f"VALUE,USL,ELAPSED_TIME,ERROR_CODE,ERROR_DETAILS,START_TIME,TEST_RESULT,STATUS) "
                    f"VALUES (NULL,'{test_case.myWind.SN}','{gv.cf.station.station_name}','{gv.cf.station.station_no}',"
                    f"'{test_case.myWind.dut_model}','{self.SuiteName}','{self.StepName}','{self.spec}','{self.LSL}',"
                    f"'{self.testValue}','{self.USL}',{self.elapsedTime},'{self.error_code}',"
                    f"'{self.error_details}','{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}',"
                    f"'{test_result}','{self.status}')")

    def set_errorCode_details(self, result=False, info=''):
        if result:
            self.error_code = ''
            self.error_details = ''
            return

        if IsNullOrEmpty(self.error_code) and IsNullOrEmpty(self.error_details):
            return

        if IsNullOrEmpty(self.ErrorCode):
            self.error_code = self.EeroName
            self.error_details = self.EeroName
        elif ':' in self.ErrorCode:
            error_list = self.ErrorCode.split()
            if len(error_list) > 1 and info == 'TooHigh':
                self.error_code = error_list[1].split(':')[0].strip()
                self.error_details = error_list[1].split(':')[1].strip()
            else:
                self.error_code = error_list[0].split(':')[0].strip()
                self.error_details = error_list[0].split(':')[1].strip()
        else:
            self.error_code = self.ErrorCode
            self.error_details = self.ErrorCode

    def process_mesVer(self, test_case):
        """collect data to mes"""
        if self.Json.lower() == 'y' and IsNullOrEmpty(self.MesVar):
            self.MesVar = self.EeroName
        if not IsNullOrEmpty(self.MesVar) and self.testValue is not None and str(
                self.testValue).lower() != 'true':
            setattr(test_case.mesPhases, self.MesVar, self.testValue)

    def _if_statement(self, test_case, test_result: bool) -> bool:
        if self.IfElse.lower() == 'if':
            test_case.IfCond = test_result
            if not test_result:
                self.setColor('#FF99CC')
                self.logger.warning(f"if statement fail needs to continue, setting the test result to true")
                test_result = True
        elif self.IfElse.lower() == 'else':
            pass
        else:
            test_case.IfCond = True
        return test_result

    def record_first_fail(self, test_case, tResult):
        if not tResult:
            test_case.failCount += 1
        else:
            return
        if test_case.failCount == 1 and IsNullOrEmpty(test_case.error_code_first_fail):
            test_case.error_code_first_fail = self.error_code
            test_case.error_details_first_fail = self.error_details
            test_case.mesPhases.first_fail = self.SuiteName

    def _process_ByPF(self, step_result: bool):
        if (self.ByPF.upper() == 'P') and not step_result:
            self.setColor(Qt.darkGreen)
            self.logger.warning(f"Let this step:{self.StepName} bypass.")
            return True
        elif (self.ByPF.upper() == 'F') and step_result:
            self.setColor(Qt.darkRed)
            self.logger.warning(f"Let this step:{self.StepName} by fail.")
            return False
        else:
            return step_result

    def clear(self):
        self.error_code = None
        self.error_details = None
        if not gv.IsDebug:
            self.isTest = True
        self.testValue = None
        self.elapsedTime = 0
        self.status = 'exception'

    def process_if_bypass(self, test_case, test_result: bool) -> str:
        result_if = self._if_statement(test_case, test_result)
        by_result = self._process_ByPF(result_if)
        return str(by_result)

    def print_test_info(self, test_case, tResult):
        ts = datetime.now() - self.start_time
        self.elapsedTime = ts.seconds + ts.microseconds / 1000000
        if self.Keyword == 'Waiting':
            return
        result_info = f"{self.StepName} {'pass' if tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}s," \
                      f"Symptom:{self.error_code}:{self.error_details}," \
                      f"spec:{self.spec},Min:{self.LSL},Value:{self.testValue},Max:{self.USL}"
        if tResult:
            self.logger.info(result_info)
        else:
            self.logger.error(result_info)
        if self.Json.lower() == 'y':
            ts = datetime.now() - self.start_time
            self.elapsedTime = ts.seconds + ts.microseconds / 1000000
            if mf.MainForm.main_form is not None:
                mf.MainForm.main_form.my_signals.update_tableWidget[list].emit(
                    [test_case.myWind.SN, self.StepName, self.spec, self.LSL, self.testValue, self.USL,
                     self.elapsedTime, self.start_time.strftime('%Y-%m-%d %H:%M:%S'), 'Pass' if tResult else 'Fail'])

    def report_to_csv(self, test_case, name):
        """collect test result and data into csv file"""
        if name in test_case.csv_list_header:
            return
        if not IsNullOrEmpty(self.USL) or not IsNullOrEmpty(self.LSL):
            test_case.csv_list_header.extend([name, f"{name}_LIMIT_MIN", f"{name}_LIMIT_MAX"])
            test_case.csv_list_data.extend([self.testValue, self.LSL, self.USL])
        elif not IsNullOrEmpty(self.spec):
            test_case.csv_list_header.extend([name, f"{name}_SPEC"])
            test_case.csv_list_data.extend([self.testValue, self.spec])
        else:
            test_case.csv_list_header.append(name)
            test_case.csv_list_data.append(self.testValue)

    def report_to_json(self, test_case, testResult, suiteItem: model.product.SuiteItem = None):
        """copy test data to json object"""
        if self.status != str(True):
            self.start_time_json = test_case.startTimeJson
        obj = model.product.StepItem()
        if self.EeroName.endswith('_'):
            obj.test_name = self.EeroName + str(test_case.ForCycleCounter)
        else:
            obj.test_name = self.EeroName
        obj.status = 'passed' if testResult else 'failed'
        obj.test_value = str(testResult) if self.testValue is None else self.testValue
        obj.units = self.Unit
        obj.error_code = self.error_code
        obj.start_time = self.start_time_json.strftime('%Y-%m-%d %H:%M:%S')
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        obj.finish_time = self.finish_time
        obj.lower_limit = self.LSL
        obj.upper_limit = self.USL
        if not IsNullOrEmpty(self.SPEC) and IsNullOrEmpty(self.LSL):
            obj.lower_limit = self.spec
        # update gv.stationObj.tests json item
        if test_case.jsonObj.tests is not None:
            for item in test_case.jsonObj.tests:
                if item.test_name == obj.test_name:
                    test_case.jsonObj.tests.remove(item)
                    self.logger.debug(f"update testName:{obj.test_name} in json report.")
                    break
            test_case.jsonObj.tests.append(obj)
        # update suiteItem.phase_items json item
        if suiteItem is not None:
            for item in suiteItem.phase_items:
                if item.test_name == obj.test_name:
                    suiteItem.phase_items.remove(item)
                    self.logger.debug(f"update testName:{obj.test_name} in json report.")
                    break
            suiteItem.phase_items.append(obj)

        return obj

    def generate_report(self, test_case, test_result, suiteItem: model.product.SuiteItem):
        """ according to self.json, if record test result and data into json file"""
        if self.Json is not None and self.Json.lower() == 'y':
            obj = self.report_to_json(test_case, test_result, suiteItem)
            self.report_to_csv(test_case, obj.test_name)
        elif not test_result or self.ByPF.lower() == 'f':
            obj = self.report_to_json(test_case, test_result, suiteItem)
            self.report_to_csv(test_case, obj.test_name)

    def process_teardown(self, test_result):
        if IsNullOrEmpty(self.TearDown) or test_result:
            return
        self.logger.debug(f'run teardown command...')
        try:
            if self.TearDown == 'ECUReset':
                gv.PLin.SingleFrame(self.ID, self._NAD, '02', '11 01', self.Timeout)
            else:
                self.logger.warning(f'this teardown({self.TearDown}) no cation.')
        except Exception as e:
            self.logger.fatal(f"process_teardown:{e}")

    def init_online_limit(self):
        pass


if __name__ == "__main__":
    help(Step)
