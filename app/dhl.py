

from ui_dhl import Ui_Form

from PyQt5.QtWidgets import QDialog


class Form(Ui_Form, QDialog):
    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
