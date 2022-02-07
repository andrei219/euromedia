
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets 

QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)



# def hook(type, value, traceback):
#     print('****************************************') 
#     print(type, value, traceback)

#     sys.__excepthook__(type, value, traceback)


# def exception_hook(exctype, value, traceback):
#     print(exctype, value, traceback) # print exception. 
#     sys._excepthook(exctype, value, traceback) # call original excepthoot. I do not why 
#     sys.exit(1) # terminate program if above do not do this

# sys.excepthook = exception_hook 


# if __name__ == '__main__':

#     print('hook')
#     sys.excepthook = hook


from maingui import MainGui
app = QApplication([])
app.setOrganizationName('Euromedia Investment Group, S.L.')
app.setApplicationVersion('1.0')

maingui = MainGui()
maingui.show()
sys.exit(app.exec_())
