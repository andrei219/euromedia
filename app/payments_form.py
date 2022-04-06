
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableView

from PyQt5.QtCore import Qt

from ui_payments_form import Ui_PaymentsForm

from utils import parse_date, today_date

from models import PaymentModel

class PaymentForm(Ui_PaymentsForm, QDialog):

    def __init__(self, parent, proforma, sale=False):
        super().__init__(parent) 
        self.setupUi(self) 
        self.proforma = proforma
        self.model = PaymentModel(proforma, sale, self) 
        self.view.setModel(self.model) 

        self.add_payment_tool_button.clicked.connect(self.addHandler) 
        self.delete_payment_tool_button.clicked.connect(self.deleteHandler)
        self.all.clicked.connect(lambda:self.amount.setText(str(self.total - self.paid)))

        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSortingEnabled(True)
        self.populate()

        self.date_line_edit.setText(today_date())


        # enable rate:

        self.rate.setEnabled(not self.proforma.eur_currency)
        self.rate.setText('0.0')


    def allclicked(self):
        self.amount.setText(str(self.total - self.paid))


    def addHandler(self):
        try:
            date = parse_date(self.date_line_edit.text())
        except:
            QMessageBox.critical(self, 'Erro - Update', 'Date must be: ddmmyyyy')
            return 
        
        try:
            amount = self.amount.text().replace(',', '.') 

            float(amount)
        
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', \
                'Error amount format. Enter a valid decimal number')
            return 

        try:
            rate = self.rate.text().replace(',', '.') 

            float(rate)
        
        except ValueError:
            QMessageBox.critical(self, 'Error - Update', \
                'Error rate format. Enter a valid decimal number')
            return 


        info = self.info_lineedit.text() 

        try:
            self.model.add(date, amount, rate, info)
            self.view.resizeColumnToContents(2) 
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
            self.view.resizeColumnToContents(2) 
            self.view.clearSelection() 
            self.updateOwing()
        except:
            raise 
            QMessageBox.critical(self, 'Error - Update', 'Could not delete payments')


    def updateOwing(self):
        self.owing = round(self.total - self.paid, 2) 
        self.owing_lineedit.setText(str(round(self.owing, 2)))

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
        try:
            type = str(self.proforma.invoice.type) 
            number = str(self.proforma.invoice.number).zfill(6)
        except AttributeError:
            type = str(self.proforma.type)
            number = str(self.proforma.number).zfill(6)

        document_number = type + '-' + number
        self.document_line_edit.setText(document_number)
        
        self.partner_line_edit.setText(self.proforma.partner.fiscal_name)
        self.document_date_line_edit.setText(self.proforma.date.strftime('%d/%m/%Y'))

        self.total_linedit.setText(str(round(float(self.total), 2)))
        self.owing_lineedit.setText(str(round(float(self.total) - float(self.paid), 2)))



    def closeEvent(self, event):
        # Es importante hacer esto porque si  no
        # los cambios solo seran guardados en la base 
        # cuando se ejecute un proximo commit 
        # Queremos que esten alli lo antes posible
        # Por si otra persona quiere consultar pagos.
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