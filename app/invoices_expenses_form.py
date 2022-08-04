

from ui_invoice_expenses_form import Ui_Form

from PyQt5.QtWidgets import QDialog

from models import InvoiceExpensesModel

class Form(Ui_Form ,QDialog):

    def __init__(self, parent, invoice):
        super().__init__(parent=parent)
        self.setupUi(self)

    def add_handler(self):
        pass

