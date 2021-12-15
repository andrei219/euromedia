
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QCompleter, QMessageBox

from PyQt5.QtWidgets import QDialog

from ui_product_form import Ui_ProductForm

from models import ProductModel
from utils import setCommonViewConfig


from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db import engine, Item

class ProductForm(Ui_ProductForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.model = ProductModel() 
        self.product_view.setModel(self.model)

        # connect slots:
        self.add_product_tool_button.clicked.connect(self.addItemHandler) 
        self.delete_tool_button.clicked.connect(self.removeItemHandler) 
    
        # configure view: 

        setCommonViewConfig(self.product_view)

        self.setUpCompleters() 

    def setUpCompleters(self):

        from utils import setCompleter

        setCompleter(
            self.mpn, 
            [r[0] for r in engine.execute(select(Item.mpn).distinct())]
        )

        manufacturers = [r[0] for r in engine.execute(select(Item.manufacturer).distinct())]
        manufacturerModel = QStringListModel(manufacturers)
        completer = QCompleter()
        completer.setModel(manufacturerModel)
        completer.setCaseSensitivity(False)

        self.manufacturer_line_edit.setCompleter(completer)

        categories = [r[0] for r in engine.execute(select(Item.category).distinct())]
        model = QStringListModel(categories)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(False)

        self.category_line_edit.setCompleter(completer)

        models = [r[0] for r in engine.execute(select(Item.model).distinct())]
        model = QStringListModel(models)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(False)
        self.model_line_edit.setCompleter(completer) 

        capacities = [r[0] for r in engine.execute(select(Item.capacity).distinct())]
        model = QStringListModel(capacities)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(False)
        self.capacity_line_edit.setCompleter(completer)

        colors = [ r[0] for r in engine.execute(select(Item.color).distinct()) ]
        model = QStringListModel(colors)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(False)
        self.color_line_edit.setCompleter(completer)

    def clearFields(self):
        self.mpn.clear()
        self.manufacturer_line_edit.setText('')
        self.category_line_edit.setText('')
        self.model_line_edit.setText('')
        self.capacity_line_edit.setText('')
        self.color_line_edit.setText('')

    def keyPressEvent(self, event):
        
        if self.add_product_tool_button.hasFocus():
            if event.key() == Qt.Key_Return:
                self.addItemHandler() 
                self.manufacturer_line_edit.setFocus() 
        else:
            super().keyPressEvent(event)

    def addItemHandler(self):
        if not self.validProduct():
            return 
        try:
            self.model.addItem(self.mpn.text(), self.manufacturer_line_edit.text(), self.category_line_edit.text(), \
                self.model_line_edit.text(), self.capacity_line_edit.text(), \
                    self.color_line_edit.text(), self.has_serie.isChecked())
            self.clearFields() 
            # self.product_view.resizeColumnsToContents() 
        except IntegrityError as e:
            code = e.orig.args[0] 
            if code == 1062:
                QMessageBox.critical(self, 'Error - Update', 'That product already exists')
            
    def removeItemHandler(self):
        indexes = self.product_view.selectedIndexes() 
        if indexes:
            index = indexes[0]
            try:
                self.model.removeItem(index)
                self.product_view.clearSelection()
                # self.product_view.resizeColumnsToContents()  
            except IntegrityError as e:
                code = e.orig.args[0]
                if code == 1451:
                    QMessageBox.critical(self, 'Error - Update', 'That product has data associated')

    def validProduct(self):
        if not all((
            self.manufacturer_line_edit.text(), 
            self.model_line_edit.text(), 
            self.category_line_edit.text()
        )):
            QMessageBox.critical(
                self, 
                'Error', 
                'Manufacturer, category, model are mandatory fields'
            )
            return False
        return True 