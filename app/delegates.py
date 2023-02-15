from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QCompleter, QLineEdit, QItemDelegate
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

from utils import warehouse_id_map
from utils import conditions

class WhRmaDelegate(QItemDelegate):
    WAREHOUSE, TARGET_CONDITION = 7, 8
    def __init__(self, parent=None):
        super(WhRmaDelegate, self).__init__(parent)

    def create_completer(self, parent, items):
        editor = QLineEdit(parent)
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        editor.setCompleter(completer)
        return editor

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == self.WAREHOUSE:
            return self.create_completer(parent, warehouse_id_map.keys())
        elif index.column() == self.TARGET_CONDITION:
            return self.create_completer(parent, conditions)
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
        if index.column() == self.column:
            editor.setText(index.data(Qt.DisplayRole))
