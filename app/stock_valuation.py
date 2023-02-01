
from PyQt5.QtWidgets import QDialog, QMessageBox

import db
from ui_stock_valuation import Ui_Dialog

from models import StockValuationModelDocument, WarehouseValueModel
from models import StockValuationModelImei

import utils


''' Write a function that validates text described as follows:
    
    an integer between 1 and 6 inclusive followed by a hyphen,
    followed by optionally some zeroes and a number. The total length 
    of the part after the hyphen must be 6. Then, a colon, then a year that must be >= 2022.
    The following samples must match: 1-0123:2022, 1-123:2022, 4-000022:2023.
    The following must not match: 7-123:2022, 1-123:2021, 1-123:2022a, 1-123:2022:2023, 
    2-0000001. Return True if the text matches, False otherwise.
'''
def match_doc_repr_and_year(doc_repr):
    import re
    pattern = r'^[1-6]-[0-9]{1,5}:202[2-9]$'
    return bool(re.match(pattern, doc_repr))


''' Write a function that parses a string that matches the pattern described in the previous function.'''
''' Return a tuple of three elements: the type of the document, the number of the document, and the year.'''
''' The following 1-123:2022 must return (1, 123, 2022), 2-000001:2023 must return (2, 1, 2023), 
    6-000001:2029 must return (6, 1, 2029).'''
def parse_doc_repr_and_year(doc_repr):
    type_, number = doc_repr.split('-')
    number, year = number.split(':')
    return int(type_), int(number), int(year)


def prepare_filters(filters):

    if not filters['date']:
        raise ValueError('Date must be provided')
    else:
        try:
            filters['date'] = utils.parse_date(filters['date']).date()
        except ValueError:
            raise ValueError('Incorrect date format: ddmmyyyy')

    try:
        filters['warehouse_id'] = utils.warehouse_id_map[filters['warehouse']]
    except KeyError:
        filters['warehouse_id'] = None

    if not filters['all'] and not filters['warehouse_id']:
        raise ValueError('Warehouse must be entered or all wh. checked.')

    return filters

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
        self.all.toggled.connect(self.all_toggled)

        utils.setCompleter(self.warehouse, utils.warehouse_id_map.keys())
        self.all_path = None

        self.date.setText(utils.today_date())
        self.warehouse.setText(db.session.query(db.Warehouse.description).where(
            db.Warehouse.id == 1
        ).scalar())


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

            if match_doc_repr_and_year(doc_repr):
                type_, number, year = parse_doc_repr_and_year(doc_repr)

                try:
                    self.model = StockValuationModelDocument(type_, number, year, self.proforma.isChecked())
                    self.view.setModel(self.model)

                except ValueError as ex:
                    QMessageBox.critical(self, 'Error', str(ex))
                    return

            else:
                QMessageBox.critical(self, 'Error', 'Incorrect document representation. Correct format: d-nnnnnn:yyyy')
                return


        elif self.by_serial.isChecked():
            self.model = StockValuationModelImei(self.serial.text())
            self.view.setModel(self.model)

        elif self.by_warehouse.isChecked():
            try:
                filters = self.build_filters()
            except ValueError as ex:
                QMessageBox.critical(self, 'Error', str(ex))
                return
            else:
                self.model = WarehouseValueModel(filters)
                self.view.setModel(self.model)

    def all_toggled(self, checked):
        if checked:
            directory = utils.get_directory(self)
            if not directory:
                self.all.setChecked(False)
            else:
                self.all_path = directory
                self.warehouse.setText('')
        else:
            self.all_path = None

    def build_filters(self):
        return prepare_filters(
            {
                'date': self.date.text(),
                'all': self.all_path,
                'book_value': self.book_value.isChecked(),
                'warehouse': self.warehouse.text()
            }
        )


if __name__ == '__main__':

    pass


