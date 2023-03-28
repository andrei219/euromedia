from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget, QCompleter, QLineEdit, QItemDelegate

from PyQt5.QtCore import Qt

from utils import warehouse_id_map, description_id_map, partner_id_map
from utils import conditions

def create_completer(parent, items):
    editor = QLineEdit(parent)
    completer = QCompleter(items)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    editor.setCompleter(completer)
    return editor

class RepairDelegate(QStyledItemDelegate):
    ITEM, PARTNER = 1, 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == self.ITEM:
            return create_completer(parent, description_id_map.keys())
        elif index.column() == self.PARTNER:
            return create_completer(parent, partner_id_map.keys())
        return super().createEditor(parent, option, index)

class WhRmaDelegate(QItemDelegate):

    WAREHOUSE, TARGET_CONDITION = 7, 8

    def __init__(self, parent=None):
        super(WhRmaDelegate, self).__init__(parent)
from db import Account, JournalEntry


def create_completer(parent, items):
    editor = QLineEdit(parent)
    completer = QCompleter(items)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    editor.setCompleter(completer)
    return editor


class WhRmaDelegate(QItemDelegate):
    WAREHOUSE, TARGET_CONDITION = 7, 8

    def __init__(self, parent=None):
        super(WhRmaDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == self.WAREHOUSE:
            return self.create_completer(parent, warehouse_id_map.keys())
        elif index.column() == self.TARGET_CONDITION:
            return create_completer(parent, conditions)
        return super().createEditor(parent, option, index)


class JournalEntryTypeDelegate(QItemDelegate):
    TYPE = 3

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == self.TYPE:
            return create_completer(parent, JournalEntry.RELATED_TYPES)
        return super().createEditor(parent, option, index)


class AccountDelegate(QItemDelegate):
    ACCOUNT = 0

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index) -> QWidget:
        if index.column() == self.ACCOUNT:
            return create_completer(parent, Account.get_leaf_accounts_map().keys())
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
