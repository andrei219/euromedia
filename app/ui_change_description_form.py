# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\uis\change_description_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(579, 284)
        self._from = QtWidgets.QLineEdit(Dialog)
        self._from.setGeometry(QtCore.QRect(110, 90, 441, 20))
        self._from.setAlignment(QtCore.Qt.AlignCenter)
        self._from.setReadOnly(True)
        self._from.setObjectName("_from")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(49, 90, 41, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(60, 130, 31, 21))
        self.label_2.setObjectName("label_2")
        self.to = QtWidgets.QLineEdit(Dialog)
        self.to.setGeometry(QtCore.QRect(110, 130, 441, 20))
        self.to.setAlignment(QtCore.Qt.AlignCenter)
        self.to.setObjectName("to")
        self.apply = QtWidgets.QPushButton(Dialog)
        self.apply.setGeometry(QtCore.QRect(260, 170, 101, 31))
        self.apply.setAutoDefault(False)
        self.apply.setDefault(False)
        self.apply.setObjectName("apply")
        self.exit = QtWidgets.QToolButton(Dialog)
        self.exit.setGeometry(QtCore.QRect(500, 210, 41, 51))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.exit.setFont(font)
        self.exit.setStyleSheet("background:lightgray; ")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/exit"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exit.setIcon(icon)
        self.exit.setIconSize(QtCore.QSize(50, 50))
        self.exit.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.exit.setObjectName("exit")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 50, 31, 16))
        self.label_3.setObjectName("label_3")
        self.serie = QtWidgets.QLineEdit(Dialog)
        self.serie.setGeometry(QtCore.QRect(110, 50, 441, 20))
        self.serie.setAlignment(QtCore.Qt.AlignCenter)
        self.serie.setObjectName("serie")

        self.retranslateUi(Dialog)
        self.exit.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Change Description"))
        self.label.setText(_translate("Dialog", "From:"))
        self.label_2.setText(_translate("Dialog", "To:"))
        self.apply.setText(_translate("Dialog", "Apply Change"))
        self.exit.setText(_translate("Dialog", "Exit"))
        self.label_3.setText(_translate("Dialog", "Serie:"))
        self.serie.setPlaceholderText(_translate("Dialog", "Enter serial number and press Enter key"))
import icons_rc
