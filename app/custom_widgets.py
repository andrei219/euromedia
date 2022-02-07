

from PyQt5.QtWidgets import QComboBox, QCompleter
from PyQt5.QtCore import pyqtSignal, QStringListModel
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

class CustomComboBox(QComboBox):

    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setMaxVisibleItems(20)
        completer = QCompleter(self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(completer)
        self.setInsertPolicy(self.__class__.InsertAtTop)
    
    def replace_items(self, data):
        self.clear()
        self.addItems(data)
        model = QStringListModel(data)
        self.completer().setModel(model) 

    def text(self):
        return self.currentText()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.returnPressed.emit()
        else:
            super().keyPressEvent(e)

