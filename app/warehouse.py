
from sqlalchemy.exc import IntegrityError

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_warehouse import Ui_WarehouseForm

from models import WarehouseListModel

class Form(Ui_WarehouseForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.model = WarehouseListModel() 
        self.view.setModel(self.model)
        self.exit.clicked.connect(lambda : self.close)
        self.add.clicked.connect(self.add_handler)
        self.delete_2.clicked.connect(self.delete_handler)
    
    def add_handler(self):
        warehouse_name = self.input.text().strip() 
        if not warehouse_name:
            return
        try:
            self.model.add(warehouse_name)
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', 'Warehouse already exists')
            return
        else:
            self.input.clear() 

    def delete_handler(self):
        current_index = self.view.currentIndex()
        if current_index:
            try:
                self.model.delete(current_index.row())  
            except IntegrityError:
                QMessageBox.critical(self, 'Error - Update', 'This warehouse has data associated. Can not delete')