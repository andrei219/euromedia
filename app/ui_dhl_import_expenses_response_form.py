# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\dhl_import_expenses_response.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(479, 345)
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setGeometry(QtCore.QRect(70, 40, 151, 241))
        self.groupBox_4.setObjectName("groupBox_4")
        self.resolved = QtWidgets.QListView(self.groupBox_4)
        self.resolved.setGeometry(QtCore.QRect(0, 20, 151, 221))
        self.resolved.setObjectName("resolved")
        self.groupBox_5 = QtWidgets.QGroupBox(Form)
        self.groupBox_5.setGeometry(QtCore.QRect(290, 40, 151, 241))
        self.groupBox_5.setObjectName("groupBox_5")
        self.notresolved = QtWidgets.QListView(self.groupBox_5)
        self.notresolved.setGeometry(QtCore.QRect(0, 20, 151, 221))
        self.notresolved.setObjectName("notresolved")
        self.ok = QtWidgets.QPushButton(Form)
        self.ok.setGeometry(QtCore.QRect(370, 300, 75, 23))
        self.ok.setObjectName("ok")

        self.retranslateUi(Form)
        self.ok.clicked.connect(Form.accept)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Dialog"))
        self.groupBox_4.setTitle(_translate("Form", "Resolved"))
        self.groupBox_5.setTitle(_translate("Form", "Not resolved"))
        self.ok.setText(_translate("Form", "Ok"))
