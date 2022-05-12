

from PyQt5.QtWidgets import QDialog

from ui_apply_credit_note_form import Ui_Dialog


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent, proforma):
        super(Form, self).__init__(parent)
        self.setupUi(self)

        self.proforma = proforma