# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\harvest.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(615, 646)
        self.exit = QtWidgets.QPushButton(Form)
        self.exit.setGeometry(QtCore.QRect(470, 580, 100, 30))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.exit.setFont(font)
        self.exit.setObjectName("exit")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(280, 80, 20, 411))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.calculate = QtWidgets.QPushButton(Form)
        self.calculate.setGeometry(QtCore.QRect(470, 520, 100, 50))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.calculate.setFont(font)
        self.calculate.setObjectName("calculate")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(215, 20, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(315, 210, 250, 3))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.by_document = QtWidgets.QGroupBox(Form)
        self.by_document.setGeometry(QtCore.QRect(10, 60, 281, 451))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.by_document.setFont(font)
        self.by_document.setCheckable(True)
        self.by_document.setChecked(False)
        self.by_document.setObjectName("by_document")
        self.document_view = QtWidgets.QListView(self.by_document)
        self.document_view.setGeometry(QtCore.QRect(20, 210, 225, 190))
        self.document_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.document_view.setObjectName("document_view")
        self.label_4 = QtWidgets.QLabel(self.by_document)
        self.label_4.setGeometry(QtCore.QRect(10, 160, 125, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.add_document = QtWidgets.QPushButton(self.by_document)
        self.add_document.setGeometry(QtCore.QRect(200, 185, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.add_document.setFont(font)
        self.add_document.setObjectName("add_document")
        self.delete_all_document = QtWidgets.QCheckBox(self.by_document)
        self.delete_all_document.setGeometry(QtCore.QRect(210, 405, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_all_document.setFont(font)
        self.delete_all_document.setObjectName("delete_all_document")
        self.document = QtWidgets.QLineEdit(self.by_document)
        self.document.setGeometry(QtCore.QRect(20, 187, 170, 20))
        self.document.setObjectName("document")
        self.delete_document = QtWidgets.QPushButton(self.by_document)
        self.delete_document.setGeometry(QtCore.QRect(130, 405, 65, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_document.setFont(font)
        self.delete_document.setObjectName("delete_document")
        self.purchase_pi = QtWidgets.QRadioButton(self.by_document)
        self.purchase_pi.setGeometry(QtCore.QRect(20, 50, 135, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.purchase_pi.setFont(font)
        self.purchase_pi.setObjectName("purchase_pi")
        self.purchase_invoice = QtWidgets.QRadioButton(self.by_document)
        self.purchase_invoice.setGeometry(QtCore.QRect(20, 70, 125, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.purchase_invoice.setFont(font)
        self.purchase_invoice.setObjectName("purchase_invoice")
        self.sales_pi = QtWidgets.QRadioButton(self.by_document)
        self.sales_pi.setGeometry(QtCore.QRect(20, 90, 120, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.sales_pi.setFont(font)
        self.sales_pi.setObjectName("sales_pi")
        self.sales_invoice = QtWidgets.QRadioButton(self.by_document)
        self.sales_invoice.setGeometry(QtCore.QRect(20, 110, 105, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.sales_invoice.setFont(font)
        self.sales_invoice.setObjectName("sales_invoice")
        self.by_period = QtWidgets.QGroupBox(Form)
        self.by_period.setGeometry(QtCore.QRect(290, 60, 281, 151))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.by_period.setFont(font)
        self.by_period.setCheckable(True)
        self.by_period.setChecked(False)
        self.by_period.setObjectName("by_period")
        self.label_6 = QtWidgets.QLabel(self.by_period)
        self.label_6.setGeometry(QtCore.QRect(70, 80, 21, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_5 = QtWidgets.QLabel(self.by_period)
        self.label_5.setGeometry(QtCore.QRect(60, 50, 31, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.to = QtWidgets.QLineEdit(self.by_period)
        self.to.setGeometry(QtCore.QRect(100, 80, 80, 20))
        self.to.setObjectName("to")
        self._from = QtWidgets.QLineEdit(self.by_period)
        self._from.setGeometry(QtCore.QRect(100, 50, 80, 20))
        self._from.setObjectName("_from")
        self.by_serial = QtWidgets.QGroupBox(Form)
        self.by_serial.setGeometry(QtCore.QRect(290, 220, 281, 291))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.by_serial.setFont(font)
        self.by_serial.setCheckable(True)
        self.by_serial.setChecked(False)
        self.by_serial.setObjectName("by_serial")
        self.delete_serial = QtWidgets.QPushButton(self.by_serial)
        self.delete_serial.setGeometry(QtCore.QRect(140, 248, 65, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_serial.setFont(font)
        self.delete_serial.setObjectName("delete_serial")
        self.serial = QtWidgets.QLineEdit(self.by_serial)
        self.serial.setGeometry(QtCore.QRect(30, 30, 170, 20))
        self.serial.setObjectName("serial")
        self.add_serial = QtWidgets.QPushButton(self.by_serial)
        self.add_serial.setGeometry(QtCore.QRect(210, 28, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.add_serial.setFont(font)
        self.add_serial.setObjectName("add_serial")
        self.serial_view = QtWidgets.QListView(self.by_serial)
        self.serial_view.setGeometry(QtCore.QRect(30, 53, 225, 190))
        self.serial_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.serial_view.setObjectName("serial_view")
        self.delete_all_serial = QtWidgets.QCheckBox(self.by_serial)
        self.delete_all_serial.setGeometry(QtCore.QRect(220, 248, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_all_serial.setFont(font)
        self.delete_all_serial.setObjectName("delete_all_serial")

        self.retranslateUi(Form)
        self.exit.clicked.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.by_document, self.purchase_pi)
        Form.setTabOrder(self.purchase_pi, self.purchase_invoice)
        Form.setTabOrder(self.purchase_invoice, self.sales_pi)
        Form.setTabOrder(self.sales_pi, self.sales_invoice)
        Form.setTabOrder(self.sales_invoice, self.document)
        Form.setTabOrder(self.document, self.document_view)
        Form.setTabOrder(self.document_view, self.add_document)
        Form.setTabOrder(self.add_document, self.delete_document)
        Form.setTabOrder(self.delete_document, self.delete_all_document)
        Form.setTabOrder(self.delete_all_document, self.by_period)
        Form.setTabOrder(self.by_period, self._from)
        Form.setTabOrder(self._from, self.to)
        Form.setTabOrder(self.to, self.by_serial)
        Form.setTabOrder(self.by_serial, self.serial)
        Form.setTabOrder(self.serial, self.serial_view)
        Form.setTabOrder(self.serial_view, self.add_serial)
        Form.setTabOrder(self.add_serial, self.delete_serial)
        Form.setTabOrder(self.delete_serial, self.delete_all_serial)
        Form.setTabOrder(self.delete_all_serial, self.calculate)
        Form.setTabOrder(self.calculate, self.exit)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Harvest"))
        self.exit.setText(_translate("Form", "Exit"))
        self.calculate.setText(_translate("Form", "Calculate"))
        self.label_7.setText(_translate("Form", "Harvest Check"))
        self.by_document.setTitle(_translate("Form", "By Document"))
        self.label_4.setText(_translate("Form", "Introduce Doc. Nº:"))
        self.add_document.setText(_translate("Form", "Add"))
        self.delete_all_document.setText(_translate("Form", "All"))
        self.delete_document.setText(_translate("Form", "Delete"))
        self.purchase_pi.setText(_translate("Form", "Purchase Proforma"))
        self.purchase_invoice.setText(_translate("Form", "Purchase Invoice"))
        self.sales_pi.setText(_translate("Form", "Sales Proforma"))
        self.sales_invoice.setText(_translate("Form", "Sales Invoice"))
        self.by_period.setTitle(_translate("Form", "By Period"))
        self.label_6.setText(_translate("Form", "to:"))
        self.label_5.setText(_translate("Form", "From:"))
        self.by_serial.setTitle(_translate("Form", "By Serial"))
        self.delete_serial.setText(_translate("Form", "Delete"))
        self.add_serial.setText(_translate("Form", "Add"))
        self.delete_all_serial.setText(_translate("Form", "All"))