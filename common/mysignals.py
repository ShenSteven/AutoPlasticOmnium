#!/usr/bin/env python
# coding: utf-8
"""
@File   : mysignals.py
@Author : Steven.Shen
@Date   : 1/11/2023
@Desc   : 
"""
import os
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QLabel, QAction, QApplication, QMessageBox


class MySignals(QObject):
    """自定义信号类"""
    loadSeq = pyqtSignal(str)
    update_tableWidget = pyqtSignal((list,), (str,))
    updateLabel = pyqtSignal([QLabel, str, int, QBrush], [QLabel, str])
    treeWidgetColor = pyqtSignal([QBrush, int, int, bool])
    timingSignal = pyqtSignal(bool)
    textEditClearSignal = pyqtSignal()
    lineEditEnableSignal = pyqtSignal(bool)
    setIconSignal = pyqtSignal(QAction, QIcon)
    updateStatusBarSignal = pyqtSignal(str)
    saveTextEditSignal = pyqtSignal(str)
    controlEnableSignal = pyqtSignal(QAction, bool)
    threadStopSignal = pyqtSignal(str)
    updateConnectStatusSignal = pyqtSignal(bool, str)
    showMessageBox = pyqtSignal(str, str, int)
    updateProgressBar = pyqtSignal([int], [int, int])
    play_audio = pyqtSignal(str)


def update_label(label: QLabel, str_: str, font_size: int = 36, color: QBrush = None):
    label.setText(str_)
    if color is not None:
        label.setStyleSheet(f"background-color:{color.color().name()};font: {font_size}pt '宋体';")
    QApplication.processEvents()


def on_actOpenFile(filePath: str):
    def thread_update():
        if os.path.exists(filePath):
            os.startfile(filePath)
            # QDesktopServices.openUrl(QUrl(f'file:///{ensure_path_sep(self.txtLogPath)}'))
        else:
            # self.logger.warning(f"File not found! path:{filePath}")
            QMessageBox.information(None, 'Information', f"File not found! path:{filePath}", QMessageBox.Yes)

    thread = Thread(target=thread_update, daemon=True)
    thread.start()
