#!/usr/cf/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2021/9/3
@Desc   : 
"""

from PySide2.QtWidgets import QApplication
import ui.mainform

# import model.loadseq
# import model.testcase

# def test_thread():
#     try:
#         while True:
#             if gv.StartFlag:
#                 if gv.IsCycle:
#                     while True:
#                         if testcase.run(gv.cf.station.fail_continue):
#                             gv.PassNumOfCycleTest += 1
#                         else:
#                             gv.FailNumOfCycleTest += 1
#                 elif gv.SingleStepTest:
#                     testcase.clone_suites[gv.SuiteNo].steps[gv.StepNo].run()
#                     gv.StartFlag = False
#                 else:
#                     result = testcase.run(gv.cf.station.fail_continue)
#                     final_result = upload_Json_to_client() & upload_result_to_mes() & result
#                     gv.finalTestResult = final_result
#                     set_test_status()
#                     collectCsvResult()
#                     saveTestResult()
#                     write_csv_file('result.csv', gv.csv_list_result)
#                     write_csv_file('result.csv', gv.csv_list_header)
#     except:
#         pass
#     else:
#         pass
#     finally:
#         pass
#     # test_task = model.testcase.TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')
#     #
#     # if is_cyclic:
#     #     while True:
#     #         test_task.run(test_task.original_suites.copy(), True, 0)
#     # elif single_step:
#     #     test_task.original_suites.copy()[0].test_steps[2].run()
#     # else:
#     #     create_csv_file('result.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
#     #     test_task.run(test_task.original_suites.copy(), True)
#     #     print(gv.csv_list_result)
#     #     write_csv_file('result.csv', gv.csv_list_result)
#     #     write_csv_file('result.csv', gv.csv_list_header)
#
#
# # run(False)
#
# # print(time.strftime("%Y-%m-%d %H:%M:%S"))
# #
# #
# def upload_result_to_mes(url):
#     logger.debug(json.dumps(gv.mesPhases, default=lambda o: o.__dict__,
#                             sort_keys=True,
#                             indent=4))
#     response = requests.post(url, logger.debug(json.dumps(gv.mesPhases, default=lambda o: o.__dict__,
#                                                           sort_keys=True,
#                                                           indent=4)))
#     if response.status_code == 200:
#         return True
#     else:
#         logger.debug(f'post fail:{response.content}')
#         return False
import conf.logconf as lg

if __name__ == "__main__":
    app = QApplication([])
    mainWin = ui.mainform.MainForm()
    mainWin.ui.show()
    lg.logger.debug("test qtextEdit debug")
    lg.logger.info("test qtextEdit info")
    lg.logger.error("eero")
    lg.logger.critical('fate,except')
    lg.logger.warning('warning')
    app.exec_()
