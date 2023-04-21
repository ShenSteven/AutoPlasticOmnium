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
from PyQt5.QtWidgets import QAction, QLabel
import model.product
import database.sqlite
import model.keyword
from .basicfunc import IsNullOrEmpty
import conf.globalvar as gv
import ui.mainform


def parse_expr(value):
    """当CmdOrParam中有表达式时，计算表达式"""
    if value is None:
        return value
    for a in re.findall(r'{(.*?)}', value):
        try:
            varVal = str(eval(a))
        except:
            raise
        else:
            value = re.compile('{' + f'{a}' + '}').sub(varVal, value, count=1)
    return value


class Step:
    """测试步骤类
    Attributes:
        suiteIndex: 测试套序列号
        _index: 当前测试step序列号
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
        _ByPF: str = None: 手动人为控制测试结果 P=bypass，F=byFail,空=不干涉测试结果
        _FTC: str = None: 失败继续 fail to continue。y=继续，None|''=不继续
        Keyword: str = None: 测试步骤对应的关键字，执行对应关键字下的代码段
        _Json: str = None: 测试结果数据是否收集到json文件中并上传给客户.y=收集，None|''=不收集
        EeroName: str = None: 客户定义的测试步骤名字
        Param1: str = None
    """

    def __init__(self, dict_=None):
        self.myWind = None
        self.logger = None
        self.breakpoint: bool = False
        self.suiteIndex: int = 0
        self._index: int = 0
        self.testValue = None
        self.start_time = None
        self.finish_time = None
        self.start_time_json = None
        self.error_code: str = ''
        self.error_details: str = ''
        self.status: str = 'exception'  # pass/fail/exception
        self.elapsedTime = 0
        self._isTest = True
        self.suiteVar = ''
        # ============= Excel Column ===============
        # self.SuiteName: str = ''
        # self.StepName: str = 'Waiting'
        # self.EeroName: str = None
        # self.Keyword: str = 'Waiting'
        # self.ErrorCode: str = None
        # self.ErrorDetails: str = None
        # self.Retry: int = 0
        # self.Timeout: int = 1
        # self.IfElse: str = None
        # self.For: str = None
        # self.SubStr1: str = None
        # self.SubStr2: str = None
        # self.Model: str = None
        # self.ID: str = None  # PLIN
        # self.NAD: str = None  # PLIN
        # self.PCI_LEN: str = None  # PLIN
        # self.CmdOrParam: str = None
        # self.Param1: str = None
        # self.ExpectStr: str = None
        # self.CheckStr1: str = None
        # self.CheckStr2: str = None
        # self.NoContain: str = None
        # self.SPEC: str = None
        # self.LSL: str = None
        # self.USL: str = None
        # self.Unit: str = None
        # self.SetGlobalVar: str = None
        # self.MesVar: str = None
        # self._ByPF: str = None
        # self._FTC: str = None
        # self._Json: str = None
        # self.TearDown: str = None
        # self.items = list(filter(lambda x: x[0:1].isupper() or x[1:2].isupper(), self.__dict__))
        if dict_ is not None:
            self.__dict__.update(dict_)

    # def __iter__(self):
    #     self.index = -1
    #     return self
    #
    # def __next__(self):
    #     self.index += 1
    #     if self.index >= len(self.items):
    #         raise StopIteration
    #     return self.items[self.index]

    # def __getitem__(self, i):
    #     if i >= len(self.items):
    #         raise IndexError("out of index")
    #     item = self.items[i]
    #     return item

    @property
    def SuiteName(self):
        if not hasattr(self, '_SuiteName'):
            return None
        if self.myWind is not None:
            self._SuiteName = self.myWind.testcase.clone_suites[self.suiteIndex].name
        return self._SuiteName

    @SuiteName.setter
    def SuiteName(self, value):
        self._SuiteName = value

    @property
    def StepName(self):
        if not hasattr(self, '_StepName'):
            return None
        return self._StepName

    @StepName.setter
    def StepName(self, value):
        if IsNullOrEmpty(value):
            raise Exception('StepName cannot be null or empty!')
        self._StepName = value

    @property
    def EeroName(self):
        if not hasattr(self, '_EeroName'):
            return None
        return self._EeroName

    @EeroName.setter
    def EeroName(self, value):
        if value == '':
            self._EeroName = self.StepName
        else:
            self._EeroName = value

    @property
    def ErrorCode(self):
        if not hasattr(self, '_ErrorCode'):
            return ''
        else:
            return self._ErrorCode

    @ErrorCode.setter
    def ErrorCode(self, value):
        self._ErrorCode = value

    @property
    def Keyword(self):
        if not hasattr(self, '_Keyword'):
            return None
        return self._Keyword

    @Keyword.setter
    def Keyword(self, value):
        if IsNullOrEmpty(value):
            raise Exception('Keyword cannot be null or empty!')
        if value.lower() == 'default':
            self._Keyword = value
            gv.Keywords.append(value)
        if value not in gv.Keywords:
            raise ValueError(f"Keyword '{value}' not in keywords list :{gv.Keywords}")
        else:
            self._Keyword = value

    @property
    def Retry(self):
        if not hasattr(self, '_Retry') or self._Retry is None:
            return 0
        else:
            return self._Retry

    @Retry.setter
    def Retry(self, value):
        try:
            self._Retry = int(value)
        except ValueError:
            raise

    @property
    def Timeout(self):
        if not hasattr(self, '_Timeout') or self._Timeout is None:
            return 1
        else:
            return self._Timeout

    @Timeout.setter
    def Timeout(self, value):
        try:
            self._Timeout = int(value)
        except ValueError:
            raise

    @property
    def SubStr1(self):
        if not hasattr(self, '_SubStr1') or self._SubStr1 is None:
            return ''
        else:
            return self._SubStr1

    @SubStr1.setter
    def SubStr1(self, value):
        self._SubStr1 = value

    @property
    def SubStr2(self):
        if not hasattr(self, '_SubStr2') or self._SubStr2 is None:
            return ''
        else:
            return self._SubStr2

    @SubStr2.setter
    def SubStr2(self, value):
        self._SubStr2 = value

    @property
    def For(self):
        if not hasattr(self, '_For') or self._For is None:
            return None
        else:
            return self._For

    @For.setter
    def For(self, value):
        if '(' in value and ')' in value:
            self._For = value
        elif value.lower().startswith('end'):
            self._For = value
        elif IsNullOrEmpty(value):
            self._For = value
        else:
            raise ValueError('Format example: For(10) or END/ENDFOR')

    @property
    def IfElse(self):
        if not hasattr(self, '_IfElse'):
            return None
        else:
            return self._IfElse.lower()

    @IfElse.setter
    def IfElse(self, value):
        self._IfElse = value

    @property
    def FTC(self):
        if not hasattr(self, '_FTC'):
            return None
        else:
            return self._FTC.upper()

    @FTC.setter
    def FTC(self, value):
        if value.upper() == 'Y':
            self._FTC = value
        elif value == 'None' or value == '':
            self._FTC = ''
        else:
            raise ValueError("fail to continue. Y=继续，None/''=不继续")

    @property
    def Json(self):
        if not hasattr(self, '_Json'):
            return None
        else:
            return self._Json.upper()

    @Json.setter
    def Json(self, value):
        if value.upper() == 'Y':
            self._Json = value
        elif value == 'None' or value == '':
            self._Json = ''
        else:
            raise ValueError("数据收集到json文件.Y=收集，None/''=不收集")

    @property
    def ByPF(self):
        if not hasattr(self, '_ByPF'):
            return None
        else:
            return self._ByPF.upper()

    @ByPF.setter
    def ByPF(self, value):
        if value.upper() == 'P' or value.upper() == 'F':
            self._ByPF = value
        elif value == 'None' or value == '':
            self._ByPF = ''
        else:
            raise ValueError("Value: 'P'=bypass，'F'=byFail, None/''=不干涉测试结果")

    @property
    def index(self):
        if self.myWind is not None:
            self._index = self.myWind.testcase.clone_suites[self.suiteIndex].steps.index(self)
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def isTest(self):
        if self.myWind is None:
            return self._isTest
        if not IsNullOrEmpty(self.IfElse) and str(self.IfElse).lower() == 'else':
            self._isTest = not self.myWind.testcase.IfCond
        if not IsNullOrEmpty(self.Model) and self.myWind.dut_model.lower() not in self.Model.split():
            self._isTest = False
        if self.myWind.SingleStepTest:
            self._isTest = True
        return self._isTest

    @isTest.setter
    def isTest(self, value):
        self._isTest = value

    @property
    def Model(self):
        if not hasattr(self, '_Model') or self._Model is None:
            return None
        else:
            return self._Model.lower()

    @Model.setter
    def Model(self, value):
        self._Model = value

    @property
    def CmdOrParam(self):
        if not hasattr(self, '_CmdOrParam') or self._CmdOrParam is None:
            return ''
        else:
            return parse_expr(self.parse_var(self._CmdOrParam))

    @CmdOrParam.setter
    def CmdOrParam(self, value):
        self._CmdOrParam = value

    @property
    def ExpectStr(self):
        if not hasattr(self, '_ExpectStr') or self._ExpectStr is None:
            return ''
        else:
            return self.parse_var(self._ExpectStr)

    @ExpectStr.setter
    def ExpectStr(self, value):
        self._ExpectStr = value

    @property
    def CheckStr1(self):
        if not hasattr(self, '_CheckStr1') or self._CheckStr1 is None:
            return ''
        else:
            return self.parse_var(self._CheckStr1)

    @CheckStr1.setter
    def CheckStr1(self, value):
        self._CheckStr1 = value

    @property
    def CheckStr2(self):
        if not hasattr(self, '_CheckStr2') or self._CheckStr2 is None:
            return ''
        else:
            return self.parse_var(self._CheckStr2)

    @CheckStr2.setter
    def CheckStr2(self, value):
        self._CheckStr2 = value

    @property
    def SPEC(self):
        if not hasattr(self, '_SPEC'):
            return None
        return self.parse_var(self._SPEC)

    @SPEC.setter
    def SPEC(self, value):
        self._SPEC = value

    @property
    def USL(self):
        if not hasattr(self, '_USL'):
            return None
        else:
            return self._USL

    @USL.setter
    def USL(self, value):
        self._USL = value

    @property
    def LSL(self):
        if not hasattr(self, '_LSL'):
            return None
        else:
            return self._LSL

    @LSL.setter
    def LSL(self, value):
        self._LSL = value

    @property
    def SetGlobalVar(self):
        if not hasattr(self, '_SetGlobalVar'):
            return None
        else:
            return self._SetGlobalVar

    @SetGlobalVar.setter
    def SetGlobalVar(self, value):
        self._SetGlobalVar = value

    @property
    def MesVar(self):
        if not hasattr(self, '_MesVar'):
            return None
        else:
            return self._MesVar

    @MesVar.setter
    def MesVar(self, value):
        self._MesVar = value

    @property
    def TearDown(self):
        if not hasattr(self, '_TearDown'):
            return None
        else:
            return self._TearDown

    @TearDown.setter
    def TearDown(self, value):
        self._TearDown = value

    @property
    def Param1(self):
        if not hasattr(self, '_Param1'):
            return None
        return self.parse_var(self._Param1)

    @Param1.setter
    def Param1(self, value):
        self._Param1 = value

    @property
    def NAD(self):
        if not hasattr(self, '_NAD'):
            return None
        return self.parse_var(self._NAD)

    @NAD.setter
    def NAD(self, value):
        self._NAD = value

    @property
    def PCI_LEN(self):
        if not hasattr(self, '_PCI_LEN'):
            return None
        return self.parse_var(self._PCI_LEN)

    @PCI_LEN.setter
    def PCI_LEN(self, value):
        self._PCI_LEN = value

    # @staticmethod
    def parse_var(self, value):
        """当CmdOrParam中有变量时，把命令中的<>字符替换成对应的变量值"""
        if self.myWind is None or value is None:
            return value
        if self.myWind.TestVariables is None:
            return value
        for a in re.findall(r'<(.*?)>', value):
            if a.startswith('Config.'):
                temp = a.split('.')
                varVal = str(dict(dict(getattr(self.myWind.TestVariables, temp[0]))[temp[1]])[temp[2]])
            else:
                varVal = getattr(self.myWind.TestVariables, a)
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
        try:
            if isinstance(self.myWind, ui.mainform.MainForm):
                self.myWind.my_signals.treeWidgetColor.emit(color, self.suiteIndex, self.index, False)
        except RuntimeError:
            pass

    def run(self, test_case, testSuite, suiteItem: model.product.SuiteItem = None):
        """run test step"""
        self.myWind = test_case.myWind
        if self.logger is None:
            self.logger = testSuite.logger
        self.SuiteName = testSuite.name
        self.suiteIndex = testSuite.index
        self.suiteVar = testSuite.suiteVar
        info = ''
        test_result = False
        self.set_json_start_time(test_case)
        self.start_time = datetime.now()

        try:
            if self.isTest:
                if not isinstance(self.myWind, ui.mainform.MainForm):
                    self.myWind.my_signals.updateLabel[QLabel, str].emit(self.myWind.lb_testName,
                                                                         f"<A href='https://www.qt.io/'>{self.StepName}</A>")
                self.setColor(Qt.yellow)
                self.logger.debug(f"<a name='testStep:{self.SuiteName}-{self.StepName}'>Start:{self.StepName},"
                                  f"Keyword:{self.Keyword},Retry:{self.Retry},Timeout:{self.Timeout}s,"
                                  f"SubStr:{self.SubStr1} - {self.SubStr2},"
                                  f"MesVer:{self.MesVar},FTC:{self.FTC}</a>")
                self.init_online_limit()
            else:
                if not self.myWind.IsCycle:
                    self.setColor(Qt.gray)
                test_result = True
                self.status = str(test_result)
                return True

            if self.breakpoint or self.myWind.pauseFlag:
                self.myWind.pauseFlag = True
                if isinstance(self.myWind, ui.mainform.MainForm):
                    self.myWind.my_signals.setIconSignal[QAction, QIcon].emit(
                        self.myWind.ui.actionStart, QIcon(':/images/Start-icon.png'))
                self.myWind.pause_event.clear()
            else:
                self.myWind.pause_event.set()

            for retry in range(self.Retry, -1, -1):
                if self.myWind.pause_event.wait():
                    test_result, info = model.keyword.testKeyword(test_case, self)
                if test_result:
                    break
            self.setColor(Qt.green if test_result else Qt.red)
            self.set_errorCode_details(str(test_result), info)
            self.print_test_info(test_case, test_result)
            self.process_teardown(test_result)
            self.status = self.process_if_bypass(test_case, test_result)
            self.record_first_fail(test_case, str(self.status), info)
            self.generate_report(test_case, test_result, suiteItem)
            self.process_mesVer(test_case)
        except Exception as e:
            self.logger.fatal(f" step run Exception！！{e},{traceback.format_exc()}")
            self.setColor(Qt.darkRed)
            self.status = 'exception'
            self.record_first_fail(test_case, str(self.status), info)
            return False
        else:
            return True if self.status == 'True' else False
        finally:
            if not IsNullOrEmpty(self.SetGlobalVar) and self.isTest:
                if bool(self.status):
                    setattr(test_case.myWind.TestVariables, self.SetGlobalVar, self.testValue)
                    self.logger.debug(f"setGlobalVar:{self.SetGlobalVar} = {self.testValue}")
                else:
                    self.logger.debug(f"Step test fail, don't setGlobalVar:{self.SetGlobalVar}")
            self.record_date_to_db(test_case, test_result)
            self.clear()

    def record_date_to_db(self, test_case, test_result):
        """ record test date to DB."""
        if self.isTest and self.Json == 'Y':
            with database.sqlite.Sqlite(gv.database_result) as db:
                self.logger.debug('INSERT test result to result.db table RESULT.')
                db.execute(
                    f"INSERT INTO RESULT (ID,SN,STATION_NAME,STATION_NO,MODEL,SUITE_NAME,ITEM_NAME,SPEC,LSL,"
                    f"VALUE,USL,ELAPSED_TIME,ERROR_CODE,ERROR_DETAILS,START_TIME,TEST_RESULT,STATUS) "
                    f"VALUES (NULL,'{test_case.myWind.SN}','{gv.cf.station.station_name}','{gv.cf.station.station_no}',"
                    f"'{test_case.myWind.dut_model}','{self.SuiteName}','{self.StepName}','{self.SPEC}',"
                    f"'{self.LSL}','{self.testValue}','{self.USL}',"
                    f"{self.elapsedTime},'{self.error_code}',"
                    f"'{self.error_details}','{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}',"
                    f"'{test_result}','{self.status}')")

    def set_errorCode_details(self, status: str, info=''):
        if status == str(True):
            self.error_code = ''
            self.error_details = ''
        elif status == 'exception':
            self.error_code = self.ErrorCode if hasattr(self, 'ErrorCode') else None
            self.error_details = 'exception!'
        else:
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
        if self.Json == 'Y' and IsNullOrEmpty(self.MesVar):
            self.MesVar = self.EeroName
        if not IsNullOrEmpty(self.MesVar) and self.testValue is not None and str(self.testValue).lower() != 'true':
            setattr(test_case.mesPhases, self.MesVar, self.testValue)

    def _if_statement(self, test_case, test_result: bool) -> bool:
        if not IsNullOrEmpty(self.IfElse) and self.IfElse == 'if':
            test_case.IfCond = test_result
            if not test_result:
                self.setColor('#FF99CC')
                self.logger.warning(f"if statement fail needs to continue, setting the test result to true")
                test_result = True
        elif not IsNullOrEmpty(self.IfElse) and self.IfElse == 'else':
            pass
        else:
            test_case.IfCond = True
        return test_result

    def record_first_fail(self, test_case, status: str, info):
        self.set_errorCode_details(status, info)
        if status != str(True):
            test_case.failCount += 1
        else:
            return
        if test_case.failCount == 1 and IsNullOrEmpty(test_case.error_code_first_fail):
            test_case.error_code_first_fail = self.error_code
            test_case.error_details_first_fail = self.error_details
            test_case.mesPhases.first_fail = self.SuiteName

    def _process_ByPF(self, step_result: bool):
        if self.ByPF == 'P' and not step_result:
            self.setColor(Qt.darkGreen)
            self.logger.warning(f"Let this step:{self.StepName} bypass.")
            return True
        elif self.ByPF == 'F' and step_result:
            self.setColor(Qt.darkRed)
            self.logger.warning(f"Let this step:{self.StepName} by fail.")
            return False
        else:
            return step_result

    def clear(self):
        self.error_code = ''
        self.error_details = ''
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
        self.elapsedTime = "%.3f" % (ts.seconds + ts.microseconds / 1000000)
        if self.Keyword == 'Waiting':
            return
        result_info = f"{self.StepName} {'pass' if tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}s," \
                      f"Symptom:{self.error_code}:{self.error_details}," \
                      f"spec:{self.SPEC},Min:{self.LSL},Value:{self.testValue}, Max: {self.USL}"
        if tResult:
            self.logger.info(result_info)
        else:
            self.logger.error(result_info)
        if self.Json == 'Y':
            ts = datetime.now() - self.start_time
            self.elapsedTime = "%.3f" % (ts.seconds + ts.microseconds / 1000000)
            if isinstance(self.myWind, ui.mainform.MainForm):
                self.myWind.my_signals.update_tableWidget[list].emit(
                    [test_case.myWind.SN, self.StepName, self.SPEC, self.LSL, self.testValue, self.USL,
                     self.elapsedTime, self.start_time.strftime('%Y-%m-%d %H:%M:%S'), 'Pass' if tResult else 'Fail'])

    def report_to_csv(self, test_case, name):
        """collect test result and data into csv file"""
        if name in test_case.csv_list_header:
            return
        if not IsNullOrEmpty(self.USL) or not IsNullOrEmpty(self.LSL):
            test_case.csv_list_header.extend([name, f"{name}_LIMIT_MIN", f"{name}_LIMIT_MAX"])
            test_case.csv_list_data.extend([self.testValue, self.LSL, self.USL])
        elif not IsNullOrEmpty(self.SPEC):
            test_case.csv_list_header.extend([name, f"{name}_SPEC"])
            test_case.csv_list_data.extend([self.testValue, self.SPEC])
        else:
            test_case.csv_list_header.append(name)
            test_case.csv_list_data.append(self.testValue)

    def report_to_json(self, test_case, testResult, suiteItem: model.product.SuiteItem = None):
        """copy test data to json object"""
        if self.status != str(True):
            self.start_time_json = test_case.startTimeJson
        obj = model.product.StepItem()
        if self.EeroName is None:
            obj.test_name = self.StepName
        elif self.EeroName.endswith('_'):
            obj.test_name = self.EeroName + str(test_case.ForCycleCounter)
        else:
            obj.test_name = self.EeroName
        obj.status = 'passed' if testResult else 'failed'
        obj.test_value = str(testResult) if self.testValue is None else self.testValue
        obj.units = self.Unit if hasattr(self, 'Unit') else None
        obj.error_code = self.error_code
        obj.start_time = self.start_time_json.strftime('%Y-%m-%d %H:%M:%S')
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        obj.finish_time = self.finish_time
        obj.lower_limit = self.LSL
        obj.upper_limit = self.USL
        if not IsNullOrEmpty(self.SPEC) and IsNullOrEmpty(self.LSL):
            obj.lower_limit = self.SPEC
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
        if self.Json == 'Y':
            obj = self.report_to_json(test_case, test_result, suiteItem)
            self.report_to_csv(test_case, obj.test_name)
        elif not test_result or self.ByPF == 'F':
            obj = self.report_to_json(test_case, test_result, suiteItem)
            self.report_to_csv(test_case, obj.test_name)

    def process_teardown(self, test_result):
        if IsNullOrEmpty(self.TearDown) or test_result:
            return
        self.logger.debug(f'run teardown command...')
        try:
            if self.TearDown == 'ECUReset':
                gv.PLin.SingleFrame(self.ID, self.NAD, '02', '11 01', self.Timeout)
            else:
                self.logger.warning(f'this teardown({self.TearDown}) no cation.')
        except Exception as e:
            raise e

    def init_online_limit(self):
        pass

    def check_keyword(self, Keyword):
        pass


if __name__ == "__main__":
    help(Step)
