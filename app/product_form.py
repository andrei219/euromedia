
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QCompleter, QMessageBox, QTableView

from PyQt5.QtWidgets import QDialog

from ui_product_form import Ui_ProductForm

from models import ProductModel
from utils import setCommonViewConfig


from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db import session, Item

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

        # setCommonViewConfig(self.product_view)
        self.product_view.setSortingEnabled(True)
        self.product_view.setAlternatingRowColors(True)
        self.product_view.setSelectionBehavior(QTableView.SelectRows)


        self.setUpCompleters() 

    def setUpCompleters(self):

        from utils import setCompleter


        for field, data in [
            (self.mpn, {item.mpn for item in self.model}), 
            (self.manufacturer_line_edit, {item.manufacturer for item in self.model}), 
            (self.category_line_edit, {item.category for item in self.model}), 
            (self.model_line_edit, {item.model for item in self.model}), 
            (self.capacity_line_edit, {item.capacity for item in self.model}), 
            (self.color_line_edit, {item.color for item in self.model}), 
        ]: 
            setCompleter(field, data) 

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
            
        self.setUpCompleters()      

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


        self.setUpCompleters()

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
        
        text = ''.join((
            self.manufacturer_line_edit.text().lower(), 
            self.mpn.text().lower(), self.category_line_edit.text().lower(), 
            self.model_line_edit.text(), self.capacity_line_edit.text().lower(), 
            self.color_line_edit.text().lower()
        ))

        if '|' in text or '?' in text or 'Mix' in text:
            QMessageBox.critical(self, 'Error', "Fields can't contain ? or | symbols or Mix/Mixed words")
            return False
        
        try:
            self.validate_subsets_mpn()
        except ValueError as ex:
            QMessageBox.critical(self,'Error', str(ex))
            return False

        return True

    def validate_subsets_mpn(self):

        incompatible = 'Incompatible Product'

        mpn, man, cat, mod, cap, col, has_serie = \
            self.mpn.text().strip(), self.manufacturer_line_edit.text().strip(), self.category_line_edit.text().strip(),\
                self.model_line_edit.text().strip(), self.capacity_line_edit.text().strip(),\
                    self.color_line_edit.text().strip(), self.has_serie.isChecked()
        
        base = lambda item: (item.manufacturer, item.category, item.model) == (man, cat, mod) 

        if cap and not has_serie:
            raise ValueError('If product has capacity it must have serie')
        
        for item in self.model:
                if mpn == item.mpn != '':
                    raise ValueError(f"Mpn:{mpn} already exists, it cannot be duplicated")

        if not cap and not col:
            if list(filter(base, self.model)):
                raise ValueError(f"Product: {man} {cat} {mod} already exists")
            return True 
        
        elif not cap and col:
            if all((
                item.color and not item.capacity
                for item in filter(base, self.model)
            )):
                return True
            raise ValueError(incompatible) 

        elif cap and not col:
            if all((
                item.capacity and not item.color
                for item in filter(base, self.model) 
            )):
                return True
            raise ValueError(incompatible)
        elif cap and col:
            if all((
                item.color and item.capacity
                for item in filter(base, self.model)
            )):
                return True
            raise ValueError(incompatible)