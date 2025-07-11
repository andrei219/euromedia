# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\harvest.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(962, 873)
        self.exit = QtWidgets.QPushButton(Form)
        self.exit.setGeometry(QtCore.QRect(530, 800, 100, 51))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.exit.setFont(font)
        self.exit.setObjectName("exit")
        self.calculate = QtWidgets.QPushButton(Form)
        self.calculate.setGeometry(QtCore.QRect(400, 800, 100, 50))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.calculate.setFont(font)
        self.calculate.setObjectName("calculate")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(370, 0, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.by_document = QtWidgets.QGroupBox(Form)
        self.by_document.setGeometry(QtCore.QRect(30, 30, 261, 741))
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
        self.document_view.setGeometry(QtCore.QRect(20, 245, 225, 441))
        self.document_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.document_view.setObjectName("document_view")
        self.label_4 = QtWidgets.QLabel(self.by_document)
        self.label_4.setGeometry(QtCore.QRect(10, 190, 125, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.add_document = QtWidgets.QPushButton(self.by_document)
        self.add_document.setGeometry(QtCore.QRect(200, 210, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.add_document.setFont(font)
        self.add_document.setObjectName("add_document")
        self.delete_all_document = QtWidgets.QCheckBox(self.by_document)
        self.delete_all_document.setGeometry(QtCore.QRect(200, 700, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_all_document.setFont(font)
        self.delete_all_document.setObjectName("delete_all_document")
        self.document = QtWidgets.QLineEdit(self.by_document)
        self.document.setGeometry(QtCore.QRect(20, 212, 170, 20))
        self.document.setObjectName("document")
        self.delete_document = QtWidgets.QPushButton(self.by_document)
        self.delete_document.setGeometry(QtCore.QRect(110, 700, 65, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_document.setFont(font)
        self.delete_document.setObjectName("delete_document")
        self.purchase_pi = QtWidgets.QRadioButton(self.by_document)
        self.purchase_pi.setGeometry(QtCore.QRect(20, 20, 135, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.purchase_pi.setFont(font)
        self.purchase_pi.setObjectName("purchase_pi")
        self.purchase_invoice = QtWidgets.QRadioButton(self.by_document)
        self.purchase_invoice.setGeometry(QtCore.QRect(20, 40, 125, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.purchase_invoice.setFont(font)
        self.purchase_invoice.setObjectName("purchase_invoice")
        self.sales_pi = QtWidgets.QRadioButton(self.by_document)
        self.sales_pi.setGeometry(QtCore.QRect(20, 60, 120, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.sales_pi.setFont(font)
        self.sales_pi.setObjectName("sales_pi")
        self.sales_invoice = QtWidgets.QRadioButton(self.by_document)
        self.sales_invoice.setGeometry(QtCore.QRect(20, 80, 105, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.sales_invoice.setFont(font)
        self.sales_invoice.setObjectName("sales_invoice")
        self.partner = QtWidgets.QLineEdit(self.by_document)
        self.partner.setGeometry(QtCore.QRect(10, 110, 231, 20))
        self.partner.setText("")
        self.partner.setAlignment(QtCore.Qt.AlignCenter)
        self.partner.setClearButtonEnabled(True)
        self.partner.setObjectName("partner")
        self.year = QtWidgets.QLineEdit(self.by_document)
        self.year.setGeometry(QtCore.QRect(10, 150, 231, 20))
        self.year.setText("")
        self.year.setAlignment(QtCore.Qt.AlignCenter)
        self.year.setClearButtonEnabled(True)
        self.year.setObjectName("year")
        self.by_period = QtWidgets.QGroupBox(Form)
        self.by_period.setGeometry(QtCore.QRect(310, 61, 281, 251))
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
        self.label_6.setGeometry(QtCore.QRect(80, 50, 21, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_5 = QtWidgets.QLabel(self.by_period)
        self.label_5.setGeometry(QtCore.QRect(70, 20, 31, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.to = QtWidgets.QLineEdit(self.by_period)
        self.to.setGeometry(QtCore.QRect(110, 50, 80, 20))
        self.to.setObjectName("to")
        self._from = QtWidgets.QLineEdit(self.by_period)
        self._from.setGeometry(QtCore.QRect(110, 20, 80, 20))
        self._from.setObjectName("_from")
        self.label = QtWidgets.QLabel(self.by_period)
        self.label.setGeometry(QtCore.QRect(40, 110, 55, 16))
        self.label.setObjectName("label")
        self.agent = QtWidgets.QLineEdit(self.by_period)
        self.agent.setGeometry(QtCore.QRect(110, 110, 131, 22))
        self.agent.setObjectName("agent")
        self.input = QtWidgets.QRadioButton(self.by_period)
        self.input.setGeometry(QtCore.QRect(40, 170, 91, 20))
        self.input.setObjectName("input")
        self.output = QtWidgets.QRadioButton(self.by_period)
        self.output.setGeometry(QtCore.QRect(160, 170, 71, 20))
        self.output.setObjectName("output")
        self.by_serial = QtWidgets.QGroupBox(Form)
        self.by_serial.setGeometry(QtCore.QRect(310, 329, 281, 441))
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
        self.delete_serial.setGeometry(QtCore.QRect(140, 380, 65, 23))
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
        self.serial_view.setGeometry(QtCore.QRect(30, 53, 225, 311))
        self.serial_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.serial_view.setObjectName("serial_view")
        self.delete_all_serial = QtWidgets.QCheckBox(self.by_serial)
        self.delete_all_serial.setGeometry(QtCore.QRect(230, 380, 45, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.delete_all_serial.setFont(font)
        self.delete_all_serial.setObjectName("delete_all_serial")
        self.by_period_2 = QtWidgets.QGroupBox(Form)
        self.by_period_2.setGeometry(QtCore.QRect(610, 60, 281, 251))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.by_period_2.setFont(font)
        self.by_period_2.setCheckable(True)
        self.by_period_2.setChecked(False)
        self.by_period_2.setObjectName("by_period_2")
        self.label_8 = QtWidgets.QLabel(self.by_period_2)
        self.label_8.setGeometry(QtCore.QRect(80, 50, 21, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.by_period_2)
        self.label_9.setGeometry(QtCore.QRect(70, 20, 31, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.to_2 = QtWidgets.QLineEdit(self.by_period_2)
        self.to_2.setGeometry(QtCore.QRect(110, 50, 80, 20))
        self.to_2.setObjectName("to_2")
        self._from_2 = QtWidgets.QLineEdit(self.by_period_2)
        self._from_2.setGeometry(QtCore.QRect(110, 20, 80, 20))
        self._from_2.setObjectName("_from_2")
        self.label_2 = QtWidgets.QLabel(self.by_period_2)
        self.label_2.setGeometry(QtCore.QRect(40, 110, 55, 16))
        self.label_2.setObjectName("label_2")
        self.agent_2 = QtWidgets.QLineEdit(self.by_period_2)
        self.agent_2.setGeometry(QtCore.QRect(110, 110, 131, 22))
        self.agent_2.setObjectName("agent_2")
        self.input_2 = QtWidgets.QRadioButton(self.by_period_2)
        self.input_2.setGeometry(QtCore.QRect(40, 170, 91, 20))
        self.input_2.setObjectName("input_2")
        self.output_2 = QtWidgets.QRadioButton(self.by_period_2)
        self.output_2.setGeometry(QtCore.QRect(160, 170, 71, 20))
        self.output_2.setObjectName("output_2")

        self.retranslateUi(Form)
        self.exit.clicked.connect(Form.close) # type: ignore
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
        self.partner.setPlaceholderText(_translate("Form", "Partner ... "))
        self.year.setPlaceholderText(_translate("Form", "year ..."))
        self.by_period.setTitle(_translate("Form", "By Period"))
        self.label_6.setText(_translate("Form", "to:"))
        self.label_5.setText(_translate("Form", "From:"))
        self.label.setText(_translate("Form", "Agent:"))
        self.input.setText(_translate("Form", "Input"))
        self.output.setText(_translate("Form", "Output"))
        self.by_serial.setTitle(_translate("Form", "By Serial"))
        self.delete_serial.setText(_translate("Form", "Delete"))
        self.add_serial.setText(_translate("Form", "Add"))
        self.delete_all_serial.setText(_translate("Form", "All"))
        self.by_period_2.setTitle(_translate("Form", "By Partner"))
        self.label_8.setText(_translate("Form", "to:"))
        self.label_9.setText(_translate("Form", "From:"))
        self.label_2.setText(_translate("Form", "Agent:"))
        self.input_2.setText(_translate("Form", "Input"))
        self.output_2.setText(_translate("Form", "Output"))
