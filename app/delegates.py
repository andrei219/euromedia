from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QCompleter, QLineEdit, QItemDelegate
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

from utils import warehouse_id_map


class WhDelegate(QItemDelegate):
    
    def __init__(self, parent=None):
        super(WhDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == 7:
            editor = QLineEdit(parent)
            completer = QCompleter(warehouse_id_map.keys())
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            editor.setCompleter(completer)
            return editor
        else:
            return super().createEditor(parent, option, index)


class WarningEditDelegate(QItemDelegate):

    def __init__(self, *, parent, column):
        super().__init__(parent=parent)
        self.column = column

    def createEditor(self, parent, option, index):
        if index.column() == self.column:
            return QLineEdit(parent)
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        print(f'self.column={self.column}')
        if index.column() == self.column:
            print(f'index.data(Qt.DisplayRole) = {index.data(Qt.DisplayRole)}')
            editor.setText(index.data(Qt.DisplayRole))
