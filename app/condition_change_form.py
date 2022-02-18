
from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox
from PyQt5.QtCore import Qt, QStringListModel

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from ui_condition_change_form import Ui_ConditionChange

import db

class ConditionChange(Ui_ConditionChange, QDialog):
    
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self) 
        self.setUp()         
        

    def setUp(self):
        self.exit.clicked.connect(self.close)
        self.update.clicked.connect(self.updateHandler) 
        self.sn.setFocus()


        conditions = { r[0] for r in db.session.query(db.PurchaseProformaLine.condition).distinct()}.\
            union({r[0] for r in db.session.query(db.Imei.condition).distinct()})

        m = QStringListModel()
        m.setStringList(conditions)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.new_condition.setCompleter(c)

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
        if self.db_result.condition == self.new_condition.text() or \
            not self.new_condition.text():
            return

        self.db_result.condition = self.new_condition.text() 
        try:
            db.session.commit() 
            self.reset() 
        except:
            raise             

    def reset(self):
        self.sn.setText('')
        self.new_condition.setText('')
        self.description.setText('')
        self.current_condition.setText('')
        self.sn.setFocus()
    
    def searchAndPopulate(self):
        try:
            self.db_result = db.session.query(db.Imei).join(db.Item).where(db.Imei.imei == self.sn.text()).one() 
            self.description.setText(str(self.db_result.item.clean_repr))
            self.current_condition.setText(self.db_result.condition)
        except NoResultFound:
            QMessageBox.critical(self, 'Search Error', 'No IMEI/SN was found')
            return
        except MultipleResultsFound:
            QMessageBox.critical(self, 'FATAL-ERROR', 'Call the developer')
            return 
