
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableView

from PyQt5.QtCore import Qt

from ui_payments_form import Ui_PaymentsForm

from utils import parse_date

from models import PaymentModel

class PaymentForm(Ui_PaymentsForm, QDialog):

    def __init__(self, parent, proforma, sale=False):
        super().__init__(parent) 
        self.setupUi(self) 
        self.proforma = proforma
        self.model = PaymentModel(proforma, sale) 
        self.view.setModel(self.model) 

        self.add_payment_tool_button.pressed.connect(self.addHandler) 
        self.delete_payment_tool_button.pressed.connect(self.deleteHandler)

        self.view.setSelectionBehavior(QTableView.SelectRows)

        self.populate()

        if self.proforma.cancelled:
            self.setEnabled(False) 

    def addHandler(self):
        try:
            date = parse_date(self.date_line_edit.text())
        except:
            QMessageBox.critical(self, 'Erro - Update', 'Date must be: ddmmyyyy')
            return 
        
        amount = self.amount_spin_box.value() 
        info = self.info_lineedit.text() 

        try:
            self.model.add(date, amount, info)
            # self.view.resizeColumnsToContents() 
            self.updateOwing()
            self.clearFields() 

        except:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not add payment')
    
    def deleteHandler(self):
        indexes = self.view.selectedIndexes()
        if not indexes:
            return 
        try:
            self.model.delete(indexes)
            # self.view.resizeColumnsToContents() 
            self.view.clearSelection() 
            self.updateOwing()
        except:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not delete payments')

    def updateOwing(self):
        self.owing = self.total - self.paid
        self.owing_lineedit.setText(str(self.owing))

    def clearFields(self):
        self.date_line_edit.setText('')
        self.amount_spin_box.setValue(0)
        self.info_lineedit.setText('')

    def keyPressEvent(self, event):
        if self.add_payment_tool_button.hasFocus():
            if event.key() == Qt.Key_Return:
                self.addHandler() 
        else:
            super().keyPressEvent(event) 

    def populate(self):
        document_number = str(self.proforma.type) + '-' + str(self.proforma.number).zfill(6)
        self.document_line_edit.setText(document_number)
        self.partner_line_edit.setText(self.proforma.partner.fiscal_name)
        self.document_date_line_edit.setText(self.proforma.date.strftime('%d/%m/%Y'))

        self.total_linedit.setText(str(float(self.total)))

        self.owing_lineedit.setText(str(float(self.total) - float(self.paid)))

    @property
    def total(self):
        return sum([line.price * line.quantity for line in self.proforma.lines])

    @property
    def paid(self):
        return self.model.paid