
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableView

from PyQt5.QtCore import Qt

from ui_payments_form import Ui_PaymentsForm

from utils import parse_date, today_date

from models import PaymentModel
from models import caches_clear


class PaymentForm(Ui_PaymentsForm, QDialog):

    def __init__(self, parent, proforma, sale=False):
        super().__init__(parent) 
        self.setupUi(self) 
        self.proforma = proforma
        self.model = PaymentModel(proforma, sale, self) 
        self.view.setModel(self.model) 
        self.is_credit_note = self.proforma.warehouse_id is None

        self.add_payment_tool_button.clicked.connect(self.addHandler)
        self.delete_payment_tool_button.clicked.connect(self.deleteHandler)
        self.all.clicked.connect(lambda: self.amount.setText(str(self.proforma.owing)))

        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSortingEnabled(True)
        self.populate()

        self.date_line_edit.setText(today_date())

        # enable rate:

        self.rate.setEnabled(not self.proforma.eur_currency)
        self.rate.setText('1.0')


    def addHandler(self):
        try:
            date = parse_date(self.date_line_edit.text())
        except:
            QMessageBox.critical(self, 'Erro - Update', 'Date must be: ddmmyyyy')
            return 
        
        try:
            amount = self.amount.text().replace(',', '.') 

            amount = float(amount)
        
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', 'Error amount format. Enter a valid decimal number')
            return 

        try:
            rate = self.rate.text().replace(',', '.') 
            rate = float(rate)
        
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', 'Error rate format. Enter a valid decimal number')
            return 

        info = self.info_lineedit.text()

        try:
            self.model.add(date, amount, rate, info)
            self.view.resizeColumnToContents(2) 
            self.updateOwing()
            self.clearFields() 

        except Exception as ex:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not add payment')
        else:
            caches_clear()

    def deleteHandler(self):
        indexes = self.view.selectedIndexes()
        if not indexes:
            return 
        try:
            self.model.delete(indexes)
            self.view.resizeColumnToContents(2) 
            self.view.clearSelection() 
            self.updateOwing()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error - Update', str(ex))
        else:
            caches_clear()

    def updateOwing(self):
        self.owing_lineedit.setText(str(self.proforma.owing))

    def clearFields(self):
        # self.date_line_edit.clear() 
        self.amount.clear()
        self.info_lineedit.clear() 

    def keyPressEvent(self, event):
        if self.add_payment_tool_button.hasFocus():
            if event.key() == Qt.Key_Return:
                self.addHandler() 
        else:
            super().keyPressEvent(event) 

    def populate(self):
        self.document_line_edit.setText(self.proforma.doc_repr)
        self.partner_line_edit.setText(self.proforma.partner_name)
        self.document_date_line_edit.setText(self.proforma.date.strftime('%d/%m/%Y'))

        self.total_linedit.setText(str(self.proforma.total_debt))
        self.owing_lineedit.setText(str(self.proforma.total_debt - self.proforma.total_paid))

    def closeEvent(self, event):
        import db
        try:
            db.session.commit()
        except:
            db.session.rollback()  
            raise
        super().closeEvent(event)

    @property
    def total(self):
        return sum([line.price * line.quantity for line in self.proforma.lines])

    @property
    def paid(self):
        return self.model.paid