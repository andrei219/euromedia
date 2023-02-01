

from ui_facks import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from models import FucksModel

def validate_year(year: str):
    try:
        year = int(year)
    except ValueError:
        return False
    else:
        return year >= 2022


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)

        self.model = FucksModel()
        self.view.setModel(self.model)

        self.dojob.clicked.connect(self.do_job)

    def do_job(self):

        year = self.year.text()
        if not validate_year(year):
            QMessageBox.critical(self, 'Error', 'Invalid year')
            self.year.setFocus()
            return

        try:
            self.model.export(year)
        except:
            raise
        else:
            QMessageBox.information(self, 'Success', 'Data exported successfully')