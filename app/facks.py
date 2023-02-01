


from ui_facks import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from models import FucksModel

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)

        self.model = FucksModel()
        self.view.setModel(self.model)

        self.dojob.clicked.connect(self.dojob_handler)

    def dojob_handler(self):
        try:
            self.model.export()
        except:
            raise
        else:
            QMessageBox.information(self, 'Success', 'Data exported successfully')


