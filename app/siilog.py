
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_siilog import Ui_Dialog

from utils import parse_date

from models import SIILogModel


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent, registers):
        super(Form, self).__init__(parent)
        self.setupUi(self)

        self.model = SIILogModel(registers)
        self.view.setModel(self.model)

        self.view.resizeColumnsToContents()
