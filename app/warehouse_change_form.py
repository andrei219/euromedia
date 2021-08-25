from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox
from PyQt5.QtCore import Qt, QStringListModel

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from ui_warehouse_change_form import Ui_WarehouseChange

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

import db


class WarehouseChange(Ui_WarehouseChange, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self) 

        self.session = db.Session() 

        self.setUp()

    
    def setUp(self):
        self.exit.clicked.connect(self.close)
        self.update.clicked.connect(self.updateHandler)
        self.sn.setFocus() 

        self.warehouses_name_to_id = {r.description: r.id for r in self.session.query(db.Warehouse.description, db.Warehouse.id)}
        self.warehouses_name_to_id[''] = 0 

        self.new_warehouse.addItems(self.warehouses_name_to_id.keys())

        self.new_warehouse.setCurrentText('')

    
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Return and self.sn.hasFocus():
            self.searchAndPopulate() 

    
    def searchAndPopulate(self):
        try:
            self.db_result = self.session.query(db.Imei).join(db.Item).join(db.Warehouse).where(db.Imei.imei == self.sn.text()).one() 

            self.description.setText(str(self.db_result.item))
            self.current_warehouse.setText(self.db_result.warehouse.description)

        except NoResultFound:
            QMessageBox.critical(self, 'Search Error', 'No IMEI/SN was found')
            return
        except MultipleResultsFound:
            QMessageBox.critical(self, 'FATAL-ERROR', 'Call the developer')
            return


    def reset(self):
        self.sn.setText('')
        self.new_warehouse.setCurrentText('') 
        self.description.setText('')
        self.current_warehouse.setText('')
        self.sn.setFocus()

    def updateHandler(self):
        try:
            self.db_result
        except AttributeError:
            return 
        if self.db_result.imei != self.sn.text():
            QMessageBox.critical(self, 'Error', 'Imei/SN field was changed')
            return 
        if self.db_result.warehouse.description == self.new_warehouse.currentText() or \
            not self.new_warehouse.currentText():
            return

        self.db_result.warehouse_id = self.warehouses_name_to_id[self.new_warehouse.currentText()]

        try:
            self.session.commit() 
            self.reset() 
        except:
            raise             



        
