


from ui_free_line_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog

class Dialog(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent) 
        self.setupUi(self)
        self.description.setFocus(True)