# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\credit_note_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1340, 958)
        font = QtGui.QFont()
        font.setPointSize(10)
        Form.setFont(font)
        Form.setToolTipDuration(1)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(90, 260, 1181, 451))
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.view = ClipView(self.groupBox)
        self.view.setEnabled(True)
        self.view.setGeometry(QtCore.QRect(40, 30, 1121, 401))
        self.view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.view.setObjectName("view")
        self.cancel = QtWidgets.QPushButton(Form)
        self.cancel.setGeometry(QtCore.QRect(1170, 900, 91, 31))
        self.cancel.setObjectName("cancel")
        self.note = QtWidgets.QTextEdit(Form)
        self.note.setGeometry(QtCore.QRect(880, 780, 371, 81))
        self.note.setObjectName("note")
        self.header = QtWidgets.QGroupBox(Form)
        self.header.setGeometry(QtCore.QRect(110, 10, 1101, 191))
        self.header.setFlat(True)
        self.header.setObjectName("header")
        self.layoutWidget_2 = QtWidgets.QWidget(self.header)
        self.layoutWidget_2.setGeometry(QtCore.QRect(50, 150, 246, 29))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_6.addWidget(self.label_9)
        self.tracking = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.tracking.setObjectName("tracking")
        self.horizontalLayout_6.addWidget(self.tracking)
        self.layoutWidget_5 = QtWidgets.QWidget(self.header)
        self.layoutWidget_5.setGeometry(QtCore.QRect(40, 40, 807, 29))
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.layoutWidget_5)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_21 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_21.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_21.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_21.setObjectName("label_21")
        self.horizontalLayout_9.addWidget(self.label_21)
        self.type = QtWidgets.QComboBox(self.layoutWidget_5)
        self.type.setMinimumSize(QtCore.QSize(41, 22))
        self.type.setMaximumSize(QtCore.QSize(41, 22))
        self.type.setFrame(False)
        self.type.setObjectName("type")
        self.type.addItem("")
        self.type.addItem("")
        self.type.addItem("")
        self.type.addItem("")
        self.type.addItem("")
        self.type.addItem("")
        self.horizontalLayout_9.addWidget(self.type)
        self.number = QtWidgets.QLineEdit(self.layoutWidget_5)
        self.number.setMinimumSize(QtCore.QSize(81, 20))
        self.number.setMaximumSize(QtCore.QSize(81, 22))
        self.number.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.number.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.number.setReadOnly(False)
        self.number.setObjectName("number")
        self.horizontalLayout_9.addWidget(self.number)
        spacerItem = QtWidgets.QSpacerItem(28, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem)
        self.label_22 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_22.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_9.addWidget(self.label_22)
        self.date = QtWidgets.QLineEdit(self.layoutWidget_5)
        self.date.setMinimumSize(QtCore.QSize(101, 22))
        self.date.setMaximumSize(QtCore.QSize(101, 22))
        self.date.setAlignment(QtCore.Qt.AlignCenter)
        self.date.setObjectName("date")
        self.horizontalLayout_9.addWidget(self.date)
        spacerItem1 = QtWidgets.QSpacerItem(28, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(28, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem2)
        self.label_24 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_24.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_24.setObjectName("label_24")
        self.horizontalLayout_9.addWidget(self.label_24)
        self.agent = QtWidgets.QComboBox(self.layoutWidget_5)
        self.agent.setMinimumSize(QtCore.QSize(191, 22))
        self.agent.setMaximumSize(QtCore.QSize(191, 22))
        self.agent.setObjectName("agent")
        self.horizontalLayout_9.addWidget(self.agent)
        self.groupBox_3 = QtWidgets.QGroupBox(self.header)
        self.groupBox_3.setGeometry(QtCore.QRect(850, 100, 171, 91))
        self.groupBox_3.setObjectName("groupBox_3")
        self.they_pay_they_ship = QtWidgets.QRadioButton(self.groupBox_3)
        self.they_pay_they_ship.setGeometry(QtCore.QRect(10, 40, 151, 18))
        self.they_pay_they_ship.setObjectName("they_pay_they_ship")
        self.we_pay_we_ship = QtWidgets.QRadioButton(self.groupBox_3)
        self.we_pay_we_ship.setGeometry(QtCore.QRect(10, 60, 151, 17))
        self.we_pay_we_ship.setObjectName("we_pay_we_ship")
        self.they_pay_we_ship = QtWidgets.QRadioButton(self.groupBox_3)
        self.they_pay_we_ship.setGeometry(QtCore.QRect(10, 20, 141, 18))
        self.they_pay_we_ship.setObjectName("they_pay_we_ship")
        self.label_25 = QtWidgets.QLabel(self.header)
        self.label_25.setGeometry(QtCore.QRect(30, 120, 56, 16))
        self.label_25.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_25.setObjectName("label_25")
        self.frame = QtWidgets.QFrame(self.header)
        self.frame.setGeometry(QtCore.QRect(100, 110, 141, 31))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.eur = QtWidgets.QRadioButton(self.frame)
        self.eur.setGeometry(QtCore.QRect(10, 8, 51, 20))
        self.eur.setObjectName("eur")
        self.usd = QtWidgets.QRadioButton(self.frame)
        self.usd.setGeometry(QtCore.QRect(70, 10, 61, 18))
        self.usd.setObjectName("usd")
        self.incoterms = QtWidgets.QComboBox(self.header)
        self.incoterms.setGeometry(QtCore.QRect(970, 50, 51, 22))
        self.incoterms.setMinimumSize(QtCore.QSize(51, 22))
        self.incoterms.setMaximumSize(QtCore.QSize(51, 22))
        self.incoterms.setIconSize(QtCore.QSize(16, 16))
        self.incoterms.setFrame(False)
        self.incoterms.setObjectName("incoterms")
        self.incoterms.addItem("")
        self.incoterms.addItem("")
        self.incoterms.setItemText(1, "")
        self.incoterms.addItem("")
        self.incoterms.addItem("")
        self.incoterms.addItem("")
        self.incoterms.addItem("")
        self.incoterms.addItem("")
        self.label_29 = QtWidgets.QLabel(self.header)
        self.label_29.setGeometry(QtCore.QRect(900, 50, 62, 16))
        self.label_29.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_29.setObjectName("label_29")
        self.layoutWidget = QtWidgets.QWidget(self.header)
        self.layoutWidget.setGeometry(QtCore.QRect(41, 81, 730, 29))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_18 = QtWidgets.QLabel(self.layoutWidget)
        self.label_18.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout.addWidget(self.label_18)
        self.partner = QtWidgets.QLineEdit(self.layoutWidget)
        self.partner.setMinimumSize(QtCore.QSize(231, 22))
        self.partner.setMaximumSize(QtCore.QSize(231, 22))
        self.partner.setReadOnly(True)
        self.partner.setObjectName("partner")
        self.horizontalLayout.addWidget(self.partner)
        spacerItem3 = QtWidgets.QSpacerItem(58, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        spacerItem4 = QtWidgets.QSpacerItem(58, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.label_20 = QtWidgets.QLabel(self.layoutWidget)
        self.label_20.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout.addWidget(self.label_20)
        self.courier = QtWidgets.QComboBox(self.layoutWidget)
        self.courier.setObjectName("courier")
        self.horizontalLayout.addWidget(self.courier)
        self.external = QtWidgets.QLineEdit(self.header)
        self.external.setGeometry(QtCore.QRect(430, 150, 171, 20))
        self.external.setObjectName("external")
        self.label = QtWidgets.QLabel(self.header)
        self.label.setGeometry(QtCore.QRect(327, 152, 101, 20))
        self.label.setObjectName("label")
        self.layoutWidget1 = QtWidgets.QWidget(Form)
        self.layoutWidget1.setGeometry(QtCore.QRect(140, 730, 206, 97))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.formLayout = QtWidgets.QFormLayout(self.layoutWidget1)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_33 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_33.setFont(font)
        self.label_33.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_33.setStyleSheet("")
        self.label_33.setObjectName("label_33")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_33)
        self.subtotal_proforma = QtWidgets.QLineEdit(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.subtotal_proforma.setFont(font)
        self.subtotal_proforma.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.subtotal_proforma.setReadOnly(True)
        self.subtotal_proforma.setObjectName("subtotal_proforma")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.subtotal_proforma)
        self.label_34 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_34.setFont(font)
        self.label_34.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_34.setObjectName("label_34")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_34)
        self.proforma_tax = QtWidgets.QLineEdit(self.layoutWidget1)
        self.proforma_tax.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.proforma_tax.setReadOnly(True)
        self.proforma_tax.setObjectName("proforma_tax")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.proforma_tax)
        self.label_35 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_35.setFont(font)
        self.label_35.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_35.setObjectName("label_35")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_35)
        self.proforma_total = QtWidgets.QLineEdit(self.layoutWidget1)
        self.proforma_total.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.proforma_total.setReadOnly(True)
        self.proforma_total.setObjectName("proforma_total")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.proforma_total)
        self.quantity = QtWidgets.QLabel(Form)
        self.quantity.setGeometry(QtCore.QRect(1000, 730, 201, 16))
        self.quantity.setStyleSheet("font:bold; ")
        self.quantity.setTextFormat(QtCore.Qt.AutoText)
        self.quantity.setScaledContents(False)
        self.quantity.setObjectName("quantity")
        self.save = QtWidgets.QPushButton(Form)
        self.save.setGeometry(QtCore.QRect(1070, 901, 75, 31))
        self.save.setObjectName("save")
        self.where_applied_title = QtWidgets.QLabel(Form)
        self.where_applied_title.setGeometry(QtCore.QRect(410, 730, 101, 21))
        self.where_applied_title.setObjectName("where_applied_title")
        self.where_applied_view = QtWidgets.QTableView(Form)
        self.where_applied_view.setGeometry(QtCore.QRect(410, 760, 281, 141))
        self.where_applied_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.where_applied_view.setObjectName("where_applied_view")
        self.where_applied_total = QtWidgets.QLabel(Form)
        self.where_applied_total.setGeometry(QtCore.QRect(414, 910, 271, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.where_applied_total.setFont(font)
        self.where_applied_total.setText("")
        self.where_applied_total.setObjectName("where_applied_total")
        self.label_32 = QtWidgets.QLabel(Form)
        self.label_32.setGeometry(QtCore.QRect(240, 200, 121, 27))
        self.label_32.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_32.setObjectName("label_32")
        self.shipping_address = QtWidgets.QComboBox(Form)
        self.shipping_address.setGeometry(QtCore.QRect(380, 200, 481, 27))
        self.shipping_address.setObjectName("shipping_address")

        self.retranslateUi(Form)
        self.incoterms.setCurrentIndex(1)
        self.cancel.clicked.connect(Form.close) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.type, self.number)
        Form.setTabOrder(self.number, self.date)
        Form.setTabOrder(self.date, self.agent)
        Form.setTabOrder(self.agent, self.they_pay_we_ship)
        Form.setTabOrder(self.they_pay_we_ship, self.they_pay_they_ship)
        Form.setTabOrder(self.they_pay_they_ship, self.we_pay_we_ship)
        Form.setTabOrder(self.we_pay_we_ship, self.partner)
        Form.setTabOrder(self.partner, self.courier)
        Form.setTabOrder(self.courier, self.incoterms)
        Form.setTabOrder(self.incoterms, self.eur)
        Form.setTabOrder(self.eur, self.usd)
        Form.setTabOrder(self.usd, self.tracking)
        Form.setTabOrder(self.tracking, self.view)
        Form.setTabOrder(self.view, self.proforma_total)
        Form.setTabOrder(self.proforma_total, self.proforma_tax)
        Form.setTabOrder(self.proforma_tax, self.subtotal_proforma)
        Form.setTabOrder(self.subtotal_proforma, self.note)
        Form.setTabOrder(self.note, self.cancel)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Credit Note"))
        Form.setToolTip(_translate("Form", "Press Return Key to see the results "))
        self.groupBox.setTitle(_translate("Form", "LINES:"))
        self.cancel.setText(_translate("Form", "Exit"))
        self.note.setPlaceholderText(_translate("Form", "Document Note ... ( Max 255 chars) "))
        self.header.setTitle(_translate("Form", "HEADER"))
        self.label_9.setText(_translate("Form", "Tracking:"))
        self.label_21.setText(_translate("Form", "Type"))
        self.type.setItemText(0, _translate("Form", "1"))
        self.type.setItemText(1, _translate("Form", "2"))
        self.type.setItemText(2, _translate("Form", "3"))
        self.type.setItemText(3, _translate("Form", "4"))
        self.type.setItemText(4, _translate("Form", "5"))
        self.type.setItemText(5, _translate("Form", "6"))
        self.number.setPlaceholderText(_translate("Form", "000000"))
        self.label_22.setText(_translate("Form", "Date:"))
        self.date.setPlaceholderText(_translate("Form", "ddmmyyyy"))
        self.label_24.setText(_translate("Form", "Agent:"))
        self.groupBox_3.setTitle(_translate("Form", "Shipping Costs:"))
        self.they_pay_they_ship.setText(_translate("Form", "They Pay - They Ship"))
        self.we_pay_we_ship.setText(_translate("Form", "We Pay - We Ship"))
        self.they_pay_we_ship.setText(_translate("Form", "They Pay - We Ship"))
        self.label_25.setText(_translate("Form", "Curr.:"))
        self.eur.setText(_translate("Form", "Eur"))
        self.usd.setText(_translate("Form", "Usd"))
        self.incoterms.setItemText(0, _translate("Form", "EXW"))
        self.incoterms.setItemText(2, _translate("Form", "FOB"))
        self.incoterms.setItemText(3, _translate("Form", "CIF"))
        self.incoterms.setItemText(4, _translate("Form", "CIP"))
        self.incoterms.setItemText(5, _translate("Form", "DAP"))
        self.incoterms.setItemText(6, _translate("Form", "DAT"))
        self.label_29.setText(_translate("Form", "Incoterms:"))
        self.label_18.setText(_translate("Form", "Partner:"))
        self.label_20.setText(_translate("Form", "Courier:"))
        self.label.setText(_translate("Form", "External Doc.:"))
        self.label_33.setText(_translate("Form", "Subtotal:"))
        self.label_34.setText(_translate("Form", "Tax:"))
        self.label_35.setText(_translate("Form", "Total "))
        self.quantity.setText(_translate("Form", "Quantity:"))
        self.save.setText(_translate("Form", "Save"))
        self.where_applied_title.setText(_translate("Form", "Where Applied:"))
        self.label_32.setText(_translate("Form", "Shipping Addr:"))
from clipview import ClipView
