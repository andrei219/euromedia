from datetime import datetime

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_SII import Ui_Dialog

from models import do_sii
from utils import parse_date


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.send.clicked.connect(self.send_handler)
        self.all.clicked.connect(self.all_handler)

    def all_handler(self):
        for serie in ['1', '2', '3', '4', '5']:
            checkbox = getattr(self, 'serie_' + serie)
            checkbox.setChecked(True)

    def send_handler(self):
        try:
            _from, to = self.get_dates()
            do_sii(_from, to, list(
                filter(lambda s: s is not None,
                       [
                           1 if self.serie_1.isChecked() else None,
                           2 if self.serie_2.isChecked() else None,
                           3 if self.serie_3.isChecked() else None,
                           4 if self.serie_4.isChecked() else None,
                           5 if self.serie_5.isChecked() else None,
                           6 if self.serie_6.isChecked() else None
                        ]
                    )
                )
            )

        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
        else:
            self.populate_last_sent()
            QMessageBox.information(self, 'Sucess', 'Invoices sent')

    def populate_last_sent(self):
        pass

    def get_dates(self):
        try:
            _from = self.date_from.text()
            to = self.date_to.text()
            _from, to = parse_date(_from), parse_date(to)
            return _from, to
        except ValueError:
            raise
