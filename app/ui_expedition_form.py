# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\expedition_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExpeditionForm(object):
    def setupUi(self, ExpeditionForm):
        ExpeditionForm.setObjectName("ExpeditionForm")
        ExpeditionForm.resize(974, 902)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/warehouse"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExpeditionForm.setWindowIcon(icon)
        ExpeditionForm.setWindowOpacity(1.0)
        ExpeditionForm.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        ExpeditionForm.setModal(False)
        self.exit = QtWidgets.QToolButton(ExpeditionForm)
        self.exit.setGeometry(QtCore.QRect(810, 770, 61, 71))
        self.exit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.exit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.exit.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/exit"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exit.setIcon(icon1)
        self.exit.setIconSize(QtCore.QSize(32, 32))
        self.exit.setCheckable(False)
        self.exit.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.exit.setAutoRaise(True)
        self.exit.setObjectName("exit")
        self.delete_imei = QtWidgets.QToolButton(ExpeditionForm)
        self.delete_imei.setGeometry(QtCore.QRect(320, 794, 81, 25))
        self.delete_imei.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.delete_imei.setStyleSheet("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/delete"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_imei.setIcon(icon2)
        self.delete_imei.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.delete_imei.setAutoRaise(True)
        self.delete_imei.setObjectName("delete_imei")
        self.imei = QtWidgets.QLineEdit(ExpeditionForm)
        self.imei.setGeometry(QtCore.QRect(150, 567, 321, 26))
        self.imei.setInputMask("")
        self.imei.setText("")
        self.imei.setAlignment(QtCore.Qt.AlignCenter)
        self.imei.setObjectName("imei")
        self.header = QtWidgets.QGroupBox(ExpeditionForm)
        self.header.setGeometry(QtCore.QRect(60, 20, 811, 251))
        self.header.setObjectName("header")
        self.label_3 = QtWidgets.QLabel(self.header)
        self.label_3.setGeometry(QtCore.QRect(30, 217, 111, 21))
        self.label_3.setObjectName("label_3")
        self.partner = QtWidgets.QLineEdit(self.header)
        self.partner.setEnabled(True)
        self.partner.setGeometry(QtCore.QRect(150, 60, 431, 22))
        self.partner.setReadOnly(True)
        self.partner.setObjectName("partner")
        self.label = QtWidgets.QLabel(self.header)
        self.label.setGeometry(QtCore.QRect(90, 181, 41, 21))
        self.label.setObjectName("label")
        self.Label4 = QtWidgets.QLabel(self.header)
        self.Label4.setGeometry(QtCore.QRect(75, 105, 38, 16))
        self.Label4.setStyleSheet("")
        self.Label4.setObjectName("Label4")
        self.Label5 = QtWidgets.QLabel(self.header)
        self.Label5.setGeometry(QtCore.QRect(54, 147, 81, 20))
        self.Label5.setStyleSheet("")
        self.Label5.setObjectName("Label5")
        self.agent = QtWidgets.QLineEdit(self.header)
        self.agent.setEnabled(True)
        self.agent.setGeometry(QtCore.QRect(150, 106, 431, 22))
        self.agent.setReadOnly(True)
        self.agent.setObjectName("agent")
        self.expedition_total = QtWidgets.QLineEdit(self.header)
        self.expedition_total.setGeometry(QtCore.QRect(150, 181, 221, 22))
        self.expedition_total.setReadOnly(True)
        self.expedition_total.setObjectName("expedition_total")
        self.Label3 = QtWidgets.QLabel(self.header)
        self.Label3.setGeometry(QtCore.QRect(70, 60, 47, 16))
        self.Label3.setStyleSheet("")
        self.Label3.setObjectName("Label3")
        self.expedition_number = QtWidgets.QLineEdit(self.header)
        self.expedition_number.setEnabled(True)
        self.expedition_number.setGeometry(QtCore.QRect(150, 21, 137, 22))
        self.expedition_number.setReadOnly(True)
        self.expedition_number.setObjectName("expedition_number")
        self.warehouse = QtWidgets.QLineEdit(self.header)
        self.warehouse.setEnabled(True)
        self.warehouse.setGeometry(QtCore.QRect(150, 147, 221, 22))
        self.warehouse.setReadOnly(True)
        self.warehouse.setObjectName("warehouse")
        self.expedition_total_processed = QtWidgets.QLineEdit(self.header)
        self.expedition_total_processed.setGeometry(QtCore.QRect(150, 217, 221, 22))
        self.expedition_total_processed.setReadOnly(True)
        self.expedition_total_processed.setObjectName("expedition_total_processed")
        self.Label2 = QtWidgets.QLabel(self.header)
        self.Label2.setGeometry(QtCore.QRect(370, 20, 41, 20))
        self.Label2.setStyleSheet("")
        self.Label2.setObjectName("Label2")
        self.Label1 = QtWidgets.QLabel(self.header)
        self.Label1.setGeometry(QtCore.QRect(40, 21, 90, 20))
        self.Label1.setStyleSheet("")
        self.Label1.setObjectName("Label1")
        self.date = QtWidgets.QLineEdit(self.header)
        self.date.setEnabled(True)
        self.date.setGeometry(QtCore.QRect(420, 20, 161, 22))
        self.date.setMinimumSize(QtCore.QSize(121, 0))
        self.date.setReadOnly(True)
        self.date.setObjectName("date")
        self.lines_group = QtWidgets.QGroupBox(ExpeditionForm)
        self.lines_group.setGeometry(QtCore.QRect(60, 310, 811, 231))
        self.lines_group.setObjectName("lines_group")
        self.next = QtWidgets.QToolButton(self.lines_group)
        self.next.setGeometry(QtCore.QRect(210, 160, 71, 51))
        self.next.setStyleSheet("background: white;")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/right_arrow"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next.setIcon(icon3)
        self.next.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.next.setAutoRaise(True)
        self.next.setArrowType(QtCore.Qt.RightArrow)
        self.next.setObjectName("next")
        self.Label6 = QtWidgets.QLabel(self.lines_group)
        self.Label6.setGeometry(QtCore.QRect(30, 50, 81, 21))
        self.Label6.setStyleSheet("")
        self.Label6.setObjectName("Label6")
        self.spec = QtWidgets.QLineEdit(self.lines_group)
        self.spec.setEnabled(True)
        self.spec.setGeometry(QtCore.QRect(620, 100, 121, 26))
        self.spec.setMinimumSize(QtCore.QSize(121, 0))
        self.spec.setAlignment(QtCore.Qt.AlignCenter)
        self.spec.setReadOnly(True)
        self.spec.setObjectName("spec")
        self.condition = QtWidgets.QLineEdit(self.lines_group)
        self.condition.setEnabled(True)
        self.condition.setGeometry(QtCore.QRect(120, 100, 121, 26))
        self.condition.setMinimumSize(QtCore.QSize(121, 0))
        self.condition.setAlignment(QtCore.Qt.AlignCenter)
        self.condition.setReadOnly(True)
        self.condition.setObjectName("condition")
        self.number = QtWidgets.QLineEdit(self.lines_group)
        self.number.setEnabled(True)
        self.number.setGeometry(QtCore.QRect(530, 50, 61, 21))
        self.number.setAlignment(QtCore.Qt.AlignCenter)
        self.number.setReadOnly(True)
        self.number.setObjectName("number")
        self.Label2_2 = QtWidgets.QLabel(self.lines_group)
        self.Label2_2.setGeometry(QtCore.QRect(40, 100, 71, 20))
        self.Label2_2.setStyleSheet("")
        self.Label2_2.setObjectName("Label2_2")
        self.Label2_3 = QtWidgets.QLabel(self.lines_group)
        self.Label2_3.setGeometry(QtCore.QRect(570, 100, 41, 20))
        self.Label2_3.setStyleSheet("")
        self.Label2_3.setObjectName("Label2_3")
        self.description = QtWidgets.QLineEdit(self.lines_group)
        self.description.setEnabled(True)
        self.description.setGeometry(QtCore.QRect(120, 50, 381, 22))
        self.description.setAlignment(QtCore.Qt.AlignCenter)
        self.description.setReadOnly(True)
        self.description.setObjectName("description")
        self.label_2 = QtWidgets.QLabel(self.lines_group)
        self.label_2.setGeometry(QtCore.QRect(600, 50, 21, 16))
        self.label_2.setObjectName("label_2")
        self.prev = QtWidgets.QToolButton(self.lines_group)
        self.prev.setGeometry(QtCore.QRect(110, 160, 71, 51))
        self.prev.setStyleSheet("background: white;")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/cancel"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.prev.setIcon(icon4)
        self.prev.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.prev.setAutoRaise(True)
        self.prev.setArrowType(QtCore.Qt.LeftArrow)
        self.prev.setObjectName("prev")
        self.overflow = QtWidgets.QLabel(self.lines_group)
        self.overflow.setGeometry(QtCore.QRect(454, 20, 111, 20))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.overflow.setFont(font)
        self.overflow.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";")
        self.overflow.setText("")
        self.overflow.setObjectName("overflow")
        self.label_5 = QtWidgets.QLabel(self.lines_group)
        self.label_5.setGeometry(QtCore.QRect(250, 107, 101, 16))
        self.label_5.setObjectName("label_5")
        self.showing_condition = QtWidgets.QLineEdit(self.lines_group)
        self.showing_condition.setGeometry(QtCore.QRect(370, 106, 113, 20))
        self.showing_condition.setAlignment(QtCore.Qt.AlignCenter)
        self.showing_condition.setReadOnly(True)
        self.showing_condition.setObjectName("showing_condition")
        self.Label8 = QtWidgets.QLabel(self.lines_group)
        self.Label8.setGeometry(QtCore.QRect(520, 161, 95, 20))
        self.Label8.setMinimumSize(QtCore.QSize(95, 20))
        self.Label8.setMaximumSize(QtCore.QSize(95, 20))
        self.Label8.setObjectName("Label8")
        self.line_total = QtWidgets.QLineEdit(self.lines_group)
        self.line_total.setEnabled(True)
        self.line_total.setGeometry(QtCore.QRect(621, 161, 81, 21))
        self.line_total.setMinimumSize(QtCore.QSize(81, 21))
        self.line_total.setMaximumSize(QtCore.QSize(81, 21))
        self.line_total.setAlignment(QtCore.Qt.AlignCenter)
        self.line_total.setReadOnly(True)
        self.line_total.setObjectName("line_total")
        self.Label10 = QtWidgets.QLabel(self.lines_group)
        self.Label10.setGeometry(QtCore.QRect(520, 191, 71, 16))
        self.Label10.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Label10.setObjectName("Label10")
        self.processed_line = QtWidgets.QLineEdit(self.lines_group)
        self.processed_line.setEnabled(True)
        self.processed_line.setGeometry(QtCore.QRect(621, 191, 81, 22))
        self.processed_line.setMinimumSize(QtCore.QSize(81, 22))
        self.processed_line.setMaximumSize(QtCore.QSize(81, 22))
        self.processed_line.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.processed_line.setAlignment(QtCore.Qt.AlignCenter)
        self.processed_line.setReadOnly(True)
        self.processed_line.setObjectName("processed_line")
        self.automatic_input = QtWidgets.QGroupBox(ExpeditionForm)
        self.automatic_input.setGeometry(QtCore.QRect(490, 570, 211, 51))
        self.automatic_input.setCheckable(True)
        self.automatic_input.setChecked(False)
        self.automatic_input.setObjectName("automatic_input")
        self.lenght = QtWidgets.QSpinBox(self.automatic_input)
        self.lenght.setGeometry(QtCore.QRect(130, 20, 61, 22))
        self.lenght.setObjectName("lenght")
        self.label_4 = QtWidgets.QLabel(self.automatic_input)
        self.label_4.setGeometry(QtCore.QRect(20, 23, 101, 16))
        self.label_4.setObjectName("label_4")
        self.all = QtWidgets.QCheckBox(ExpeditionForm)
        self.all.setGeometry(QtCore.QRect(410, 797, 61, 20))
        self.all.setObjectName("all")
        self.current = QtWidgets.QLabel(ExpeditionForm)
        self.current.setGeometry(QtCore.QRect(940, 350, 251, 16))
        self.current.setStyleSheet("font-weight:bold; font-size:16px")
        self.current.setText("")
        self.current.setObjectName("current")
        self.view = ClipListView(ExpeditionForm)
        self.view.setGeometry(QtCore.QRect(150, 600, 321, 181))
        self.view.setObjectName("view")

        self.retranslateUi(ExpeditionForm)
        self.exit.clicked.connect(ExpeditionForm.close)
        QtCore.QMetaObject.connectSlotsByName(ExpeditionForm)
        ExpeditionForm.setTabOrder(self.expedition_number, self.date)
        ExpeditionForm.setTabOrder(self.date, self.partner)
        ExpeditionForm.setTabOrder(self.partner, self.agent)
        ExpeditionForm.setTabOrder(self.agent, self.warehouse)
        ExpeditionForm.setTabOrder(self.warehouse, self.description)
        ExpeditionForm.setTabOrder(self.description, self.imei)
        ExpeditionForm.setTabOrder(self.imei, self.delete_imei)

    def retranslateUi(self, ExpeditionForm):
        _translate = QtCore.QCoreApplication.translate
        ExpeditionForm.setWindowTitle(_translate("ExpeditionForm", "Expedition"))
        self.exit.setText(_translate("ExpeditionForm", "Exit"))
        self.delete_imei.setText(_translate("ExpeditionForm", "Delete"))
        self.imei.setPlaceholderText(_translate("ExpeditionForm", "ENTER IMEI/SN ... OR SEARCH"))
        self.header.setTitle(_translate("ExpeditionForm", "GENERAL:"))
        self.label_3.setText(_translate("ExpeditionForm", "Total Processed:"))
        self.label.setText(_translate("ExpeditionForm", "Total:"))
        self.Label4.setText(_translate("ExpeditionForm", "Agent:"))
        self.Label5.setText(_translate("ExpeditionForm", "Warehouse:"))
        self.Label3.setText(_translate("ExpeditionForm", "Partner:"))
        self.Label2.setText(_translate("ExpeditionForm", "Date:"))
        self.Label1.setText(_translate("ExpeditionForm", "Expedition Nº:"))
        self.lines_group.setTitle(_translate("ExpeditionForm", "LINES:"))
        self.next.setText(_translate("ExpeditionForm", "Next"))
        self.Label6.setText(_translate("ExpeditionForm", "Description:"))
        self.Label2_2.setText(_translate("ExpeditionForm", "Condition:"))
        self.Label2_3.setText(_translate("ExpeditionForm", "Spec:"))
        self.label_2.setText(_translate("ExpeditionForm", "Nº"))
        self.prev.setText(_translate("ExpeditionForm", "Prev"))
        self.label_5.setText(_translate("ExpeditionForm", "Public condition:"))
        self.Label8.setText(_translate("ExpeditionForm", "Line Total :"))
        self.Label10.setText(_translate("ExpeditionForm", "Processed:"))
        self.automatic_input.setTitle(_translate("ExpeditionForm", "AUTOMATIC INPUT:"))
        self.label_4.setText(_translate("ExpeditionForm", "IMEI/SN Lenght:"))
        self.all.setText(_translate("ExpeditionForm", "ALL"))
from clipview import ClipListView
import icons_rc
