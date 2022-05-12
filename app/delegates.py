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


