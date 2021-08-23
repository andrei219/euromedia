
from PyQt5.QtWidgets import QDialog

from ui_quantity_price_form import Ui_QuantityPriceForm


class QuantityPriceForm(Ui_QuantityPriceForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        