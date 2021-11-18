#!/usr/cf/env python
# coding: utf-8
"""
@File   : test step.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
from datetime import datetime
import model.product
import conf.globalvar as gv
import model.test
import conf.logconf as lg

# count = 0
# IfCond = True
# setError = True


class Step:
    index = 0  # 当前测试step序列号
    tResult = False  # 测试项测试结果
    # isTest = True  # 是否测试,不测试的跳过
    # startIndex = 0  # 需要执行的step suite_no
    start_time = None  # 测试项的开始时
    finish_time = None
    error_code = ""
    error_details = ""
    testValue = None  # 测试得到的值
    elapsedTime = None  # 测试步骤耗时

    suite_name: str = ''
    ItemName: str = None  # 当前测试step名字
    ErrorCode: str = None  # 测试错误码
    RetryTimes: str = None  # 测试失败retry次数
    TimeOut: int = None  # 测试步骤超时时间
    SubStr1: str = None  # 截取字符串 如截取abc中的b SubStr1=a，SubStr2=cf
    SubStr2: str = None
    IfElse: str = None  # 测试步骤结果是否做为if条件，决定else步骤是否执行
    For: str = None  # 循环测试for(6)开始6次循环，END FOR结束
    Mode: str = None  # 机种，根据机种决定哪些用例不跑，哪些用例需要跑
    ComdOrParam: str = None  # 发送的测试命令
    ExpectStr: str = None  # 期待的提示符，用来判断反馈是不是结束了
    CheckStr1: str = None  # 检查反馈是否包含CheckStr1
    CheckStr2: str = None  # 检查反馈是否包含CheckStr2
    Limit_max: str = None  # 最小限值
    Limit_min: str = None  # 最大限值
    ErrorDetails: str = None  # 测试错误码详细描述
    Unit: str = None  # 测试值单位
    MES_var: str = None  # 上传MES信息的变量名字
    ByPassFail: str = None  # 手动人为控制测试结果 1=pass，0||空=fail
    FTC: str = None  # 失败继续 fail to continue。1=继续，0||空=不继续
    TestKeyword: str = None  # 测试步骤对应的关键字，执行对应关键字下的代码段
    Spec: str = None  # 测试定义的Spec
    Json: str = None  # 测试结果是否生成Json数据上传给客户
    EeroName: str = None  # 客户定义的测试步骤名字
    param1: str = None

    def __init__(self, dict_=None):
        self.__test_command = ''
        self.__test_spec = ''
        self.__retry_times = 0
        self.__isTest = True
        if dict_ is not None:
            self.__dict__.update(dict_)

    @property
    def isTest(self):
        if str(self.IfElse).lower() == 'else':
            self.__isTest = not gv.IfCond
        if not model.IsNullOrEmpty(self.Mode) and gv.dut_mode.lower() not in self.Mode.lower():
            self.__isTest = False
        return self.__isTest

    @isTest.setter
    def isTest(self, value):
        self.__isTest = value

    @property
    def retry_times(self):
        if model.IsNullOrEmpty(self.RetryTimes):
            self.__retry_times = 0
        else:
            self.__retry_times = int(self.RetryTimes)
        return self.__retry_times

    @property
    def test_command(self):
        return self.__test_command

    @test_command.setter
    def test_command(self, value):
        for a in re.findall(r'<(.*?)>', value):
            value = re.compile(f'<{a}>').sub(gv.get_globalVal(a), value, count=1)
        self.__test_command = value

    @property
    def test_spec(self):
        return self.__test_spec

    @test_spec.setter
    def test_spec(self, value):
        for a in re.findall(r'<(.*?)>', value):
            value = re.compile(f'<{a}>').sub(gv.get_globalVal(a), value, count=1)
        self.__test_spec = value

    def run(self, testPhase: model.product.SuiteItem = None):

        info = ''
        test_result = False
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            if self.isTest:
                lg.logger.debug(
                    f"Start step...{self.ItemName},Keyword:{self.TestKeyword},Retry:{self.RetryTimes},Timeout:"
                    f"{self.TimeOut}s,SubStr:{self.SubStr1}*{self.SubStr2},MesVer:{self.MES_var},FTC:{self.FTC}")
                self.test_command = self.ComdOrParam
                self.test_spec = self.Spec
            else:
                return True

            for retry in range(self.retry_times, -1, -1):
                test_result, info = model.test.test(self)
                if test_result:
                    break

            self.print_result(test_result)
            self.tResult = self.process_if_bypass(test_result)
            self.set_errorCode_details(self.tResult, info)
            self.record_first_fail(self.tResult)
            self.Process_json(testPhase, test_result)
            self.process_mesVer()

        except Exception as e:
            lg.logger.exception(f"run Exception！！{e}")
            self.tResult = False
            return self.tResult
        else:
            return self.tResult
        finally:
            self.clear()

    def set_errorCode_details(self, result=False, info=''):
        if not result:
            if model.IsNullOrEmpty(self.ErrorCode):
                self.error_code = self.EeroName
                self.error_details = self.EeroName
            elif ':' in self.ErrorCode:
                error_list = self.ErrorCode.split()
                # lg.logger.debug(f'ErrorList.length {len(error_list)},{error_list[0]}')
                if len(error_list) > 1 and info == 'TooHigh':
                    self.error_code = error_list[1].split(':')[0].strip()
                    self.error_details = error_list[1].split(':')[1].strip()
                else:
                    self.error_code = error_list[0].split(':')[0].strip()
                    self.error_details = error_list[0].split(':')[1].strip()
            else:
                self.error_code = self.ErrorCode
                self.error_details = self.ErrorCode

    def process_mesVer(self):
        if not model.IsNullOrEmpty(self.MES_var) and self.testValue is not None and str(
                self.testValue).lower() != 'true':
            setattr(gv.mesPhases, self.MES_var, self.testValue)

    def if_statement(self, test_result: bool):
        if self.IfElse.lower() == 'if':
            gv.IfCond = test_result
            if not test_result:
                lg.logger.info(f"if statement fail needs to continue, setting the test result to true")
                test_result = True
        elif self.IfElse.lower() == 'else':
            pass
        else:
            gv.IfCond = True
        return test_result

    def record_first_fail(self, tResult):
        if not tResult:
            gv.failCount += 1
        else:
            return
        if gv.failCount == 1 and model.IsNullOrEmpty(gv.error_code_first_fail):
            gv.error_code_first_fail = self.error_code
            gv.error_details_first_fail = self.error_details
            gv.mesPhases.first_fail = self.suite_name

    def process_ByPassFail(self, step_result):
        if (str(self.ByPassFail).upper() == 'P' or str(self.ByPassFail).upper() == '1') and not step_result:
            lg.logger.info(f"Let this step:{self.ItemName} bypass.")
            return True
        elif (str(self.ByPassFail).upper() == 'F' or str(self.ByPassFail).upper() == '0') and step_result:
            lg.logger.error(f"Let this step:{self.ItemName} by fail.")
            return False
        else:
            return step_result

    def clear(self):
        self.tResult = False
        self.error_code = None
        self.error_details = None
        if not gv.IsDebug:
            self.isTest = True
        self.testValue = None
        self.elapsedTime = None
        self.start_time = None
        self.finish_time = None
        self.test_command = ''
        self.test_spec = ''

    def process_if_bypass(self, test_result: bool):
        result_if = self.if_statement(test_result)
        by_result = self.process_ByPassFail(result_if)
        return by_result

    def print_result(self, test_result):
        self.elapsedTime = (
                datetime.now() - datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S.%f')).microseconds
        if self.TestKeyword == 'Wait' and self.TestKeyword == 'ThreadSleep':
            return
        if self.tResult:
            lg.logger.info(
                f"{self.ItemName} {'pass' if self.tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}ms,"
                f"Symptom:{self.error_code}:{self.error_details},"
                f"Spec:{self.Spec},Min:{self.Limit_min},Value:{self.testValue},Max:{self.Limit_max}")
        else:
            lg.logger.error(
                f"{self.ItemName} {'pass' if self.tResult else 'fail'}!! ElapsedTime:{self.elapsedTime}ms,"
                f"Symptom:{self.error_code}:{self.error_details},"
                f"Spec:{self.Spec},Min:{self.Limit_min},Value:{self.testValue},Max:{self.Limit_max}")

    def collect_result(self):
        if not model.IsNullOrEmpty(self.Limit_max) or not model.IsNullOrEmpty(self.Limit_min):
            gv.csv_list_header.extend([self.EeroName, "_LIMIT_MIN", "_LIMIT_MAX"])
            gv.csv_list_result.extend([self.testValue, self.Limit_min, self.Limit_max])
        elif not model.IsNullOrEmpty(self.Spec):
            gv.csv_list_header.extend([self.EeroName, "_SPEC"])
            gv.csv_list_result.extend([self.testValue, self.Spec])
        else:
            gv.csv_list_header.append(self.EeroName)
            gv.csv_list_result.append(self.tResult)

    def copy_to(self, obj: model.product.StepItem):
        if self.EeroName.endswith('_'):
            obj.test_name = self.EeroName + str(gv.ForTestCycle)
        else:
            obj.test_name = self.EeroName
        obj.status = self.tResult
        obj.test_value = self.testValue
        obj.units = self.Unit
        obj.error_code = self.error_code
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.lower_limit = self.Limit_min
        obj.upper_limit = self.Limit_max
        if not model.IsNullOrEmpty(
                self.Spec) and '<' not in self.Spec and '>' not in self.Spec and not model.IsNullOrEmpty(self.Limit_min):
            obj.lower_limit = self.Spec

        gv.stationObj.tests.appand(obj)
        self.collect_result()

    def Process_json(self, testPhase: model.product.SuiteItem, test_result):

        if self.Json is not None and self.Json.lower() == 'y':
            if self.IfElse.lower() == 'if' and not test_result:
                pass
            else:
                self.JsonAndCsv(testPhase, test_result)
        elif not test_result:
            self.JsonAndCsv(testPhase, test_result)

    def JsonAndCsv(self, testPhase: model.product.SuiteItem, test_result):
        obj = model.product.StepItem()
        if self.ByPassFail.lower() == 'f':
            self.tResult = False
        elif self.ByPassFail.lower() == 'p':
            self.tResult = True
        else:
            self.tResult = test_result

        if self.testValue is None:
            self.testValue = str(test_result)

        self.copy_to(obj)
        if testPhase is not None:
            testPhase.phase_items.append(obj)


if __name__ == "__main__":
    pass
