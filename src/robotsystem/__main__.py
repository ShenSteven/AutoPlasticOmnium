#!/usr/bin/env python
# coding: utf-8
"""
@File   : __main__.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""

import os
import sys
from os.path import abspath, join, dirname
from PyQt5.QtWidgets import QApplication, QMessageBox
import robotsystem.ui.mainform as mf
from traceback import format_exception
import robotsystem.conf.logprint as lg


def excepthook(cls, exception, traceback):
    lg.logger.exception(format_exception(cls, exception, traceback))
    QMessageBox.critical(None, "Error", "".join(format_exception(cls, exception, traceback)))


def main():
    sys.excepthook = excepthook
    app = QApplication([])
    print("applicationDirPath:", app.applicationDirPath())
    mainWin = mf.MainForm()
    mainWin.ui.show()
    try:
        app.exec_()
    except KeyboardInterrupt:
        lg.logger.exception('KeyboardInterrupt')
        pass


if __name__ == "__main__":
    main()
