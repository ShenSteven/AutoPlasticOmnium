#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
import threading

from PyQt5.QtWidgets import QApplication, QFrame

from runin.ui_cell import Ui_cell


class Cell(QFrame, Ui_cell):
    # main_form = None
    # _lock = threading.RLock()
    #
    # def __new__(cls, *args, **kwargs):
    #
    #     if cls.main_form:  # 如果已经有单例了就不再去抢锁，避免IO等待
    #         return cls.main_form
    #     with cls._lock:  # 使用with语法，方便抢锁释放锁
    #         if not cls.main_form:
    #             cls.main_form = super().__new__(cls, *args, **kwargs)
    #         return cls.main_form

    def __init__(self, parent=None, row=-1, col=-1, testcase=None):
        QFrame.__init__(self, parent)
        Ui_cell.__init__(self)
        self.setupUi(self)
        self.row_index = row
        self.col_index = col
        self.testcase = testcase
        self.sequences = []
        self.CellLogTxt = ''
        self.rs_url = ''
        self.mes_result = ''
        self.logger = None
        self.StartFlag = False
        self.init_cell()

    def init_cell(self):
        self.lb_cellNum.setText('')
        self.lb_sn.setText('')
        self.lb_model.setText('')
        self.lb_testTime.setText('')
        self.lbl_failCount.setText('')
        self.lb_testName.setText(f'{self.row_index}-{self.col_index}')

    def startTest(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    mainWin = Cell()
    mainWin.show()
    app.exec_()
