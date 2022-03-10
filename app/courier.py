
from PyQt5.QtWidgets import QDialog, QMessageBox


from ui_courier import Ui_CourierForm

from models import CourierListModel

class CourierForm(QDialog, Ui_CourierForm):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.model = CourierListModel()
        self.view.setModel(self.model)
        self.add.clicked.connect(self.add_handler)
        self.delete_2.clicked.connect(self.delete_handler)
        self.input.setFocus(True) 

    
    def add_handler(self):
        name = self.input.text().strip()
        if not name:
            return
        try:
            self.model.add(name)
        except ValueError:
            return 
    
    def delete_handler(self):
        index = self.view.currentIndex()
        if index:
            try:
                self.model.delete(index.row())
            except:
                raise 
