

from PyQt5.QtWidgets import QDialog


from ui_line_complete_form import Ui_LineCompleteForm

class Form(Ui_LineCompleteForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self) 
