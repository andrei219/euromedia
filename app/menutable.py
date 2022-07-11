from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableView


class MenuTable(QTableView):

    def __init__(self, *args, **kwargs):
        super(MenuTable, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        indexes = self.selectedIndexes()
        if not indexes:
            return

    



