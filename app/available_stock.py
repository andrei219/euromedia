
from ui_available_stock import Ui_Form
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtWidgets import QTableView

from models import IncomingStockModel
from models import StockModel

from utils import setCompleter
from utils import warehouse_id_map
from utils import description_id_map
from utils import conditions
from utils import specs

class Form(Ui_Form, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.set_view_config()
        self.set_completers()
        self.set_handlers()

    def set_model(self):
        warehouse = self.warehouse.text()
        try:
            warehouse_id = warehouse_id_map[warehouse]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Specify warehouse')
            return

        spec = self.spec.text()
        description = self.description.text()
        condition = self.condition.text()
        Model = StockModel if self.physical.isChecked() else IncomingStockModel
        self.model = Model(
            warehouse_id=warehouse_id,
            description=description,
            condition=condition,
            spec=spec,
            check=True
        )

        self.view.setModel(self.model)
        self.view.resizeColumnToContents(0)

    def apply_handler(self):
        self.set_model()

    def whatsapp_handler(self):
        if hasattr(self, 'model'):
            self.model.whatsapp_export()



    def excel_handler(self):
        if hasattr(self, 'model'):
            from utils import get_file_path
            file_path = get_file_path(self)
            try:
                self.model.excel_export(file_path)
            except:
                QMessageBox.critical(self, 'Error', 'Error exporting data')
                raise
            else:
                QMessageBox.information(self, 'Success', 'Data exported successfully')


    def set_view_config(self):
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)

    def set_handlers(self):
        self.whatsapp.clicked.connect(self.whatsapp_handler)
        self.excel.clicked.connect(self.excel_handler)
        self.apply.clicked.connect(self.apply_handler)

    def set_completers(self):
        for field, data in [
            (self.warehouse, warehouse_id_map.keys()),
            (self.description, description_id_map.keys()),
            (self.condition, conditions),
            (self.spec, specs)
        ]:
            setCompleter(field, data)




















