from sqlalchemy.exc import IntegrityError

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_spec import Ui_SpecForm

from models import SpecListModel


class Form(Ui_SpecForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.model = SpecListModel() 
        self.view.setModel(self.model)
        self.exit.clicked.connect(lambda : self.close)
        self.add.clicked.connect(self.add_handler)
        self.delete_2.clicked.connect(self.delete_handler)
    

    def add_handler(self):
        spec_name = self.input.text().strip() 
        if not spec_name:
            return
        try:
            self.model.add(spec_name)
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', \
                'Spec already exists')
            return
        else:
            self.input.clear() 

    def delete_handler(self):
        current_index = self.view.currentIndex()
        if current_index:
            try:
                self.model.delete(current_index.row())  
            except: raise 