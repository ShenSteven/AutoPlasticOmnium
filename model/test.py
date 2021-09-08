#!/usr/bin/env python
# coding: utf-8
"""
@File   : test.py
@Author : Steven.Shen
@Date   : 2021/9/6
@Desc   : Test the code block corresponding to the keyword
"""
import math
import re
import time

from bin.basefunc import IsNullOrEmpty
from bin.globalconf import logger
# from bin.main import comm
# from model.step import TestStep


# def CheckSpec(spec, testValue):
#     if spec.Contains("{") and spec.Contains("}") and testValue in spec:  # Spec值有多种情况,属于包含关系
#         logger.debug("check Spec contain pass")
#         return True
#     elif testValue == spec:  # Spec值只有一种,检查 ==
#         logger.debug("check Spec == pass")
#         return True
#     else:
#         return False

def CheckSpec(spec, testValue):
    if testValue in spec:  # Spec值有多种情况,属于包含关系
        logger.debug("check Spec contain pass")
        return True
    else:
        return False


def CompareLimit(limitMin, limitMax, value, is_round=False):
    if IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):
        return True
    if IsNullOrEmpty(value):
        return False
    temp = round(float(value)) if is_round else float(value)
    if IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 只需比较最大值
        logger.debug("Compare Limit_max...")
        return temp <= float(limitMax)
    if not IsNullOrEmpty(limitMin) and IsNullOrEmpty(limitMax):  # 只需比较最小值
        logger.debug("Compare Limit_min...")
        return temp >= float(limitMin)
    if not IsNullOrEmpty(limitMin) and not IsNullOrEmpty(limitMax):  # 比较最小最大值
        logger.debug("Compare Limit_min and Limit_max...")
        if float(limitMin) <= temp <= float(limitMax):
            return True
        else:
            if temp < float(limitMin):
                return False, 'TooLow'
            else:
                return False, 'TooHigh'


def test(retry_time, item):
    rReturn = False
    compInfo = ''
    try:
        if item.TestKeyword == 'Sleep':
            time.sleep(item.TimeOut)
            rReturn = True
        elif item.TestKeyword == '':
            rReturn = True
        else:
            logger.debug('run test step')
            pass
            # rReturn, revStr = comm.SendCommand(item.ComdSend, item.ExpectStr, item.TimeOut)
            # if rReturn:
            #     if re.search(item.CheckStr1, revStr) and re.search(item.CheckStr2, revStr):
            #         rReturn = True
            #
            #         if not IsNullOrEmpty(item.SubStr1) or not IsNullOrEmpty(item.SubStr2):
            #             values = re.findall(f'{item.SubStr1}(.*?){item.SubStr2}', revStr)
            #             if len(values) == 1:
            #                 item.TestValue = values[0]
            #                 logger.debug(f'get TestValue:{item.TestValue}')
            #             else:
            #                 raise Exception(f'get TestValue exception:{values}')
            #
            #             if not IsNullOrEmpty(item.Spec):
            #                 rReturn = CheckSpec(item.Spec, item.TestValue)
            #             if not IsNullOrEmpty(item.Limit_min) or not IsNullOrEmpty(item.Limit_max):
            #                 rReturn, compInfo = CompareLimit(item.Limit_min, item.Limit_max, item.TestValue)
            #     else:
            #         rReturn = False
            # else:
            #     pass

    except Exception as e:
        logger.exception(f"test Exception！！{e}")
        rReturn = False
        return rReturn
    else:
        return rReturn
    finally:
        item.set_errorCode_details(rReturn, item.ErrorCode.split('\n')[0])
        pass
