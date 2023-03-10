# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\advanced_definition_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1326, 913)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(20, 130, 1271, 341))
        self.groupBox.setObjectName("groupBox")
        self.lines_view = ClipView(self.groupBox)
        self.lines_view.setGeometry(QtCore.QRect(0, 30, 1271, 311))
        self.lines_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.lines_view.setObjectName("lines_view")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 30, 1271, 91))
        self.groupBox_2.setObjectName("groupBox_2")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 40, 193, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.document = QtWidgets.QLineEdit(self.layoutWidget)
        self.document.setReadOnly(True)
        self.document.setObjectName("document")
        self.horizontalLayout.addWidget(self.document)
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget1.setGeometry(QtCore.QRect(290, 40, 168, 22))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.date = QtWidgets.QLineEdit(self.layoutWidget1)
        self.date.setReadOnly(True)
        self.date.setObjectName("date")
        self.horizontalLayout_2.addWidget(self.date)
        self.layoutWidget2 = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget2.setGeometry(QtCore.QRect(490, 40, 369, 22))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.partner = QtWidgets.QLineEdit(self.layoutWidget2)
        self.partner.setMinimumSize(QtCore.QSize(321, 0))
        self.partner.setReadOnly(True)
        self.partner.setObjectName("partner")
        self.horizontalLayout_3.addWidget(self.partner)
        self.layoutWidget3 = QtWidgets.QWidget(self.groupBox_2)
        self.layoutWidget3.setGeometry(QtCore.QRect(960, 40, 200, 22))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget3)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.warehouse = QtWidgets.QLineEdit(self.layoutWidget3)
        self.warehouse.setReadOnly(True)
        self.warehouse.setObjectName("warehouse")
        self.horizontalLayout_4.addWidget(self.warehouse)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 480, 611, 311))
        self.groupBox_3.setObjectName("groupBox_3")
        self.stock_view = ClipView(self.groupBox_3)
        self.stock_view.setGeometry(QtCore.QRect(0, 20, 611, 291))
        self.stock_view.setObjectName("stock_view")
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setGeometry(QtCore.QRect(660, 480, 631, 311))
        self.groupBox_4.setObjectName("groupBox_4")
        self.defined_view = ClipView(self.groupBox_4)
        self.defined_view.setGeometry(QtCore.QRect(0, 20, 631, 291))
        self.defined_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.defined_view.setObjectName("defined_view")
        self.delete_ = QtWidgets.QPushButton(Form)
        self.delete_.setGeometry(QtCore.QRect(1217, 800, 75, 31))
        self.delete_.setObjectName("delete_")
        self.update = QtWidgets.QPushButton(Form)
        self.update.setGeometry(QtCore.QRect(560, 800, 71, 31))
        self.update.setObjectName("update")
        self.save = QtWidgets.QPushButton(Form)
        self.save.setGeometry(QtCore.QRect(1200, 860, 91, 31))
        self.save.setObjectName("save")
        self.cancel = QtWidgets.QPushButton(Form)
        self.cancel.setGeometry(QtCore.QRect(1100, 860, 81, 31))
        self.cancel.setObjectName("cancel")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setGeometry(QtCore.QRect(770, 810, 401, 16))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.total = QtWidgets.QLabel(self.splitter)
        self.total.setStyleSheet("font-weight:bold;")
        self.total.setText("")
        self.total.setObjectName("total")
        self.selected = QtWidgets.QLabel(self.splitter)
        self.selected.setStyleSheet("font-weight:bold;")
        self.selected.setText("")
        self.selected.setObjectName("selected")

        self.retranslateUi(Form)
        self.cancel.clicked.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Previous Lines:"))
        self.groupBox_2.setTitle(_translate("Form", "Info"))
        self.label.setText(_translate("Form", "Document:"))
        self.label_2.setText(_translate("Form", "Date:"))
        self.label_3.setText(_translate("Form", "Partner:"))
        self.label_4.setText(_translate("Form", "Warehouse:"))
        self.groupBox_3.setTitle(_translate("Form", "Available Physical Stock:"))
        self.groupBox_4.setTitle(_translate("Form", "Selected Stock Per Line:"))
        self.delete_.setText(_translate("Form", "Delete"))
        self.update.setText(_translate("Form", "Update"))
        self.save.setText(_translate("Form", "Save"))
        self.cancel.setText(_translate("Form", "Cancel"))
from clipview import ClipView
