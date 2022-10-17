


from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_inventory_form import Ui_InventoryForm

from models import InventoryModel

import utils 

class InventoryForm(Ui_InventoryForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent) 
        self.setupUi(self)
        
        utils.setCommonViewConfig(self.view)

        self.apply.clicked.connect(self.apply_handler)
        self.excel.clicked.connect(self.excel_handler) 

        self.set_completers()

    def set_completers(self):
        for field, data in [
            (self.description, utils.descriptions),
            (self.condition, utils.conditions), 
            (self.spec, utils.specs), 
            (self.warehouse, utils.warehouse_id_map.keys())
        ]:
            utils.setCompleter(field, data) 
   

    def excel_handler(self):
        from utils import get_file_path
        from openpyxl import Workbook

        if not hasattr(self, 'model'): 
            return 
        
        file_path = get_file_path(self)
        
        if not file_path:
            return

        try:
            self.model.excel_export(file_path)
        except:
            QMessageBox.information(self, 'Error', 'An error ocurred while exporting data')
        else:
            QMessageBox.information(self, 'Information', 'Data exported successfully')

    def apply_handler(self):
        filters = self.build_filters()
        self.model = InventoryModel(**filters)
        self.view.setModel(self.model) 
        self.view.resizeColumnToContents(1)
    
    def build_filters(self):
        return {
            'description': self.description.text().strip(),
            'spec': self.spec.text().strip(),
            'condition': self.condition.text().strip(),
            'warehouse': self.warehouse.text().strip()
        }
        return filters
