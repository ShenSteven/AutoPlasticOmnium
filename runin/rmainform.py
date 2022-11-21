#!/usr/bin/env python
# coding: utf-8
"""
@File   : rmainform.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
from PyQt5.QtWidgets import QMainWindow, QApplication
from os.path import dirname, abspath, join
# from ui_runin import Ui_RuninMain
# import ui_runin

# from PyQt5.uic import loadUi
# import ui.images_rc
from runin.ui_runin import Ui_RuninMain


class RuninMainForm(QMainWindow, Ui_RuninMain):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        Ui_RuninMain.__init__(self)
        super().__init__(parent)
        self.setupUi(self)


# class RuninMainWind:
#
#     def __init__(self):
#         self.ui = loadUi(join(dirname(abspath(__file__)), 'ui_runin.ui'))


if __name__ == "__main__":
    app = QApplication([])
    # LoginWin = LoginWind()
    # LoginWin.ui.show()
    mainWin = RuninMainForm()
    mainWin.show()
    app.exec_()
