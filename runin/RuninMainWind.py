#!/usr/bin/env python
# coding: utf-8
"""
@File   : RuninMainWind.py
@Author : Steven.Shen
@Date   : 9/2/2022
@Desc   : 
"""
from PyQt5.QtWidgets import QMainWindow, QApplication

from ui_RuninMain import Ui_MainWindow
import ui.images_rc


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        Ui_MainWindow.__init__(self)
        super().__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec_()
