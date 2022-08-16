import db
from ui_invoice_expenses_form import Ui_Form

from PyQt5.QtWidgets import QDialog, QMessageBox

from models import InvoiceExpensesModel

import utils


class Form(Ui_Form, QDialog):

    def __init__(self, parent, invoice):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.invoice = invoice
        self.set_header()

        self.doc_map = {p.doc_repr: p for p in self.invoice.proformas}

        utils.setCompleter(self.proforma, self.doc_map.keys())

        self.model = InvoiceExpensesModel(invoice)
        self.view.setModel(self.model)

        self.add.clicked.connect(self.add_handler)
        self.view.doubleClicked.connect(self.view_double_clicked)

        self.date.setText(utils.today_date())

    def set_header(self):
        self.partner.setText(self.invoice.partner_name)
        self.invoice_repr.setText(self.invoice.doc_repr)
        self.proformas.setText(', '.join(p.doc_repr for p in self.invoice.proformas))

    def view_double_clicked(self, index):
        expense = self.model[index.row()]
        from expenses_form import ExpenseForm
        ExpenseForm(
            self,
            expense.proforma,
            sale=isinstance(self.invoice, db.SaleInvoice)
        ).exec_()

    def clear_fields(self):
        self.amount.clear()
        self.info.clear()

    def add_handler(self):

        try:
            date = utils.parse_date(self.date.text())
        except ValueError:
            QMessageBox.information(self, 'Error', 'Invalid date format')
            return

        try:
            amount = float(self.amount.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Invalid number')
            return

        try:
            proforma = self.doc_map[self.proforma.text()]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Invalid Proforma number')
            return

        self.model.add(date, amount, self.info.text(), proforma)
        self.clear_fields()
