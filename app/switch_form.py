
from ui_switch_form import Ui_Dialog
from PyQt5.QtWidgets import QDialog


from models import SwitchModel

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)

