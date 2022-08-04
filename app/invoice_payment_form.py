

from PyQt5.QtWidgets import QDialog, QMessageBox

import db
from ui_invoice_payment_form import Ui_Form

from models import InvoicePaymentModel

from utils import today_date



class Form(Ui_Form, QDialog):

    def __init__(self, parent, invoice):
        super().__init__()
        self.invoice = invoice
        self.setupUi(self)
        self.model = InvoicePaymentModel(invoice)
        self.view.setModel(self.model)

        self.add.clicked.connect(self.add_handler)
        self.view.doubleClicked.connect(self.view_double_clicked)

        if not sum(pay.amount for pro in invoice.proformas for pay in pro.payments):
            self.full.setChecked(True)
            self.partial.setChecked(False)
            self.date.setText(today_date())
            self.rate.setReadOnly(all(p.eur_currency for p in invoice.proformas))
            self.amount.setText(str(sum(p.total_debt for p in invoice.proformas)))

            self.info.setFocus()



    def view_double_clicked(self, index):
        proforma = self.model[index.row()]

        print(proforma.doc_repr)

        from payments_form import PaymentForm
        PaymentForm(self, proforma, sale=isinstance(self.invoice, db.SaleInvoice)).exec_()


    def reset_model(self):
        pass

    def add_handler(self):
        try:
            rate = float(self.rate.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Rate must be a number')
        else:
            self.model.complete_payments(
                rate, self.info.text()
            )
            self.model.layoutChanged.emit()