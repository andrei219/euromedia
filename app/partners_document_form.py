

from ui_partners_document_form import Ui_DocumentsForm

from PyQt5.QtWidgets import QDialog

class Form(Ui_DocumentsForm, QDialog):

    def __init__(self, partner):
        super(Form, self).__init__()
        self.setupUi(self)
