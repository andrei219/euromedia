


from PyQt5.QtWidgets import QDialog

from ui_inventory_form import Ui_InventoryForm

from models import InventoryModel

from utils import setCommonViewConfig

class InventoryForm(Ui_InventoryForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent) 
        self.setupUi(self)
        self.view.setModel(InventoryModel())
        setCommonViewConfig(self.view)