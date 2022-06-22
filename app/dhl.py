import typing

from ui_dhl import Ui_Form

from PyQt5.QtWidgets import QDialog

from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtCore import Qt

class ListModel(QAbstractListModel):

    def __init__(self, data):
        super().__init__()
        self._items = data

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._items)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self._items[index.row()]


class Form(Ui_Form, QDialog):
    def __init__(self, parent, resolved, unresolved):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)

        self.resolved.setModel(ListModel(resolved))
        self.notresolved.setModel(ListModel(unresolved))
