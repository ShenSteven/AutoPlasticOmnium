#!/usr/cf/env python
# coding: utf-8
"""
@File   : suite.py
@Author : Steven.Shen
@Date   : 2021/9/2
@Desc   : 
"""
import re
from datetime import datetime
import model.product
import conf.globalvar as gv
import model.step
import conf.logconf as lg


def process_EndFor(step: model.step.Step):
    if not model.IsNullOrEmpty(step.For) and str(step.For).lower().startswith('end'):
        if gv.ForTestCycle < gv.ForTotalCycle:
            gv.ForFlag = True
            gv.ForTestCycle = gv.ForTestCycle + 1
            return True
        else:
            gv.ForFlag = False
            lg.logger.debug(
                f"==================Have Complete all({gv.ForTestCycle}) Cycle test.======================")
            return False
    else:
        return False


def fail_continue(step, failContinue):
    if step.FTC.lower() == 'n' or step.FTC.lower() == '0':
        return False
    elif step.FTC.lower() == 'y' or step.FTC.lower() == '1':
        return True
    else:
        return failContinue


class TestSuite:
    SeqName: str = ""
    isTest: bool = True  # 是否测试
    isTestFinished: bool = False  # 测试完成标志
    tResult: bool = True  # 测试结果
    totalNumber: int = 0  # 测试大项item总数量
    index: int = 0  # 测试大项在所有中的序列号
    test_steps: list = []
    start_time: str = ""
    finish_time: str = ""
    error_code: str = None
    phase_details: str = None
    elapsedTime = None

    def update_from_dict(self, step_dict):
        import model.step
        for step_dict in step_dict['test_steps']:
            step_obj = model.step.Step(step_dict)
            self.test_steps.append(step_obj)

    def __init__(self, SeqName=None, test_serial=None, dict_=None):
        self.SeqName = SeqName
        self.index = test_serial
        self.test_steps = []
        if dict_ is not None:
            self.__dict__.update(dict_)

    def clear(self):
        self.isTestFinished = False
        self.tResult = True
        self.start_time = ''
        self.finish_time = ''
        self.error_code = ''
        self.phase_details = ''
        self.elapsedTime = None

    def copy_to(self, obj: model.product.SuiteItem):
        obj.phase_name = self.SeqName
        obj.status = "passed" if self.tResult else "failed"
        obj.start_time = self.start_time
        obj.finish_time = self.finish_time
        obj.error_code = self.error_code
        obj.phase_details = self.phase_details

    def process_mesVer(self):
        setattr(gv.mesPhases, self.SeqName + '_Time',
                self.elapsedTime.seconds + self.elapsedTime.microseconds / 1000000)
        if not self.tResult:
            setattr(gv.mesPhases, self.SeqName, str(self.tResult).upper())

    def run(self, global_fail_continue, stepNo=-1):
        if self.isTest:
            return True
        lg.logger.debug('- ' * 9 + f"Start testSuite:{self.SeqName}" + '- ' * 9)
        # mainWin.ui.textEdit.insertHtml(
        #     '- ' * 9 + f"<a name='testSuite:{self.SeqName}'>Start testSuite:{self.SeqName}</a>" + '- ' * 9)

        # step_result = False
        testPhase = model.product.SuiteItem()
        step_result_list = []
        self.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            for i, step in enumerate(self.test_steps):
                if stepNo != -1:
                    i = stepNo
                    stepNo = -1
                self.process_for(self.test_steps[i])

                if self.test_steps[i].isTest:
                    step_result = self.test_steps[i].run(testPhase)
                    step_result_list.append(step_result)
                else:
                    step_result = True

                if not step_result and not fail_continue(self.test_steps[i], global_fail_continue):
                    break

                if process_EndFor(self.test_steps[i]):
                    break

            self.tResult = all(step_result_list)
            self.print_result()
            self.process_mesVer()
            # self.copy_to(testPhase)  # 把seq测试结果保存到test_phase变量中.
            # gv.stationObj.SuiteItem.append(testPhase)  # 加入station实例,记录测试结果 用于序列化Json文件
        except Exception as e:
            lg.logger.exception(f"run testSuite {self.SeqName} Exception！！{e}")
            self.tResult = False
            return self.tResult
        else:
            return self.tResult
        finally:
            self.clear()

    def print_result(self):
        self.finish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.elapsedTime = datetime.strptime(self.finish_time, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(
            self.start_time, '%Y-%m-%d %H:%M:%S.%f')
        if self.tResult:
            lg.logger.info(f"{self.SeqName} Test Pass!,ElapsedTime:{self.elapsedTime}")
        else:
            lg.logger.error(f"{self.SeqName} Test Fail!,ElapsedTime:{self.elapsedTime}")

    def process_for(self, step: model.step.Step):
        if not model.IsNullOrEmpty(step.For) and '(' in step.For and ')' in step.For:
            gv.ForTestCycle = int(re.findall(f'{step.SubStr1}(.*?){step.SubStr2}', step.For)[0])
            gv.ForStartStepNo = self.index
            gv.ForStartStepNo = step.index
            gv.ForFlag = False
            lg.logger.debug(f"====================Start Cycle-{gv.ForTestCycle}===========================")


if __name__ == "__main__":
    pass
