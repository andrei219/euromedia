
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets 
import icons

from maingui import MainGui

QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication([])
app.setOrganizationName('Euromedia Investment Group, S.L.')
app.setApplicationVersion('1.0')
maingui = MainGui()
maingui.show()
sys.exit(app.exec_())

