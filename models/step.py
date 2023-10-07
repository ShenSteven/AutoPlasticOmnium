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
import models.product
import dal.database.sqlite
import models.keyword
from common.basicfunc import IsNullOrEmpty, str_to_int
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
        start_time: 测试项的开始时
        finish_time: 测试结束时间
        start_time_json = None
        error_code = '': 错误码
        error_details = ''：错误码详细描述
        status = 'exception'  # pass,fail,exception
        testValue = None: 测试得到的值
        elapsedTime = 0: 测试步骤耗时
        _isTest：bool 决定步骤是否测试，默认都测试
        ####################### excel header variant ##########################
        _SuiteName: str = ''：测试套名字
        _StepName: str = None: 当前测试step名字
        _ErrorCode: str = None: 测试错误码
        ErrorDetails: str = None: 测试错误码详细描述
        _Retry: int = None: 测试失败retry次数
        _Timeout: int = None: 测试步骤超时时间
        _SubStr1: str = None: 截取字符串 如截取abc中的b SubStr1=a，SubStr2=cf
        _SubStr2: str = None
        _IfElse: str = None: 测试步骤结果是否做为if条件，决定else步骤是否执行
        _For: str = None: 循环测试for(6)开始6次循环，END FOR结束
        _Model: str = None: 机种，根据机种决定哪些用例不跑，哪些用例需要跑
        _CmdOrParam: str = None: 发送的测试命令
        _ExpectStr: str = None: 期待的提示符，用来判断反馈是不是结束了
        _CheckStr1: str = None: 检查反馈是否包含CheckStr1
        _CheckStr2: str = None: 检查反馈是否包含CheckStr2
        _SPEC: str = None: 测试定义的Spec
        _LSL: str = None: 最小限值
        _USL: str = None: 最大限值
        Unit: str = None: 测试值单位
        _MesVar: str = None: 上传MES信息的变量名字
        _ByPF: str = None: 手动人为控制测试结果 P=bypass，F=byFail,空=不干涉测试结果
        _FTC: str = None: 失败继续 fail to continue。y=继续，None|''=不继续
        _Keyword: str = None: 测试步骤对应的关键字，执行对应关键字下的代码段
        _Json: str = None: 测试结果数据是否收集到json文件中并上传给客户.y=收集，None|''=不收集
        _EeroName: str = None: 客户定义的测试步骤名字
        _Param1: str = None
    """

    def __init__(self, dict_=None):
        self.test_result = False
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
        # self._SuiteName: str = ''
        # self._StepName: str = 'Waiting'
        # self._EeroName: str = None
        # self._Keyword: str = 'Waiting'
        # self._ErrorCode: str = None
        # self._ErrorDetails: str = None
        # self._ErrorMsg: str = None
        # self._Retry: int = 0
        # self._Timeout: int = 1
        # self._IfElse: str = None
        # self._For: str = None
        # self._SubStr1: str = None
        # self._SubStr2: str = None
        # self._Model: str = None
        # self._ID: str = None  # PLIN
        # self._NAD: str = None  # PLIN
        # self._PCI_LEN: str = None  # PLIN
        # self._CmdOrParam: str = None
        # self._Param1: str = None
        # self._ExpectStr: str = None
        # self._CheckStr1: str = None
        # self._CheckStr2: str = None
        # self._NoContain: str = None
        # self._SPEC: str = None
        # self._LSL: str = None
        # self._USL: str = None
        # self._Unit: str = None
        # self._SetGlobalVar: str = None
        # self._MesVar: str = None
        # self._ByPF: str = None
        # self._FTC: str = None
        # self._Json: str = None
        # self._TearDown: str = None
        # self.items = list(filter(lambda x: x[0:1].isupper() or x[1:2].isupper(), self.__dict__))
        if dict_ is not None:
            self.__dict__.update(dict_)

    @property
    def index(self):
        if self.myWind is not None:
            self._index = self.myWind.testcase.cloneSuites[self.suiteIndex].steps.index(self)
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def isTest(self):
        if self.myWind is None:
            return self._isTest
        if not IsNullOrEmpty(self.IfElse) and str(self.IfElse).lower() == 'else':
            self._isTest = not self.myWind.testcase.IfElseFlow.ifCond_all
        if not IsNullOrEmpty(self.IfElse) and str(self.IfElse).lower() == 'elif':
            self._isTest = not self.myWind.testcase.IfElseFlow.ifCond_all
        if not IsNullOrEmpty(self.Model) and self.myWind.dut_model.lower() not in self.Model.lower().split():
            self._isTest = False
        if self.myWind.SingleStepTest:
            self._isTest = True
        return self._isTest

    @isTest.setter
    def isTest(self, value):
        self._isTest = value

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
            self._SuiteName = self.myWind.testcase.cloneSuites[self.suiteIndex].name
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
            return None
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
            if '(' in self._For and ')' in self._For:
                return re.findall(r'\((.*?)\)', self._For)[0]
            else:
                return self._For.lower()

    @For.setter
    def For(self, value):
        if '(' in value and ')' in value or value.lower() == 'endfor':
            self._For = value
        elif value.lower() == 'do' or value.lower() == 'while':
            self._For = value
        elif IsNullOrEmpty(value) or value.lower() == 'whiledo' or value.lower() == 'endwhiledo':
            self._For = value
        elif str_to_int(value)[0]:
            self._For = value
        else:
            raise ValueError('Format string: for(10)...endfor/do...while/whiledo...endwhile')

    @property
    def IfElse(self):
        if not hasattr(self, '_IfElse'):
            return None
        else:
            return self._IfElse.lower()

    @IfElse.setter
    def IfElse(self, value):
        if value.lower() == 'if' or value.lower() == '&if' or value.lower() == '||if':
            self._IfElse = value.lower()
        elif value.lower() == 'elif' or value.lower() == 'else':
            self._IfElse = value.lower()
        elif IsNullOrEmpty(value):
            self._IfElse = value
        else:
            raise ValueError('Format string: if,&if,||if,elif,else')

    @property
    def FTC(self):
        if not hasattr(self, '_FTC'):
            return 'Y' if gv.cfg.station.fail_continue else 'N'
        elif self._FTC.lower() == 'n' or self._FTC.lower() == 'y':
            return self._FTC.upper()
        else:
            return 'Y' if gv.cfg.station.fail_continue else 'N'

    @FTC.setter
    def FTC(self, value):
        if value.upper() == 'Y' or value.upper() == 'N':
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
        if value is None:
            del self._ByPF
            return
        if value.upper() == 'P' or value.upper() == 'F':
            self._ByPF = value
        elif value == 'None' or value == '':
            self._ByPF = ''
        else:
            raise ValueError("Value: 'P'=bypass，'F'=byFail, None/''=不干涉测试结果")

    @property
    def Model(self):
        if not hasattr(self, '_Model') or self._Model is None:
            return None
        else:
            return self._Model

    @Model.setter
    def Model(self, value):
        self._Model = value

    @property
    def CmdOrParam(self):
        if not hasattr(self, '_CmdOrParam') or self._CmdOrParam is None:
            return ''
        else:
            if self.myWind is not None and self.myWind.startFlag:
                return parse_expr(self.parse_var(self._CmdOrParam))
            else:
                return self.parse_var(self._CmdOrParam)

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
    def ID(self):
        if not hasattr(self, '_ID'):
            return None
        return self.parse_var(self._ID)

    @ID.setter
    def ID(self, value):
        self._ID = value

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
                self.myWind.mySignals.treeWidgetColor.emit(color, self.suiteIndex, self.index, False)
        except RuntimeError:
            pass

    def run(self, test_case, testSuite, suiteItem: models.product.SuiteItem = None):
        """run test step"""
        self.myWind = test_case.myWind
        if self.logger is None:
            self.logger = test_case.logger
        self.SuiteName = testSuite.name
        self.suiteIndex = testSuite.index
        self.suiteVar = testSuite.suiteVar
        info = ''
        self.set_json_start_time(test_case)
        self.start_time = datetime.now()
        self.test_result = False

        try:
            if self.isTest:
                if test_case.WhileLoop is not None and test_case.WhileLoop.while_condition is not None:
                    if not test_case.WhileLoop.while_condition:
                        self.test_result = True
                        self.status = str(self.test_result)
                        self.setColor(Qt.lightGray)
                        return True
                if not isinstance(self.myWind, ui.mainform.MainForm):
                    self.myWind.mySignals.updateLabel[QLabel, str].emit(self.myWind.lb_testName,
                                                                        f"<A href='file:///{self.myWind.txtLogPath}'>{self.StepName}</A>")
                self.logger.debug(f"<a name='testStep:{self.SuiteName}-{self.StepName}'>Start:{self.StepName},"
                                  f"Keyword:{self.Keyword},Retry:{self.Retry},Timeout:{self.Timeout}s,"
                                  f"SubStr:{self.SubStr1} - {self.SubStr2},"
                                  f"MesVer:{self.MesVar},FTC:{self.FTC}</a>")
                self.setColor(Qt.yellow)
                self.init_online_limit()
                self.start_loop(test_case, testSuite)
            else:
                if not self.myWind.IsCycle:
                    self.setColor(Qt.gray)
                self.test_result = True
                self.status = str(self.test_result)
                test_case.stepFinishNum += 1
                # test_case.sumStep -= 1
                self.myWind.mySignals.updateProgressBar[int, int].emit(test_case.stepFinishNum, test_case.sumStep)
                return True
        except Exception as e:
            self.logger.fatal(f"TestStep precondition Exception!{e},{traceback.format_exc()}")
            self.setColor(Qt.darkRed)
            self.status = 'exception'
            self.record_first_fail(test_case, str(self.status), 'TestStep precondition Exception!!!')
            return False

        try:
            self.set_breakpoint()
            for retry in range(self.Retry, -1, -1):
                if self.myWind.pause_event.wait():
                    if gv.cfg.dut.test_mode == 'debug' or gv.IsDebug and self.Keyword in gv.cfg.dut.debug_skip:
                        self.logger.debug('This is debug mode.Skip this step.')
                        self.test_result, info = True, ''
                    else:
                        self.test_result, info = models.keyword.testKeyword(self.Keyword, self, test_case)
                        self.test_keyword_finally(test_case)
                if self.test_result:
                    break
            self.setColor(Qt.green if self.test_result else Qt.red)
            self.set_errorCode_details(str(self.test_result), info)
            self.print_test_info(test_case)
            self.process_teardown()
            result_if = self._if_statement(test_case, self.test_result)
            self.status = str(self._process_bypass_byfail(result_if))
            self.record_first_fail(test_case, str(self.status), info)
            self.record_test_data(test_case, str(self.status), suiteItem)
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
                if bool(self.test_result):
                    setattr(test_case.myWind.TestVariables, self.SetGlobalVar, self.testValue)
                    self.logger.debug(f"setGlobalVar:{self.SetGlobalVar} = {self.testValue}")
                else:
                    self.logger.debug(f"Step test fail, don't setGlobalVar:{self.SetGlobalVar}")
            self.record_date_to_db(test_case, self.test_result)
            test_case.stepFinishNum += 1
            if (test_case.ForLoop is not None and not test_case.ForLoop.IsEnd) or \
                    (test_case.DoWhileLoop is not None and not test_case.DoWhileLoop.IsEnd) or \
                    (test_case.WhileLoop is not None and not test_case.WhileLoop.IsEnd):
                # if test_case.loop is not None and not test_case.loop.IsEnd:
                test_case.sumStep += 1
            self.myWind.mySignals.updateProgressBar[int, int].emit(test_case.stepFinishNum, test_case.sumStep)
            self.clear()
            test_case.IfElseFlow.clear(self.IfElse)

    def set_breakpoint(self):
        if self.breakpoint or self.myWind.pauseFlag:
            self.myWind.pauseFlag = True
            if isinstance(self.myWind, ui.mainform.MainForm):
                self.myWind.mySignals.setIconSignal[QAction, QIcon].emit(
                    self.myWind.actionStart, QIcon(':/images/Start-icon.png'))
            self.myWind.pause_event.clear()
            self.myWind.treeView.blockSignals(False)
        else:
            self.myWind.pause_event.set()

    def test_keyword_finally(self, test_case):
        if (self.StepName.startswith("GetDAQResistor") or self.StepName.startswith("GetDAQTemp") or
                self.Keyword == "NiDAQmxVolt" or self.Keyword == "NiDAQmxCur"):
            test_case.ArrayListDaq.append("N/A" if IsNullOrEmpty(self.testValue) else self.testValue)
            test_case.ArrayListDaqHeader.append(self.StepName)
            self.logger.debug(f"DQA add {self.testValue}")

    def record_date_to_db(self, test_case, test_result):
        """ record test date to DB."""
        SQL_statements = f'''INSERT INTO RESULT 
                      (ID,SN,STATION_NAME,STATION_NO,MODEL,SUITE_NAME,ITEM_NAME,SPEC,LSL,VALUE,USL,
                      ELAPSED_TIME,ERROR_CODE,ERROR_DETAILS,START_TIME,TEST_RESULT,STATUS) 
                      VALUES (NULL,'{test_case.myWind.SN}','{gv.cfg.station.station_name}','{gv.cfg.station.station_no}',
                      '{test_case.myWind.dut_model}','{self.SuiteName}','{self.StepName}','{self.SPEC}','{self.LSL}',
                      '{self.testValue}','{self.USL}',{self.elapsedTime},'{self.error_code}','{self.error_details}',
                      '{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}','{test_result}','{self.status}')
                      '''
        if self.isTest and self.Json == 'Y':
            with dal.database.sqlite.Sqlite(gv.DatabaseResult) as db:
                self.logger.debug('INSERT test result to result.db table RESULT.')
                db.execute_commit(SQL_statements)
            # with database.mysql.MySQL(host='127.0.0.1', port=3306, user='root', passwd='123456') as db:
            #     self.logger.debug('INSERT test result to result.db table RESULT.')
            #     db.execute_commit(SQL_statements)

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
        if IsNullOrEmpty(self.IfElse):
            pass
        else:
            condition = test_case.IfElseFlow.process_if_else_flow(self.IfElse, test_result)
            if not condition:
                self.setColor(Qt.darkCyan)
                self.logger.warning(f"if statement fail needs to continue, setting the test result to true")
                test_result = True
        return test_result

    def record_first_fail(self, test_case, status: str, info):
        self.set_errorCode_details(status, info)
        if status != str(True):
            test_case.failCount += 1
        else:
            return
        if test_case.failCount == 1 and IsNullOrEmpty(test_case.errorCodeFirstFail):
            test_case.errorCodeFirstFail = self.error_code if self.error_code is not None else '0.0.0'
            test_case.errorDetailsFirstFail = self.error_details if self.error_details is not None else 'NoErrorCode'
            test_case.mesPhases.first_fail = self.SuiteName

    def _process_bypass_byfail(self, step_result: bool):
        if not IsNullOrEmpty(self.For) and self.For == 'while':
            if not step_result:
                self.setColor(Qt.darkMagenta)
                self.logger.warning(f"do while condition fail, needs to continue, setting the test result to true")
                step_result = True
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
        # self.logger = None

    def print_test_info(self, test_case):
        ts = datetime.now() - self.start_time
        self.elapsedTime = "%.3f" % (ts.seconds + ts.microseconds / 1000000)
        if self.Keyword == 'Waiting':
            return
        result_info = f"{self.StepName} {'pass' if self.test_result else 'fail'}!! ElapsedTime:{self.elapsedTime}s," \
                      f"Symptom:{self.error_code}:{self.error_details}," \
                      f"spec:{self.SPEC},Min:{self.LSL},Value:{self.testValue}, Max: {self.USL}"
        if self.test_result:
            self.logger.info(result_info)
        else:
            self.logger.error(result_info)
        if self.Json == 'Y':
            ts = datetime.now() - self.start_time
            self.elapsedTime = "%.3f" % (ts.seconds + ts.microseconds / 1000000)
            if isinstance(self.myWind, ui.mainform.MainForm):
                self.myWind.mySignals.update_tableWidget[list].emit(
                    [test_case.myWind.SN, self.StepName, self.SPEC, self.LSL, self.testValue, self.USL,
                     self.elapsedTime, self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                     'Pass' if self.test_result else 'Fail'])

    def record_to_csv(self, test_case, name):
        """collect test result and data into csv file"""
        if name in test_case.csvListHeader:
            return
        if not IsNullOrEmpty(self.USL) or not IsNullOrEmpty(self.LSL):
            test_case.csvListHeader.extend([name, f"{name}_LIMIT_MIN", f"{name}_LIMIT_MAX"])
            test_case.csvListData.extend([self.testValue, self.LSL, self.USL])
        elif not IsNullOrEmpty(self.SPEC):
            test_case.csvListHeader.extend([name, f"{name}_SPEC"])
            test_case.csvListData.extend([self.testValue, self.SPEC])
        else:
            test_case.csvListHeader.append(name)
            test_case.csvListData.append(self.testValue)

    def record_to_json(self, test_case, testResult, suiteItem: models.product.SuiteItem = None):
        """copy test data to json object"""
        if self.status != str(True):
            self.start_time_json = test_case.startTimeJson
        obj = models.product.StepItem()
        if self.EeroName is None:
            obj.test_name = self.StepName
        elif self.EeroName.endswith('_'):
            # obj.test_name = self.EeroName + str(test_case.ForLoop.LoopCounter)
            obj.test_name = self.EeroName + str(test_case.loop.LoopCounter)
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

    def record_test_data(self, test_case, test_result, suiteItem: models.product.SuiteItem):
        """ according to self.Json record test result and data into json file"""
        if self.Json == 'Y':
            obj = self.record_to_json(test_case, test_result, suiteItem)
            self.record_to_csv(test_case, obj.test_name)
        elif not test_result or self.ByPF == 'F':
            obj = self.record_to_json(test_case, test_result, suiteItem)
            self.record_to_csv(test_case, obj.test_name)

    def process_teardown(self):
        if IsNullOrEmpty(self.TearDown) or self.test_result:
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

    def start_loop(self, test_case, suit):
        """FOR 循环开始判断 FOR(3)"""
        import bll.flowcontrol.dowhile
        if IsNullOrEmpty(self.For):
            return
        if str_to_int(self.For)[0]:
            if test_case.ForLoop is None:
                test_case.ForLoop = bll.flowcontrol.forloop.ForLoop(self.logger)
            test_case.ForLoop.start(suit.index, self.index, int(self.For))
            # test_case.loop = flowcontrol.forloop.ForLoop(self.logger)
            # test_case.loop.start(suit.index, self.index, int(self.For))
        elif self.For.lower() == "do":
            if test_case.DoWhileLoop is None:
                test_case.DoWhileLoop = bll.flowcontrol.dowhile.DoWhile(self.logger)
            test_case.DoWhileLoop.start(suit.index, self.index)
            # test_case.loop = flowcontrol.dowhile.DoWhile(self.logger)
            # test_case.loop.start(suit.index, self.index)

    def end_loop(self, test_case, step_result, index):
        """FOR 循环结束判断 END FOR"""
        import bll.flowcontrol.whileloop
        if IsNullOrEmpty(self.For):
            return False
        if self.For.lower() == 'endfor':
            is_end = not test_case.ForLoop.is_end()
            # is_end = not test_case.loop.is_end()
            return is_end
        elif self.For.lower() == "while":
            is_end = not test_case.DoWhileLoop.is_end(step_result)
            # is_end = not test_case.loop.is_end(step_result)
            return is_end
        elif self.For.lower() == "endwhiledo":
            is_end = not test_case.WhileLoop.is_end()
            # is_end = not test_case.loop.is_end()
            return is_end
        if self.For.lower() == "whiledo":
            if test_case.WhileLoop is None:
                test_case.WhileLoop = bll.flowcontrol.whileloop.WhileLoop(self.logger)
            if step_result:
                test_case.WhileLoop.start(index, self.index, step_result)
                # test_case.loop.start(index, self.index, step_result)
                return False
            else:
                if not IsNullOrEmpty(self.FTC) and self.FTC == 'Y':
                    test_case.WhileLoop.start(index, self.index, False)
                    # test_case.loop.start(index, self.index, False)
                    self.logger.warning(f"while condition fail, but by pass to continue.")
                    return False
                else:
                    return False


if __name__ == "__main__":
    help(Step)
