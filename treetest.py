import sys
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QApplication, QTreeView, QMainWindow, QWidget

multiples = {4: [4, 8, 16, 20], 6: [6, 12, 18, 24], 8: [8, 16, 24, 32], 10: [10, 20, 30, 40]}

class TreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.rootItem = QStandardItem('Root')
        self.setupModelData(data)

    def setupModelData(self, data):
        for key in data:
            parent = QStandardItem(str(key))
            self.rootItem.appendRow(parent)
            for value in data[key]:
                child = QStandardItem(str(value))
                parent.appendRow(child)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.rowCount()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.text()
        return QVariant()

class TreeViewExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle("PyQt TreeView Example")
        self.initUI()

    def initUI(self):
        self.model = TreeModel(multiples)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.setCentralWidget(self.tree)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TreeViewExample()
    ex.show()
    sys.exit(app.exec_())
