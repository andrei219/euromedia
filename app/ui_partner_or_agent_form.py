# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\partner_or_agent_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(616, 175)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 20, 571, 71))
        self.groupBox.setObjectName("groupBox")
        self.agent = QtWidgets.QRadioButton(self.groupBox)
        self.agent.setGeometry(QtCore.QRect(70, 30, 181, 17))
        self.agent.setChecked(True)
        self.agent.setObjectName("agent")
        self.partner = QtWidgets.QRadioButton(self.groupBox)
        self.partner.setGeometry(QtCore.QRect(350, 30, 201, 17))
        self.partner.setObjectName("partner")
        self.send = QtWidgets.QPushButton(Dialog)
        self.send.setGeometry(QtCore.QRect(420, 120, 75, 23))
        self.send.setObjectName("send")
        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setGeometry(QtCore.QRect(500, 120, 75, 23))
        self.cancel.setObjectName("cancel")

        self.retranslateUi(Dialog)
        self.cancel.clicked.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Send Whatsapp"))
        self.groupBox.setTitle(_translate("Dialog", "Send to:"))
        self.agent.setText(_translate("Dialog", "Agent"))
        self.partner.setText(_translate("Dialog", "Partner"))
        self.send.setText(_translate("Dialog", "Send"))
        self.cancel.setText(_translate("Dialog", "Cancel"))
