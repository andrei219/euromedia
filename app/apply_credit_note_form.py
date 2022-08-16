

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_apply_credit_note_form import Ui_Dialog

from models import AppliedNoteModel
from models import AvailableNoteModel

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent, invoice):
        super(Form, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        # This form only available in invoices, then,
        # it sure proforma.invoice != None
        self.applied_model = None
        self.available_model = None
        self.invoice = invoice

        self.set_models()

        self.add.clicked.connect(self.add_handler)
        self.delete_.clicked.connect(self.delete_handler)

    def set_applied_model(self):
        self.applied_model = AppliedNoteModel(self.invoice)
        self.applied.setModel(self.applied_model)

    def set_available_model(self):
        self.available_model = AvailableNoteModel(self.invoice)
        self.available.setModel(self.available_model)

    def set_models(self):
        self.set_applied_model()
        self.set_available_model()
        self.parent.update_totals()
        self.parent.update_totals()

    def delete_handler(self):
        rows = {i.row() for i in self.applied.selectedIndexes()}
        try:
            self.applied_model.delete(rows)
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
        else:
            self.set_models()
            self.parent.update_totals()

    def add_handler(self):
        rows = {i.row() for i in self.available.selectedIndexes()}
        try:
            self.available_model.add(rows)
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
        else:
            self.set_models()
            self.parent.update_totals()


