from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListView
from alembic.command import current

from clipboard import ClipBoard



import PyQt5.QtCore

class ClipView_old(QTableView):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            clipboard = ClipBoard()
            current = self.selectionModel().currentIndex()
            data = self.model().data(current, role=Qt.DisplayRole)
            clipboard.data = data
        else:
            super().mousePressEvent(e)


class ClipView(QTableView):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            app = PyQt5.QtCore.QCoreApplication.instance()
            local_clipboard = ClipBoard()
            current = self.selectionModel().currentIndex()
            data = self.model().data(current, role=Qt.DisplayRole)
            local_clipboard.data = data
            app.clipboard().setText(data)

        else:
            super().mousePressEvent(e)

class ClipLineEdit(QLineEdit):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        print('Mosuse Press event catched')
        if e.button() == Qt.RightButton:
            app = PyQt5.QtCore.QCoreApplication.instance()
            global_text = app.clipboard().text()
            if global_text:
                print
                self.setText(global_text)
            else:
                local_text = ClipBoard()
                if local_text:
                    self.setText(local_text)
        else:
            super().mousePressEvent(e)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        pass


class ClipListView(QListView):

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            app = PyQt5.QtCore.QCoreApplication.instance()
            local_clipboard = ClipBoard()
            current = self.selectionModel().currentIndex()
            data = self.model().data(current, role=Qt.DisplayRole)
            local_clipboard.data = data
            app.clipboard().setText(data)
        else:
            super().mousePressEvent(e)


