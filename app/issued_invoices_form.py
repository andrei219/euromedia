
from ui_issued_invoices_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog


class Filters:

    pass

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.view.clicked.connect(self.view_handler)
        self._export.clicked.connect(self.export_handler)

    def view_handler(self):
        pass


    def export_handler(self):
        pass