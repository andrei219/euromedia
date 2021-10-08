from sqlalchemy.exc import IntegrityError

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_condition import Ui_ConditionForm

from models import ConditionListModel


class Form(Ui_ConditionForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.model = ConditionListModel() 
        self.view.setModel(self.model)
        self.exit.clicked.connect(lambda : self.close)
        self.add.clicked.connect(self.add_handler)
        self.delete_2.clicked.connect(self.delete_handler)
    

    def add_handler(self):
        condition_name = self.input.text().strip() 
        if not condition_name:
            return
        try:
            self.model.add(condition_name)
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', \
                'Warehouse already exists')
            return
        else:
            self.input.clear() 

    def delete_handler(self):
        current_index = self.view.currentIndex()
        if current_index:
            try:
                self.model.delete(current_index.row())  
            except : raise 