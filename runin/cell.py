#!/usr/bin/env python
# coding: utf-8
"""
@File   : cell.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
from PyQt5.QtWidgets import QApplication, QFrame

from runin.ui_cell import Ui_testcell


class cell(QFrame, Ui_testcell):

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        Ui_testcell.__init__(self)
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication([])
    mainWin = cell()
    mainWin.show()
    app.exec_()
