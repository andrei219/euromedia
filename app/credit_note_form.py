
from ui_credit_note_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QTableView

from models import CreditNoteLineModel

class Form(Ui_Form, QWidget):

    def __init__(self, parent, proforma):
        super(Form, self).__init__()
        self.setupUi(self)
        self.proforma = proforma
        self.view.setModel(CreditNoteLineModel(proforma.credit_note_lines))


        self.set_view_config()

    def set_view_config(self):
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.resizeColumnToContents(0)

    def set_form(self):
        pass

    def set_proforma(self):
        pass



