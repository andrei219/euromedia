
from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox
from PyQt5.QtCore import Qt, QStringListModel

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from ui_spec_change_form import Ui_SpecChange

import db

class SpecChange(Ui_SpecChange, QDialog):
    
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self) 

        self.session = db.Session()

        self.setUp()         
        

    def setUp(self):
        self.exit.clicked.connect(self.close)
        self.update.clicked.connect(self.updateHandler) 
        self.sn.setFocus()


        specs = { r[0] for r in self.session.query(db.PurchaseProformaLine.specification).distinct()}.\
            union({r[0] for r in self.session.query(db.Imei.specification).distinct()})

        m = QStringListModel()
        m.setStringList(specs)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.new_spec.setCompleter(c)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.sn.hasFocus():
            self.searchAndPopulate() 
        
    
    def updateHandler(self):
        try:
            self.db_result
        except AttributeError:
            return 
        if self.db_result.imei != self.sn.text():
            QMessageBox.critical(self, 'Error', 'Imei/SN field was changed')
            return 
        if self.db_result.specification == self.new_spec.text() or \
            not self.new_spec.text():
            return

        self.db_result.specification = self.new_spec.text() 
        try:
            self.session.commit() 
            self.reset() 
        except:
            raise             

    def reset(self):
        self.sn.setText('')
        self.new_spec.setText('')
        self.description.setText('')
        self.current_spec.setText('')
        self.sn.setFocus()
    
    def searchAndPopulate(self):
        try:
            self.db_result = self.session.query(db.Imei).join(db.Item).where(db.Imei.imei == self.sn.text()).one() 

            self.description.setText(str(self.db_result.item))
            self.current_spec.setText(self.db_result.specification)

        except NoResultFound:
            QMessageBox.critical(self, 'Search Error', 'No IMEI/SN was found')
            return
        except MultipleResultsFound:
            QMessageBox.critical(self, 'FATAL-ERROR', 'Call the developer')
            return 