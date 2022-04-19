from ui_advanced_definition_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QMessageBox, QTableView

import lxml

import utils
import db

from models import AdvancedStockModel
from models import DefinedStockModel
from models import AdvancedLinesModel


def reload_utils():
    from importlib import reload
    global utils
    utils = reload(utils)


class Form(Ui_Form, QWidget):

    def __init__(self, parent, view, proforma):
        self.stock_model = None
        self.defined_model = None
        reload_utils()
        super().__init__()
        self.setupUi(self)
        self.proforma = proforma
        utils.setCommonViewConfig(self.lines_view)
        utils.setCommonViewConfig(self.defined_view)

        self.lines_model = AdvancedLinesModel(proforma, show_free=False)
        self.lines_view.setModel(self.lines_model)

        self.set_header()
        self.set_handlers()

        self.init_template()

        self.warehouse_id = utils.warehouse_id_map.get(
            self.warehouse.text()
        )

        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        self.stock_view.setSelectionMode(QTableView.MultiSelection)
        self.stock_view.setAlternatingRowColors(True)

        self.saved = False


    def init_template(self):
        self.init_lines_stock_defined()

    def init_lines_stock_defined(self):
        index = self.lines_model.index(0, 0)
        self.lines_view.setCurrentIndex(index)
        line = self.lines_model[0]
        self.set_stock_mv(line)
        self.set_defined_mv(line)

    def set_handlers(self):
        self.lines_view.clicked.connect(self.lines_view_clicked_handler)
        self.delete_.clicked.connect(self.delete_handler)
        self.update.clicked.connect(self.update_handler)
        self.save.clicked.connect(self.save_handler)

    def set_header(self):
        self.partner.setText(self.proforma.partner.fiscal_name)
        doc = str(self.proforma.type) + '-' + str(self.proforma.number).zfill(6)
        self.document.setText(doc)
        self.date.setText(self.proforma.date.strftime('%d/%m/%Y'))
        self.warehouse.setText(self.proforma.warehouse.description)

    def lines_view_clicked_handler(self, index):
        row = index.row()
        line = self.lines_model.lines[row]
        self.set_stock_mv(line)
        self.set_defined_mv(line)

    def update_handler(self):
        line = self.get_selected_line()

        if sum(stock.request for stock in self.stock_model.requested_stocks) > line.quantity:
            QMessageBox.critical(self, 'Error', 'sum(requested) must be equal to line quantity')
        else:
            self.defined_model.add(*self.stock_model.requested_stocks, showing_condition=line.showing_condition)
            self.set_stock_mv(line)

    def set_defined_mv(self, line):
        self.defined_model = DefinedStockModel(line)
        self.defined_view.setModel(self.defined_model)

    def save_handler(self):

        if all((
                line.definitions
                for line in self.proforma.advanced_lines
                if not line.free_description
        )):
            self.lines_model.update_count_relevant()

            try:
                db.session.commit()
                self.saved = True
            except:
                raise
                db.session.rollback()
            else:
                QMessageBox.information(
                    self,
                    'Success',
                    'Advanced sale definition made successfully'
                )
                self.close()

    def delete_handler(self):
        if hasattr(self, 'defined_model'):
            self.defined_model.reset()
            line = self.get_selected_line()
            self.set_stock_mv(line)

    def get_selected_line(self):
        indexes = self.lines_view.selectedIndexes()
        if not indexes:
            return
        row = {i.row() for i in indexes}.pop()
        return self.lines_model[row]

    def set_stock_mv(self, line):
        self.stock_model = AdvancedStockModel(
            self.proforma.warehouse_id,
            line
        )
        self.stock_view.setModel(self.stock_model)

    def closeEvent(self, event):
        if not self.saved:
            QMessageBox.information(
                self,
                'Information',
                'This is an all or None operation, changes will not be saved'
            )

            db.session.rollback()
        else:
            db.session.commit()


class EditableForm(Form):

    def __init__(self, parent, view, proforma):
        super().__init__(parent, view, proforma)

        self.lines_view.clicked.connect(self.lines_view_clicked_handler)

        self.disable_things()

    def disable_things(self):
        self.stock_view.setDisabled(True)
        self.save.setDisabled(True)
        self.stock_view.setDisabled(True)
        self.update.setDisabled(True)
        self.delete_.setDisabled(True)

    def init_template(self):
        pass

    def lines_view_clicked_handler(self, index):
        row = index.row()
        line = self.lines_model.lines[row]
        self.set_defined_mv(line)


def get_form(parent, view, proforma):
    if any((
            definition
            for line in proforma.advanced_lines
            for definition in line.definitions
    )):
        return EditableForm(parent, view, proforma)
    else:
        return Form(parent, view, proforma)
