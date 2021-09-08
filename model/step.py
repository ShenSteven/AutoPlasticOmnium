#!/usr/bin/env python
# coding: utf-8
"""
@File   : test step.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
from datetime import datetime
from bin.basefunc import IsNullOrEmpty
from bin.globalconf import logger  # , set_global, get_global
from bin import globalvar as gv
from model.product import phase_items, test_phases
from model.test import test
from bin.globalvar import set_globalVal, get_globalVal

count = 0
IfCond = True
setError = True


class TestStep:
    index = 0  # 当前测试step序列号
    tResult = False  # 测试项测试结果
    # isTest = True  # 是否测试,不测试的跳过
    startIndex = 0  # 需要执行的step suite_no
    start_time = None  # 测试项的开始时
    TestValue = None  # 测试得到的值
    elapsedTime = None  # 测试步骤耗时
    suite_name = ''

    ItemName = None  # 当前测试step名字
    ErrorCode = None  # 测试错误码
    RetryTimes = None  # 测试失败retry次数
    TimeOut = None  # 测试步骤超时时间
    SubStr1 = None  # 截取字符串 如截取abc中的b SubStr1=a，SubStr2=c
    SubStr2 = None
    IfElse = None  # 测试步骤结果是否做为if条件，决定else步骤是否执行
    For = None  # 循环测试for(6)开始6次循环，END FOR结束
    Mode = None  # 机种，根据机种决定哪些用例不跑，哪些用例需要跑
    ComdSend = None  # 发送的测试命令
    ExpectStr = None  # 期待的提示符，用来判断反馈是不是结束了
    CheckStr1 = None  # 检查反馈是否包含CheckStr1
    CheckStr2 = None  # 检查反馈是否包含CheckStr2
    Limit_max = None  # 最小限值
    Limit_min = None  # 最大限值
    ErrorDetails = None  # 测试错误码详细描述
    unit = None  # 测试值单位
    MES_var = None  # 上传MES信息的变量名字
    ByPassFail = None  # 手动人为控制测试结果 1=pass，0||空=fail
    FTC = None  # 失败继续 fail to continue。1=继续，0||空=不继续
    TestKeyword = None  # 测试步骤对应的关键字，执行对应关键字下的代码段
    Spec = None  # 测试定义的Spec
    error_code = ""
    error_details = ""
    Json = None  # 测试结果是否生成Json数据上传给客户

    def __init__(self, isTest=True, retry_times=0):
        self.__retry_times = retry_times
        self.__isTest = isTest

    def copy_to(self, obj: phase_items):
        obj.name = self.ItemName
        obj.status = self.tResult
        obj.value = self.TestValue
        obj.unit = self.unit
        obj.spec = self.Spec
        obj.limit_min = self.Limit_min
        obj.limit_max = self.Limit_max

    def get_fail_continue(self):
        return True if self.FTC == 1 else False

    @property
    def isTest(self):
        return self.__isTest

    @property
    def retry_times(self):
        return self.__retry_times

    @property
    def test_command(self):
        return self.__test_command

    @property
    def test_spec(self):
        return self.__test_spec

    @test_spec.setter
    def test_spec(self, value):
        for a in re.findall(r'<(.*?)>', value):
            value = re.compile(f'<{a}>').sub(get_globalVal(a), value, count=1)
        self.__test_spec = value

    @test_command.setter
    def test_command(self, value):
        for a in re.findall(r'<(.*?)>', value):
            value = re.compile(f'<{a}>').sub(get_globalVal(a), value, count=1)
        self.__test_command = value

    @retry_times.setter
    def retry_times(self, value):
        if IsNullOrEmpty(value):
            self.__retry_times = 0
        else:
            self.__retry_times = int(value)

    @isTest.setter
    def isTest(self, if_cond):
        if str(self.IfElse).lower() == 'else':
            self.__isTest = not if_cond
        if not IsNullOrEmpty(self.Mode) and gv.dut_mode not in str(self.Mode).lower():
            self.__isTest = False

    def set_errorCode_details(self, result=False, *args):
        if not result:
            if len(args) == 0:
                temp = self.ErrorCode.split(':')
            else:
                temp = args[0].split(':')
            self.error_code = temp[0]
            if len(temp) == 1:
                self.error_details = temp[0].strip()
            else:
                self.error_details = temp[1].strip()

    def _process_mesVer(self):
        if not IsNullOrEmpty(self.MES_var):
            if self.TestValue is not None:
                setattr(gv.mesPhases, self.MES_var, self.TestValue)
            else:
                setattr(gv.mesPhases, self.MES_var, str(self.tResult).upper())

    def if_statement(self, test_result: bool):
        global IfCond
        if str(self.IfElse).lower() == 'if':
            IfCond = test_result
            if not test_result:
                logger.info(f"if statement fail needs to continue, setting the test result to true")
                return True
        elif str(self.IfElse).lower() == 'else':
            pass
        else:
            IfCond = True
        return test_result

    def record_first_fail(self, tResult):
        global count
        if not tResult:
            count += 1
        if count == 1 and IsNullOrEmpty(get_globalVal('error_code_first_fail')):
            set_globalVal('error_code_first_fail', self.error_code)
            set_globalVal('error_details_first_fail', self.error_details)
            setattr(gv.mesPhases, 'first_fail', self.suite_name)

    def _process_ByPassFail(self, step_result):
        if str(self.ByPassFail).upper() == 'P' and not step_result:
            logger.info(f"Let this step:{self.ItemName} bypass.")
            return True
        elif str(self.ByPassFail).upper() == 'F' and step_result:
            self.set_errorCode_details(self.ErrorCode.split('\n')[0])
            logger.error(
                f"Let this step:{self.ItemName} by fail."
                f"Set error_code:{self.error_code},error_details:{self.error_details}")
            return False
        else:
            return step_result

    def clear(self):
        self.tResult = False
        self.isTest = True
        self.startIndex = 0
        self.TestValue = None
        self.elapsedTime = None
        self.start_time = None
        self.test_command = ''
        self.test_spec = ''

    def _process_if_bypass(self, test_result: bool):
        result_if = self.if_statement(test_result)
        by_result = self._process_ByPassFail(result_if)
        self.record_first_fail(by_result)
        return by_result

    def run_step(self, testPhase: test_phases):
        phaseItem = phase_items()
        test_result = False
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            self.isTest = IfCond
            if self.isTest:
                self.test_command = self.ComdSend
                self.test_spec = self.Spec

                logger.debug(
                    f"Start step...{self.ItemName},Keyword:{self.TestKeyword},Retry:{self.RetryTimes},Timeout:"
                    f"{self.TimeOut}s,SubStr:{self.SubStr1}*{self.SubStr2},MesVer:{self.MES_var},FTC:{self.FTC}")

                self.retry_times = self.RetryTimes
                for retry in range(int(self.retry_times), -1, -1):
                    if test(retry, self):
                        test_result = True
                        break
                    else:
                        pass

                self.tResult = self._process_if_bypass(test_result)
                self._process_mesVer()

                self.collect_result()

                self.print_result()
                # 给Json格式对象赋值
                self.copy_to(phaseItem)
                testPhase.phase_items.append(phaseItem)
            else:
                logger.debug(f'skip this step:{self.ItemName}')
                return True
        except Exception as e:
            logger.exception(f"run_step Exception！！{e}")
            self.tResult = False
            return self.tResult
        else:
            return self.tResult
        finally:
            self.clear()

    def print_result(self):
        self.elapsedTime = (
                datetime.now() - datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S.%f')).microseconds
        if self.tResult:
            logger.info(
                f"{self.ItemName} {'pass' if self.tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}ms,"
                f"Symptom:{self.error_code}:{self.error_details},"
                f"Spec:{self.Spec},Min:{self.Limit_min},Value:{self.TestValue},Max:{self.Limit_max}")
        else:
            logger.error(
                f"{self.ItemName} {'pass' if self.tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}ms,"
                f"Symptom:{self.error_code}:{self.error_details},"
                f"Spec:{self.Spec},Min:{self.Limit_min},Value:{self.TestValue},Max:{self.Limit_max}")

    def collect_result(self):
        # if IsNullOrEmpty(self.Json):
        print(f'{self.Spec},{self.Limit_min},{self.Limit_max}')
        if not IsNullOrEmpty(self.Spec):
            gv.csv_list_header.extend([self.ItemName, "SPEC"])
            gv.csv_list_result.extend([self.TestValue, self.Spec])
        elif not IsNullOrEmpty(self.Limit_max) or not IsNullOrEmpty(self.Limit_min):
            gv.csv_list_header.extend([self.ItemName, "LIMIT_MIN", "LIMIT_MAX"])
            gv.csv_list_result.extend([self.TestValue, self.Limit_min, self.Limit_max])
        else:
            gv.csv_list_header.append(self.ItemName)
            gv.csv_list_result.append(self.tResult)

# def wrapper(self, flag):
#     def wrapper(func):
#         def inner(obj):
#             if flag:
#                 pass
#             result = func(obj)
#             if flag:
#                 obj.set_errorCode_details(result)
#             return result
#
#         return inner
#
#     return wrapper
