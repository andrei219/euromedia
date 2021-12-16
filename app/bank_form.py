

from PyQt5.QtWidgets import (
    QDialog,
    QTableView,
    QMessageBox 
)

from PyQt5.QtCore import QStringListModel

from ui_bank_form import Ui_Dialog 

import utils 
    
import db 
import models 

from PyQt5.QtCore import Qt


class Dialog(Ui_Dialog, QDialog):

    def __init__(self, parent, partner):
        super().__init__(parent=parent)
        self.partner = partner 
        self.setupUi(self)
        self.partner = partner 
        self.model = models.BankAccountModel(partner)
        self.view.setModel(self.model) 

        self.set_handlers()

        self.country.addItems(utils.countries)

        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)

        self.view.setAlternatingRowColors(True)

    def set_handlers(self):
        self.add.clicked.connect(self.add_handler)
        self.delete_.clicked.connect(self.delete_handler) 
        self.save.clicked.connect(self.save_handler) 
        self.exit.clicked.connect(lambda : self.close())


    def clear_fields(self):
        
        for field_name in [
            'name', 'iban', 'swift', 'address', 
            'postcode', 'city', 'state', 'routing_'
        ]:
            try:
                getattr(self, field_name).clear()
            except:
                pass 

    def add_handler(self):
        try:
            self.model.add(
                self.name.text(), self.iban.text(), 
                self.swift.text(), self.address.text(), 
                self.postcode.text(), self.city.text(), 
                self.state.text(), self.country.currentText(), 
                self.routing_.text(), self.currency.text()
            )

            self.clear_fields()
        except:
            raise   
    


    def delete_handler(self):
        rows = {
            index.row() 
            for index in self.view.selectedIndexes()
        }
        if not rows:return 
        row = rows.pop() 
        try:
            self.model.delete(row)
        except:
            raise 
        
        self.view.clearSelection()

    def save_handler(self):
        try:
            db.session.commit()
            QMessageBox.information(self, 'Information', 'Accounts saved/updated successfully')
        except:
            raise 


    def closeEvent(self, event):
        import db 
        db.session.rollback() 
        super().closeEvent(event)