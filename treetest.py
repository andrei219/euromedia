from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex, QVariant
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QTreeView, QMainWindow, QWidget, QVBoxLayout

class SaleProformaLineModel(QStandardItemModel):
    def __init__(self, lines, parent=None):
        super().__init__(parent)
        self._groups = {}
        for line in lines:
            mix_id = line.mix_id
            if mix_id not in self._groups:
                group = QStandardItem(mix_id)
                self.appendRow(group)
                self._groups[mix_id] = group
            item = QStandardItem()
            item.setData(line.item_id, Qt.UserRole + 1)
            item.setData(line.condition, Qt.UserRole + 2)
            item.setData(line.spec, Qt.UserRole + 3)
            item.setData(line.price, Qt.UserRole + 4)
            item.setText(line.description)
            self._groups[mix_id].appendRow(item)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            index = self.itemFromIndex(index)
            return index.text()


    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 6


class GroupedSalesWidget(QMainWindow):
    def __init__(self, lines):
        super().__init__()
        self.setWindowTitle("Grouped Sales Widget")
        self.setGeometry(100, 100, 400, 400)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setModel(SaleProformaLineModel(lines))
        layout.addWidget(self.tree_view)

if __name__ == '__main__':
    app = QApplication([])

    from collections import namedtuple

    Line = namedtuple('Line', ['item_id', 'description', 'condition', 'spec', 'price', 'mix_id'])

    lines = [
        Line('1', 'Item 1', 'New', 'Spec 1', 100, 'Mix 1'),
        Line('2', 'Item 2', 'New', 'Spec 1', 100, 'Mix 1'),
        Line('3', 'Item 3', 'New', 'Spec 1', 100, 'Mix 1'),
        Line('4', 'Item 4', 'New', 'Spec 1', 100, 'Mix 1'),
        Line('5', 'Item 5', 'New', 'Spec 1', 100, 'Mix 2'),
        Line('6', 'Item 6', 'New', 'Spec 1', 100, 'Mix 2'),
        Line('7', 'Item 7', 'New', 'Spec 1', 100, 'Mix 2'),
        Line('8', 'Item 8', 'New', 'Spec 1', 100, 'Mix 2'),
        Line('9', 'Item 9', 'New', 'Spec 1', 100, 'Mix 3'),
        Line('10', 'Item 10', 'New', 'Spec 1', 100, 'Mix 3'),
        Line('11', 'Item 11', 'New', 'Spec 1', 100, 'Mix 3'),
        Line('12', 'Item 12', 'New', 'Spec 1', 100, 'Mix 4'),
        Line('13', 'Item 13', 'New', 'Spec 1', 100, 'Mix 4'),
        Line('14', 'Item 14', 'New', 'Spec 1', 100, 'Mix 4'),
        Line('15', 'Item 15', 'New', 'Spec 1', 100, 'Mix 4'),
    ]

    widget = GroupedSalesWidget(lines)
    widget.show()

    app.exec_()


