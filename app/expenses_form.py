

from PyQt5.QtWidgets import QDialog, QTableView, QMessageBox
from PyQt5.QtCore import Qt

from ui_expenses_form import Ui_ExpenseForm

from utils import parse_date
from models import ExpenseModel

class ExpenseForm(Ui_ExpenseForm, QDialog):
    def __init__(self, parent, proforma, sale=False):
        super().__init__(parent)
        self.setupUi(self)
        self.proforma = proforma
        self.model = ExpenseModel(proforma, sale)
        self.view.setModel(self.model) 
        self.add_button.pressed.connect(self.addExpense)
        self.delete_button.pressed.connect(self.deleteExpenses) 

        self.view.setSelectionBehavior(QTableView.SelectRows)  
        self.view.setSortingEnabled(True)

        self.populate()     
    
    def addExpense(self):
        try:
            date = parse_date(self.date_line_edit.text())
        except:
            QMessageBox.critical(self, 'Erro - Update', 'Date must be: ddmmyyyy')
            return
        
        try:
            amount = self.amount.text().replace(',', '.')
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', \
                'Error amount format. Enter a valid decimal number')
            return 
        
        info = self.info_lineedit.text() 
        
        try:
            self.model.add(date, amount, info)
            # self.view.resizeColumnsToContents()
            self.updateSpent()
            self.clearFields()
        except:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not add expense')

    def deleteExpenses(self):
        indexes = self.view.selectedIndexes() 
        if not indexes:
            return
        try:
            self.model.delete(indexes)
            # self.view.resizeColumnsToContents() 
            self.updateSpent() 
        except:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not delete expenses')

    def updateSpent(self):
        self.spent_line_edit.setText(str(self.model.spent)) 

    def keyPressEvent(self, event):
        if self.add_button.hasFocus() and event.key() == Qt.Key_Return:
            self.addExpense() 
        else:
            super().keyPressEvent(event)

    def clearFields(self):
        self.date_line_edit.clear()
        self.amount.clear() 
        self.info_lineedit.clear()

    def populate(self):
        try:
            type = self.proforma.invoice.type 
            number = self.proforma.invoice.number
        except AttributeError:
            type = self.proforma.type
            number = self.proforma.number
        
        doc_number = str(type) + '-' + str(number).zfill(6)
        self.document_line_edit.setText(doc_number)
        self.document_date_line_edit.setText(self.proforma.date.strftime('%d/%m/%Y'))
        self.partner_line_edit.setText(self.proforma.partner.fiscal_name)
        self.updateSpent() 

    def closeEvent(self, event):
        import db
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise 
