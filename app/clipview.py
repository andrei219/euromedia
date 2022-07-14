from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListView




from clipboard import ClipBoard


class ClipView(QTableView):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            clipboard = ClipBoard()
            current = self.selectionModel().currentIndex()
            data = self.model().data(current, role=Qt.DisplayRole)
            clipboard.data = data
        else:
            super().mousePressEvent(e)


class ClipLineEdit(QLineEdit):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            self.setText(ClipBoard().data)
        else:
            super().mousePressEvent(e)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        pass

class ClipListView(QListView):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            current = self.selectionModel().currentIndex()
            data = self.model().data(current, role=Qt.DisplayRole)
            ClipBoard().data = data
        else:
            super().mousePressEvent(e)