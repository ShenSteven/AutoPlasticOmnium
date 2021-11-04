from PySide2 import QtCore
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import QApplication, QMessageBox, QStyleFactory, QTreeWidgetItem, QMenu
from PySide2.QtUiTools import QUiLoader
from model.testcase import *
from conf import globalvar as gv


class MainForm:
    def __init__(self):
        self.ui = QUiLoader().load('ui/main.ui')
        self.test_task = TestCase("scripts/fireflyALL.xlsx", 'MBLT')
        self.create_model(self.test_task.test_suites)

        self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)
        self.ui.treeWidget.itemClicked.connect(self.handle_itemClicked)
        self.ui.treeWidget.customContextMenuRequested.connect(self.handle_treeWidgetMenu)
        self.ui.actionCheckAll.triggered.connect(self.handle_actionCheckAll)
        self.ui.actionUncheckAll.triggered.connect(self.handle_actionUncheckAll)
        self.ui.actionStepping.triggered.connect(self.handle_actionStepping)
        self.ui.actionLooping.triggered.connect(self.handle_actionLooping)
        self.ui.actionEditStep.triggered.connect(self.handle_actionEditStep)

    def handle_itemChanged(self, checked_item):
        if gv.startFlag:
            return
        if checked_item.parent() is None:
            pNo = self.ui.treeWidget.indexOfTopLevelItem(checked_item)
            isChecked: bool = True if checked_item.checkState(0) == Qt.Checked else False
            self.test_task.test_suites[pNo].isTest = isChecked
            self.ui.treeWidget.itemChanged.disconnect()
            for i in range(0, checked_item.childCount()):
                checked_item.child(i).setCheckState(0, Qt.Checked if isChecked else Qt.Unchecked)
                self.test_task.test_suites[pNo].test_steps[i].isTest = isChecked
            self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)
        else:
            ParentIsTest = []
            pNo = self.ui.treeWidget.indexOfTopLevelItem(checked_item.parent())
            iNo = checked_item.parent().indexOfChild(checked_item)
            isChecked = True if checked_item.checkState(0) == Qt.Checked else False
            self.test_task.test_suites[pNo].test_steps[iNo].isTest = isChecked
            for i in range(checked_item.parent().childCount()):
                isChecked_all = True if checked_item.parent().child(i).checkState(0) == Qt.Checked else False
                ParentIsTest.append(isChecked_all)
            isChecked_parent = any(ParentIsTest)
            self.ui.treeWidget.itemChanged.disconnect()
            self.test_task.test_suites[pNo].isTest = isChecked_parent
            checked_item.parent().setCheckState(0, Qt.Checked if isChecked_parent else Qt.Unchecked)
            self.ui.treeWidget.itemChanged.connect(self.handle_itemChanged)

    def handle_itemClicked(self, clicked_item):
        """mouse left-click event, click always mouse click event in Qt.
        :param clicked_item:
        """
        # ss =QGuiApplication.mouseButtons()
        # if QGuiApplication.mouseButtons() == Qt.LeftButton:
        #     QMessageBox.about(self.ui, '统计结果', "left")
        if clicked_item.parent() is not None:
            ss = clicked_item.parent().data(0, QtCore.Qt.DisplayRole).split(' ', 1)[1]
            self.ui.textEdit.insertHtml('- ' * 9 + f"<a name='testSuite:{ss}'>Start testSuite:{ss}</a>" + '- ' * 9)
            self.ui.textEdit.scrollToAnchor(f'testSuite:{ss}')
            # QMessageBox.about(self.ui, '统计结果', ss)

    def handle_treeWidgetMenu(self, pos: QPoint):
        # nd = self.ui.treeWidget.itemAt(pos)
        menu = QMenu(self.ui.treeWidget)
        menu.addAction(self.ui.actionCheckAll)
        menu.addAction(self.ui.actionUncheckAll)
        menu.addAction(self.ui.actionStepping)
        menu.addAction(self.ui.actionLooping)
        menu.addAction(self.ui.actionEditStep)
        pt = self.ui.treeWidget.mapToGlobal(pos)
        menu.exec_(pt)

    def handle_actionCheckAll(self):
        self.create_model(self.test_task.test_suites, True)

    def handle_actionUncheckAll(self):
        self.create_model(self.test_task.test_suites, False)

    def handle_actionStepping(self):
        pass

    def handle_actionLooping(self):
        pass

    def handle_actionEditStep(self):
        pass

    def create_model(self, sequences, checkall=True):
        self.ui.treeWidget.clear()
        self.ui.treeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        for suite in sequences:
            root_node = QTreeWidgetItem(self.ui.treeWidget)
            root_node.setData(0, QtCore.Qt.DisplayRole, f'{suite.index + 1}. {suite.SeqName}')
            root_node.setIcon(0, QIcon('images/close.png'))
            if checkall:
                root_node.setCheckState(0, Qt.Checked)
            else:
                root_node.setCheckState(0, Qt.Unchecked)
            root_node.setBackground(0, Qt.red)
            # root_node.child()
            for step in suite.test_steps:
                step_node = QTreeWidgetItem(root_node)
                step_node.setData(0, QtCore.Qt.DisplayRole, f'{step.index + 1}) {step.ItemName}')
                if checkall:
                    step_node.setCheckState(0, Qt.Checked)
                else:
                    step_node.setCheckState(0, Qt.Unchecked)
                step_node.setIcon(0, QIcon('images/stop.png'))
                step_node.setBackground(0, Qt.green)
                step_node.setFlags(QtCore.Qt.ItemIsEnabled)
                root_node.addChild(step_node)
        self.ui.treeWidget.setStyle(QStyleFactory.create('windows'))  # 设置成有虚线连接的方式
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.resizeColumnToContents(0)


app = QApplication([])
mainForm = MainForm()
mainForm.ui.show()
app.exec_()

# def mousePressEvent(self, e):  ##重载一下鼠标点击事件
#     # 左键按下
#     if e.buttons() == QtCore.Qt.LeftButton:
#         self.mouseClick = Qt.LeftButton
#     # 右键按下
#     elif e.buttons() == QtCore.Qt.RightButton:
#         self.mouseClick = Qt.RightButton
#     # 中键按下
#     elif e.buttons() == QtCore.Qt.MidButton:
#         self.mouseClick = Qt.MidButton
#     # 左右键同时按下
#     elif e.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.RightButton:
#         self.mouseClick = QtCore.Qt.LeftButton | QtCore.Qt.RightButton
#
#  def onCurrentChanged(self, current, previous):
#
#         txt = '父级:[{}] '.format(str(current.parent().data()))
#         txt += '当前选中:[(行{},列{})] '.format(current.row(), current.column())
#
#         name = ''
#         info = ''
#         if current.column() == 0:
#             name = str(current.data())
#             info = str(current.sibling(current.row(), 1).data())
#         else:
#             name = str(current.sibling(current.row(), 0).data())
#             info = str(current.data())
#
#         txt += '名称:[{}]  信息:[{}]'.format(name, info)
#
#         self.ui.statusBar().showMessage(txt)


#
# def run(is_cyclic=False, single_step=True):
#     test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')
#
#     if is_cyclic:
#         while True:
#             test_task.run(test_task.test_suites.copy(), True, 0)
#     elif single_step:
#         test_task.test_suites.copy()[0].test_steps[2].run()
#     else:
#         create_csv_file('result.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
#         test_task.run(test_task.test_suites.copy(), True)
#         print(gv.csv_list_result)
#         write_csv_file('result.csv', gv.csv_list_result)
#         write_csv_file('result.csv', gv.csv_list_header)
# run(False)
