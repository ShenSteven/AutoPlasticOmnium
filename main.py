#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""
import sys
from os.path import dirname, abspath
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMessageBox
import ui.mainform as mf
from os.path import dirname, abspath, join
from PyQt5.uic import loadUi
import runin.rmainform as rmf

# get app dir path
bundle_dir = ''


# runinMainWin = None
# loginWin = None


class LoginWind:
    def __init__(self):
        self.ui = loadUi(join(dirname(abspath(__file__)), 'runin/ui_login.ui'))
        self.ui.lineEdit.returnPressed.connect(self.onSignIn)

    def onSignIn(self):
        # ScanfixName = self.ui.lineEdit.Text.trim()
        # self.FixtureNumber = ScanfixName[0:10]
        runinMainWin = rmf.RuninMainForm()
        runinMainWin.ui.show()
        self.ui.hide()


def get_about(about_abspath):
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), about_abspath), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


def get_app_dir_path():
    global bundle_dir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('running in a PyInstaller bundle')
        bundle_dir = sys._MEIPASS
    else:
        print('running in a normal Python process')
        bundle_dir = dirname(abspath(__file__))
    print(bundle_dir)


get_app_dir_path()


def excepthook(cls, exception, traceback):
    import conf.logprint as lg
    lg.logger.fatal("".join(format_exception(cls, exception, traceback)))
    QMessageBox.critical(None, "Error", "".join(format_exception(cls, exception, traceback)))


def main():
    sys.excepthook = excepthook
    app = QApplication([])
    print("applicationDirPath:", app.applicationDirPath())
    about_abspath = 'conf/__version__.py'
    if get_about(about_abspath)['__station__'] == 'RUNIN' or get_about(about_abspath)['__station__'] == 'ORT':
        loginWin = LoginWind()
        loginWin.ui.show()
    else:
        mainWin = mf.MainForm()
        mainWin.ui.show()
    try:
        app.exec_()
    except KeyboardInterrupt:
        import conf.logprint as lg
        lg.logger.fatal('KeyboardInterrupt')
        pass


if __name__ == "__main__":
    main()
