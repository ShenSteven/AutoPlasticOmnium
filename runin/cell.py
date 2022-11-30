#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
from PyQt5.QtWidgets import QApplication, QFrame

from runin.ui_cell import Ui_cell


class Cell(QFrame, Ui_cell):

    def __init__(self, parent=None, row=-1, col=-1):
        QFrame.__init__(self, parent)
        Ui_cell.__init__(self)
        self.setupUi(self)
        self.row_index = row
        self.col_index = col
        self.init_cell()

    def init_cell(self):
        self.lb_cellNum.setText('')
        self.lb_sn.setText('')
        self.lb_model.setText('')
        self.lb_testTime.setText('')
        self.lbl_failCount.setText('')
        self.lb_testName.setText(f'{self.row_index}-{self.col_index}')


if __name__ == "__main__":
    app = QApplication([])
    mainWin = Cell()
    mainWin.show()
    app.exec_()
