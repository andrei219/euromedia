
from ui_switch_form import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QMessageBox

from models import SwitchModel


import db

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.model = SwitchModel()
        self.view.setModel(self.model)

        self.switch_.clicked.connect(self.switch_handler)

    def switch_handler(self):
        ixs = self.view.selectionModel().selectedRows()
        if ixs:
            ix = ixs[0]
            new_context = self.model.switch(ix.row())
            self.parent.setWindowTitle('Context:' + new_context)
            QMessageBox.information(self, 'Switch', 'Switched Successfully')

