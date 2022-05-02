

from ui_warehouse_rma_incoming_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QTableView

from models import WhRmaIncomingLineModel

from db import session

from utils import warehouse_id_map

class Form(Ui_Form, QWidget):

    def __init__(self, parent, order):
        super().__init__()
        self.setupUi(self)
        self.order = order
        self.parent = parent

        self.view.setModel(WhRmaIncomingLineModel(order.lines))

        self.populate_form()
        self.set_view_config()

    def set_view_config(self):
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)

    def populate_form(self):
        self.partner.setText(self.order.incoming_rma.partner.fiscal_name)
        self.date.setText(self.order.incoming_rma.date.strftime('%d%m%y'))
        self.warehouse.addItems(warehouse_id_map.keys())
        try:
            self.warehouse.setCurrentText(self.order.warehouse.description)
        except AttributeError:
            pass


    def save_handler(self):
        try:
            self.order.warehouse_id = warehouse_id_map[self.warehouse.currentText()]
            session.commit()
        except Exception as ex:
            session.rollback()
            raise


