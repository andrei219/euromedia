

from ui_change_description_form import Ui_Dialog


from PyQt5.QtWidgets import QDialog, QMessageBox

from utils import setCompleter
from utils import description_id_map

from models import update_description
from models import find_item_id_from_serie

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
        descriptions = description_id_map.keys()
        setCompleter(self.to, description_id_map.keys())

        self.serie.returnPressed.connect(self.serie_return_pressed)
        self.apply.clicked.connect(self.apply_handler)

    def serie_return_pressed(self):
        serie = self.serie.text().strip()
        try:
            self._from.setText(description_id_map.inverse[find_item_id_from_serie(serie)])
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Device not found')

    def apply_handler(self):
        description = self.to.text()
        imei = self.serie.text()
        try:
            to_item_id = description_id_map[description]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Cant find description')
        else:
            try:
                update_description(imei, to_item_id)
            except ValueError as ex:
                QMessageBox.critical(self, 'Error', str(ex))

            else:
                self.serie_return_pressed()
