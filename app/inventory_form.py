


from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_inventory_form import Ui_InventoryForm

from models import FutureInventoryModel

import utils 

class InventoryForm(Ui_InventoryForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent) 
        self.setupUi(self)
        self.model = None

        utils.setCommonViewConfig(self.view)

        self.apply.clicked.connect(self.apply_handler)
        self.excel.clicked.connect(self.excel_handler) 

        self.set_completers()

        self.date.setText(utils.today_date())
        self.description.setFocus()

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

        if self.model is None:
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
        date = self.date.text()
        if date:
            try:
                date = utils.parse_date(date)
            except ValueError:
                QMessageBox.critical(self, 'Error', 'Incorrect value for date field.')
                return
        else:
            date = None

        self.model = FutureInventoryModel(**filters, date=date)
        self.view.setModel(self.model) 
        self.view.resizeColumnToContents(1)
    
    def build_filters(self):
        return {
            'description': self.description.text().strip(),
            'spec': self.spec.text().strip(),
            'condition': self.condition.text().strip(),
            'warehouse': self.warehouse.text().strip(),
        }
