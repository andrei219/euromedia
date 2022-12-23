
from PyQt5.QtWidgets import QDialog, QMessageBox
from ui_stock_valuation import Ui_Dialog

from models import StockValuationModelDocument
from models import StockValuationModelImei
from models import StockValuationModelWarehouse
from models import WarehouseSimpleValueModel


import utils

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
        self.model = None
        self.calculate.clicked.connect(self.calculate_handler)
        self.by_document.toggled.connect(self.by_doc_toggled)
        self.by_serial.toggled.connect(self.by_serial_toggled)
        self.by_warehouse.toggled.connect(self.by_warehouse_toggled)
        self.export_.clicked.connect(self.export_handler)

        utils.setCompleter(self.warehouse, utils.warehouse_id_map.keys())

    def by_doc_toggled(self, check):
        self.by_serial.setChecked(False)
        self.by_warehouse.setChecked(False)

    def by_serial_toggled(self, check):
        self.by_document.setChecked(False)
        self.by_warehouse.setChecked(False)

    def by_warehouse_toggled(self, check):
        self.by_serial.setChecked(False)
        self.by_document.setChecked(False)

    def export_handler(self):
        if self.model is None:
            return
        filepath = utils.get_file_path(self)

        try:
            self.model.export(filepath)
        except AttributeError:
            raise
        else:
            QMessageBox.information(self, 'Info', 'Data exported')

    def calculate_handler(self, check):
        if self.by_document.isChecked():
            doc_repr = self.document.text()
            if utils.match_doc_repr(doc_repr):
                try:
                    self.model = StockValuationModelDocument(
                        doc_repr=doc_repr,
                        proforma=self.proforma.isChecked()
                    )
                    self.view.setModel(self.model)
                except ValueError as ex:
                    QMessageBox.critical(self, 'Error', str(ex))

        elif self.by_serial.isChecked():
            self.model = StockValuationModelImei(self.serial.text())
            self.view.setModel(self.model)

        elif self.by_warehouse.isChecked():
            try:
                warehouse_id = utils.warehouse_id_map[self.warehouse.text()]

            except KeyError:
                return
            else:

                if self.just_line_price.isChecked():
                    self.model = WarehouseSimpleValueModel(warehouse_id)
                else:
                    self.model = StockValuationModelWarehouse(warehouse_id)


                self.view.setModel(self.model)


