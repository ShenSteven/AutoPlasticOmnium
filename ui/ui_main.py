# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1448, 857)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1448, 857))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/PO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolTip("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(1, 1, 1, 1)
        self.formLayout.setSpacing(1)
        self.formLayout.setObjectName("formLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.treeWidget = QtWidgets.QTreeWidget(self.widget)
        self.treeWidget.setMinimumSize(QtCore.QSize(330, 450))
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.horizontalLayout_2.addWidget(self.treeWidget)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.widget)
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_7.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_7.setSpacing(1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.tabWidget = QtWidgets.QTabWidget(self.widget_2)
        self.tabWidget.setObjectName("tabWidget")
        self.result = QtWidgets.QWidget()
        self.result.setObjectName("result")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.result)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tableViewRet = QtWidgets.QTableView(self.result)
        self.tableViewRet.setObjectName("tableViewRet")
        self.horizontalLayout_5.addWidget(self.tableViewRet)
        self.tabWidget.addTab(self.result, "")
        self.stepInfo = QtWidgets.QWidget()
        self.stepInfo.setObjectName("stepInfo")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.stepInfo)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.tableViewStepProp = QtWidgets.QTableView(self.stepInfo)
        self.tableViewStepProp.setObjectName("tableViewStepProp")
        self.horizontalLayout_6.addWidget(self.tableViewStepProp)
        self.tabWidget.addTab(self.stepInfo, "")
        self.variables = QtWidgets.QWidget()
        self.variables.setObjectName("variables")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.variables)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.tableViewVar = QtWidgets.QTableView(self.variables)
        self.tableViewVar.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableViewVar.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewVar.setObjectName("tableViewVar")
        self.horizontalLayout_9.addWidget(self.tableViewVar)
        self.tabWidget.addTab(self.variables, "")
        self.Chart = QtWidgets.QWidget()
        self.Chart.setObjectName("Chart")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.Chart)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.widget_5 = QtWidgets.QWidget(self.Chart)
        self.widget_5.setStyleSheet("background-color: rgb(248, 248, 248);")
        self.widget_5.setObjectName("widget_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pBt_start = QtWidgets.QPushButton(self.widget_5)
        self.pBt_start.setObjectName("pBt_start")
        self.verticalLayout_3.addWidget(self.pBt_start)
        self.pBt_stop = QtWidgets.QPushButton(self.widget_5)
        self.pBt_stop.setObjectName("pBt_stop")
        self.verticalLayout_3.addWidget(self.pBt_stop)
        self.horizontalLayout_8.addWidget(self.widget_5)
        self.graphicsView = QtWidgets.QGraphicsView(self.Chart)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout_8.addWidget(self.graphicsView)
        self.tabWidget.addTab(self.Chart, "")
        self.video = QtWidgets.QWidget()
        self.video.setEnabled(False)
        self.video.setObjectName("video")
        self.layoutWidget = QtWidgets.QWidget(self.video)
        self.layoutWidget.setGeometry(QtCore.QRect(2, 3, 431, 411))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lb_video = QtWidgets.QLabel(self.layoutWidget)
        self.lb_video.setMinimumSize(QtCore.QSize(200, 200))
        self.lb_video.setObjectName("lb_video")
        self.verticalLayout_2.addWidget(self.lb_video)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(50)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.bt_photo = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_photo.sizePolicy().hasHeightForWidth())
        self.bt_photo.setSizePolicy(sizePolicy)
        self.bt_photo.setObjectName("bt_photo")
        self.horizontalLayout_4.addWidget(self.bt_photo)
        self.bt_video = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bt_video.sizePolicy().hasHeightForWidth())
        self.bt_video.setSizePolicy(sizePolicy)
        self.bt_video.setObjectName("bt_video")
        self.horizontalLayout_4.addWidget(self.bt_video)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.setStretch(0, 95)
        self.verticalLayout_2.setStretch(1, 5)
        self.tabWidget.addTab(self.video, "")
        self.horizontalLayout_7.addWidget(self.tabWidget)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.widget_2)
        self.widget_3 = QtWidgets.QWidget(self.centralwidget)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lb_status = QtWidgets.QLabel(self.widget_3)
        self.lb_status.setStyleSheet("background-color: rgb(198, 198, 198);\n"
"font: 36pt \"宋体\";")
        self.lb_status.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_status.setObjectName("lb_status")
        self.verticalLayout.addWidget(self.lb_status)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(20, -1, -1, -1)
        self.horizontalLayout.setSpacing(22)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget_3)
        self.label.setStyleSheet("font: 75 12pt \"Agency FB\";\n"
"font: 75 12pt \"Arial\";\n"
"")
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self.widget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(254, 30))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lb_errorCode = QtWidgets.QLabel(self.widget_3)
        self.lb_errorCode.setStyleSheet("background-color: rgb(198, 198, 198);\n"
"font: 20pt \"宋体\";")
        self.lb_errorCode.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_errorCode.setObjectName("lb_errorCode")
        self.verticalLayout.addWidget(self.lb_errorCode)
        self.verticalLayout.setStretch(0, 40)
        self.verticalLayout.setStretch(1, 20)
        self.verticalLayout.setStretch(2, 40)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.widget_3)
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setContentsMargins(1, 1, 4, 1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.textEdit = QtWidgets.QTextEdit(self.widget_4)
        self.textEdit.setStyleSheet("font: 9pt \"宋体\";")
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlaceholderText("")
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_3.addWidget(self.textEdit)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.widget_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1448, 26))
        self.menubar.setObjectName("menubar")
        self.testcase = QtWidgets.QMenu(self.menubar)
        self.testcase.setObjectName("testcase")
        self.menuSelect_Station = QtWidgets.QMenu(self.testcase)
        self.menuSelect_Station.setObjectName("menuSelect_Station")
        self.settings = QtWidgets.QMenu(self.menubar)
        self.settings.setObjectName("settings")
        self.help = QtWidgets.QMenu(self.menubar)
        self.help.setObjectName("help")
        self.tools = QtWidgets.QMenu(self.menubar)
        self.tools.setObjectName("tools")
        self.debug = QtWidgets.QMenu(self.menubar)
        self.debug.setObjectName("debug")
        self.menuLog = QtWidgets.QMenu(self.menubar)
        self.menuLog.setObjectName("menuLog")
        self.menuTestCase = QtWidgets.QMenu(self.menubar)
        self.menuTestCase.setObjectName("menuTestCase")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setEnabled(True)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionOpenScript = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/Open-file-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenScript.setIcon(icon1)
        self.actionOpenScript.setObjectName("actionOpenScript")
        self.actionConfig = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/Settings-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConfig.setIcon(icon2)
        self.actionConfig.setObjectName("actionConfig")
        self.actionReloadScript = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/reload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionReloadScript.setIcon(icon3)
        self.actionReloadScript.setObjectName("actionReloadScript")
        self.actionSaveToScript = QtWidgets.QAction(MainWindow)
        self.actionSaveToScript.setEnabled(False)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/Other-Save-Metro-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSaveToScript.setIcon(icon4)
        self.actionSaveToScript.setObjectName("actionSaveToScript")
        self.actionStart = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/images/Start-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStart.setIcon(icon5)
        self.actionStart.setObjectName("actionStart")
        self.actionStop = QtWidgets.QAction(MainWindow)
        self.actionStop.setEnabled(False)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/images/Stop-red-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStop.setIcon(icon6)
        self.actionStop.setObjectName("actionStop")
        self.actionSaveLog = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSaveLog.setIcon(icon7)
        self.actionSaveLog.setObjectName("actionSaveLog")
        self.actionOpenLog = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/images/File-Open-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenLog.setIcon(icon8)
        self.actionOpenLog.setObjectName("actionOpenLog")
        self.actionException = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/images/log-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionException.setIcon(icon9)
        self.actionException.setObjectName("actionException")
        self.actionLogFolder = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/images/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLogFolder.setIcon(icon10)
        self.actionLogFolder.setObjectName("actionLogFolder")
        self.actionCSVLog = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/images/csv-file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCSVLog.setIcon(icon11)
        self.actionCSVLog.setObjectName("actionCSVLog")
        self.actionResultLog = QtWidgets.QAction(MainWindow)
        self.actionResultLog.setObjectName("actionResultLog")
        self.actionPrivileges = QtWidgets.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/images/lab-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPrivileges.setIcon(icon12)
        self.actionPrivileges.setObjectName("actionPrivileges")
        self.actionHelper = QtWidgets.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/images/Folders-OS-Help-Metro-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHelper.setIcon(icon13)
        self.actionHelper.setObjectName("actionHelper")
        self.actionCheckAll = QtWidgets.QAction(MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/images/check-all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCheckAll.setIcon(icon14)
        self.actionCheckAll.setObjectName("actionCheckAll")
        self.actionUncheckAll = QtWidgets.QAction(MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/images/uncheck-all.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUncheckAll.setIcon(icon15)
        self.actionUncheckAll.setObjectName("actionUncheckAll")
        self.actionStepping = QtWidgets.QAction(MainWindow)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/images/RunSingle.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStepping.setIcon(icon16)
        self.actionStepping.setObjectName("actionStepping")
        self.actionLooping = QtWidgets.QAction(MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/images/loop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLooping.setIcon(icon17)
        self.actionLooping.setObjectName("actionLooping")
        self.actionEditStep = QtWidgets.QAction(MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/images/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEditStep.setIcon(icon18)
        self.actionEditStep.setObjectName("actionEditStep")
        self.actionClearLog = QtWidgets.QAction(MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(":/images/clear-log.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClearLog.setIcon(icon19)
        self.actionClearLog.setObjectName("actionClearLog")
        self.actionOpen_TestCase = QtWidgets.QAction(MainWindow)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(":/images/microsoft-excel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen_TestCase.setIcon(icon20)
        self.actionOpen_TestCase.setObjectName("actionOpen_TestCase")
        self.actionConvertExcelToJson = QtWidgets.QAction(MainWindow)
        self.actionConvertExcelToJson.setEnabled(True)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(":/images/blue-document-convert-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConvertExcelToJson.setIcon(icon21)
        self.actionConvertExcelToJson.setObjectName("actionConvertExcelToJson")
        self.actionUpdates = QtWidgets.QAction(MainWindow)
        self.actionUpdates.setObjectName("actionUpdates")
        self.actionFeedback = QtWidgets.QAction(MainWindow)
        self.actionFeedback.setObjectName("actionFeedback")
        self.actionPause = QtWidgets.QAction(MainWindow)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(":/images/Pause-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPause.setIcon(icon22)
        self.actionPause.setObjectName("actionPause")
        self.actionunknow = QtWidgets.QAction(MainWindow)
        self.actionunknow.setObjectName("actionunknow")
        self.actionMode = QtWidgets.QAction(MainWindow)
        self.actionMode.setEnabled(False)
        self.actionMode.setObjectName("actionMode")
        self.actionTestMode = QtWidgets.QAction(MainWindow)
        self.actionTestMode.setEnabled(False)
        self.actionTestMode.setObjectName("actionTestMode")
        self.actionproduction = QtWidgets.QAction(MainWindow)
        self.actionproduction.setObjectName("actionproduction")
        self.actionLocal_IP = QtWidgets.QAction(MainWindow)
        self.actionLocal_IP.setCheckable(False)
        self.actionLocal_IP.setEnabled(False)
        self.actionLocal_IP.setObjectName("actionLocal_IP")
        self.action192_168_1_101 = QtWidgets.QAction(MainWindow)
        self.action192_168_1_101.setObjectName("action192_168_1_101")
        self.actionRestart = QtWidgets.QAction(MainWindow)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap(":/images/restart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRestart.setIcon(icon23)
        self.actionRestart.setObjectName("actionRestart")
        self.actionExpandAll = QtWidgets.QAction(MainWindow)
        icon24 = QtGui.QIcon()
        icon24.addPixmap(QtGui.QPixmap(":/images/ExpandAll.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExpandAll.setIcon(icon24)
        self.actionExpandAll.setObjectName("actionExpandAll")
        self.actionCollapseAll = QtWidgets.QAction(MainWindow)
        icon25 = QtGui.QIcon()
        icon25.addPixmap(QtGui.QPixmap(":/images/CollapseAll.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCollapseAll.setIcon(icon25)
        self.actionCollapseAll.setObjectName("actionCollapseAll")
        self.actionEnable_lab = QtWidgets.QAction(MainWindow)
        self.actionEnable_lab.setIcon(icon12)
        self.actionEnable_lab.setObjectName("actionEnable_lab")
        self.actionDisable_factory = QtWidgets.QAction(MainWindow)
        icon26 = QtGui.QIcon()
        icon26.addPixmap(QtGui.QPixmap(":/images/factory.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDisable_factory.setIcon(icon26)
        self.actionDisable_factory.setObjectName("actionDisable_factory")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionBreakpoint = QtWidgets.QAction(MainWindow)
        icon27 = QtGui.QIcon()
        icon27.addPixmap(QtGui.QPixmap(":/images/StepBreakpoint.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBreakpoint.setIcon(icon27)
        self.actionBreakpoint.setObjectName("actionBreakpoint")
        self.actionMBLT = QtWidgets.QAction(MainWindow)
        self.actionMBLT.setObjectName("actionMBLT")
        self.actionPeakLin = QtWidgets.QAction(MainWindow)
        self.actionPeakLin.setObjectName("actionPeakLin")
        self.actionDelete = QtWidgets.QAction(MainWindow)
        self.actionDelete.setObjectName("actionDelete")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        icon28 = QtGui.QIcon()
        icon28.addPixmap(QtGui.QPixmap(":/images/edit_copy.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon28)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setEnabled(False)
        icon29 = QtGui.QIcon()
        icon29.addPixmap(QtGui.QPixmap(":/images/edit_paste.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon29)
        self.actionPaste.setObjectName("actionPaste")
        self.actionNewSeq = QtWidgets.QAction(MainWindow)
        self.actionNewSeq.setObjectName("actionNewSeq")
        self.actionNewStep = QtWidgets.QAction(MainWindow)
        self.actionNewStep.setObjectName("actionNewStep")
        self.actionCutStep = QtWidgets.QAction(MainWindow)
        icon30 = QtGui.QIcon()
        icon30.addPixmap(QtGui.QPixmap(":/images/edit_cut.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCutStep.setIcon(icon30)
        self.actionCutStep.setObjectName("actionCutStep")
        self.testcase.addAction(self.actionOpenScript)
        self.testcase.addAction(self.actionSaveToScript)
        self.testcase.addAction(self.actionReloadScript)
        self.testcase.addSeparator()
        self.testcase.addAction(self.menuSelect_Station.menuAction())
        self.settings.addAction(self.actionConfig)
        self.help.addAction(self.actionHelper)
        self.help.addAction(self.actionUpdates)
        self.help.addAction(self.actionFeedback)
        self.help.addAction(self.actionAbout)
        self.tools.addAction(self.actionPeakLin)
        self.debug.addSeparator()
        self.debug.addAction(self.actionEnable_lab)
        self.debug.addAction(self.actionDisable_factory)
        self.menuLog.addAction(self.actionSaveLog)
        self.menuLog.addAction(self.actionOpenLog)
        self.menuLog.addAction(self.actionClearLog)
        self.menuLog.addSeparator()
        self.menuLog.addAction(self.actionException)
        self.menuLog.addAction(self.actionLogFolder)
        self.menuLog.addAction(self.actionCSVLog)
        self.menuTestCase.addAction(self.actionNewSeq)
        self.menuTestCase.addSeparator()
        self.menuTestCase.addAction(self.actionOpen_TestCase)
        self.menuTestCase.addAction(self.actionConvertExcelToJson)
        self.menubar.addAction(self.menuTestCase.menuAction())
        self.menubar.addAction(self.testcase.menuAction())
        self.menubar.addAction(self.settings.menuAction())
        self.menubar.addAction(self.debug.menuAction())
        self.menubar.addAction(self.tools.menuAction())
        self.menubar.addAction(self.menuLog.menuAction())
        self.menubar.addAction(self.help.menuAction())
        self.toolBar.addAction(self.actionOpen_TestCase)
        self.toolBar.addAction(self.actionConvertExcelToJson)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpenScript)
        self.toolBar.addAction(self.actionSaveToScript)
        self.toolBar.addAction(self.actionReloadScript)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionConfig)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPrivileges)
        self.toolBar.addAction(self.actionStart)
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpenLog)
        self.toolBar.addAction(self.actionClearLog)
        self.toolBar.addAction(self.actionLogFolder)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionHelper)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRestart)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionMode)
        self.toolBar.addAction(self.actionunknow)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionTestMode)
        self.toolBar.addAction(self.actionproduction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionLocal_IP)
        self.toolBar.addAction(self.action192_168_1_101)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PlasticOmniumLighting"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.result), _translate("MainWindow", "Result"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.stepInfo), _translate("MainWindow", "Property"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.variables), _translate("MainWindow", "Variables"))
        self.pBt_start.setText(_translate("MainWindow", "Start"))
        self.pBt_stop.setText(_translate("MainWindow", "Stop"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Chart), _translate("MainWindow", "Chart"))
        self.lb_video.setText(_translate("MainWindow", "video"))
        self.bt_photo.setText(_translate("MainWindow", "Photo"))
        self.bt_video.setText(_translate("MainWindow", "Video"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.video), _translate("MainWindow", "Video"))
        self.lb_status.setText(_translate("MainWindow", "StandBy"))
        self.label.setText(_translate("MainWindow", "SN:"))
        self.lb_errorCode.setText(_translate("MainWindow", "ErrorCode"))
        self.testcase.setTitle(_translate("MainWindow", "Script"))
        self.menuSelect_Station.setTitle(_translate("MainWindow", "Select Station"))
        self.settings.setTitle(_translate("MainWindow", "Settings"))
        self.help.setTitle(_translate("MainWindow", "Help"))
        self.tools.setTitle(_translate("MainWindow", "Tools"))
        self.debug.setTitle(_translate("MainWindow", "Debug"))
        self.menuLog.setTitle(_translate("MainWindow", "Log"))
        self.menuTestCase.setTitle(_translate("MainWindow", "TestCase"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionOpenScript.setText(_translate("MainWindow", "OpenScript"))
        self.actionOpenScript.setToolTip(_translate("MainWindow", "OpenScript"))
        self.actionConfig.setText(_translate("MainWindow", "参数配置"))
        self.actionReloadScript.setText(_translate("MainWindow", "ReloadScript"))
        self.actionReloadScript.setToolTip(_translate("MainWindow", "ReloadScript"))
        self.actionSaveToScript.setText(_translate("MainWindow", "SaveToScript"))
        self.actionSaveToScript.setToolTip(_translate("MainWindow", "SaveToScript"))
        self.actionStart.setText(_translate("MainWindow", "Start"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))
        self.actionSaveLog.setText(_translate("MainWindow", "SaveLog"))
        self.actionOpenLog.setText(_translate("MainWindow", "OpenLog"))
        self.actionException.setText(_translate("MainWindow", "ExceptionLog"))
        self.actionLogFolder.setText(_translate("MainWindow", "LogFolder"))
        self.actionCSVLog.setText(_translate("MainWindow", "CSVLog"))
        self.actionResultLog.setText(_translate("MainWindow", "ResultLog"))
        self.actionPrivileges.setText(_translate("MainWindow", "Lab"))
        self.actionPrivileges.setToolTip(_translate("MainWindow", "Lab pattern"))
        self.actionHelper.setText(_translate("MainWindow", "Helper"))
        self.actionCheckAll.setText(_translate("MainWindow", "CheckAll"))
        self.actionUncheckAll.setText(_translate("MainWindow", "UncheckAll"))
        self.actionStepping.setText(_translate("MainWindow", "Run Single-Step"))
        self.actionLooping.setText(_translate("MainWindow", "Loop All Selected"))
        self.actionEditStep.setText(_translate("MainWindow", "EditStep"))
        self.actionClearLog.setText(_translate("MainWindow", "ClearLog"))
        self.actionOpen_TestCase.setText(_translate("MainWindow", "Open TestCase"))
        self.actionConvertExcelToJson.setText(_translate("MainWindow", "ConvertExcelToJson"))
        self.actionUpdates.setText(_translate("MainWindow", "Updates"))
        self.actionFeedback.setText(_translate("MainWindow", "Feedback"))
        self.actionPause.setText(_translate("MainWindow", "Pause"))
        self.actionunknow.setText(_translate("MainWindow", "null"))
        self.actionMode.setText(_translate("MainWindow", "Model:"))
        self.actionTestMode.setText(_translate("MainWindow", "TestMode:"))
        self.actionproduction.setText(_translate("MainWindow", "production"))
        self.actionLocal_IP.setText(_translate("MainWindow", "Local_IP:"))
        self.action192_168_1_101.setText(_translate("MainWindow", "192.168.1.101"))
        self.actionRestart.setText(_translate("MainWindow", "Restart"))
        self.actionRestart.setToolTip(_translate("MainWindow", "Restart"))
        self.actionExpandAll.setText(_translate("MainWindow", "ExpandAll"))
        self.actionExpandAll.setToolTip(_translate("MainWindow", "ExpandAll"))
        self.actionCollapseAll.setText(_translate("MainWindow", "CollapseAll"))
        self.actionCollapseAll.setToolTip(_translate("MainWindow", "CollapseAll"))
        self.actionEnable_lab.setText(_translate("MainWindow", "Enable(lab)"))
        self.actionDisable_factory.setText(_translate("MainWindow", "Disable(factory)"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionBreakpoint.setText(_translate("MainWindow", "Breakpoint Set"))
        self.actionBreakpoint.setToolTip(_translate("MainWindow", "Breakpoint"))
        self.actionMBLT.setText(_translate("MainWindow", "MBLT"))
        self.actionPeakLin.setText(_translate("MainWindow", "PEAK"))
        self.actionDelete.setText(_translate("MainWindow", "Delete"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setToolTip(_translate("MainWindow", "Copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setToolTip(_translate("MainWindow", "Paste"))
        self.actionNewSeq.setText(_translate("MainWindow", "New..."))
        self.actionNewStep.setText(_translate("MainWindow", "New..."))
        self.actionNewStep.setToolTip(_translate("MainWindow", "New step"))
        self.actionCutStep.setText(_translate("MainWindow", "Cut"))
        self.actionCutStep.setToolTip(_translate("MainWindow", "Cut step"))
import ui.images_rc
