

from PyQt5.QtWidgets import QWidget, QMessageBox, QTableView
from ui_rmas_incoming_form import Ui_Form


from utils import setCompleter
from utils import partner_id_map
from models import get_partner_warranty
from utils import today_date

from utils import parse_date
from db import IncomingRma
from db import session

from models import RmaIncomingLineModel


import utils

class Form(Ui_Form, QWidget):

    def __init__(self, parent, order=None):

        from importlib import  reload
        global utils
        utils = reload(utils)
        super().__init__()
        self.parent = parent
        self.order = None
        self.lines_model = None
        self.setupUi(self)
        self.set_completer()
        self.set_handlers()

        if order is not None:
            self.order = order
            self.partner.setText(order.partner.fiscal_name)
            self.date.setText(order.date.strftime('%d%m%Y'))
        else:
            self.order = IncomingRma()
            session.add(self.order)
            session.flush()

        self.set_model()
        self.set_view_config()

    def set_view_config(self):
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)


    def set_model(self):
        self.lines_model = RmaIncomingLineModel(self.order.lines)
        self.view.setModel(self.lines_model)
        self.view.resizeColumnsToContents()

    def set_completer(self):
        setCompleter(self.partner, partner_id_map.keys())
        self.date.setText(today_date())

    def set_handlers(self):
        self.partner.editingFinished.connect(self.search_partner_warranty)
        self.check.clicked.connect(self.search_sn)
        self.exit.clicked.connect(self.exit_handler)
        self.save.clicked.connect(self.save_handler)
        self.delete_.clicked.connect(self.delete_handler)

    def search_partner_warranty(self):
        try:
            warranty = get_partner_warranty(partner_id_map[self.partner.text()])
        except KeyError:
            self.warranty.setText('Invalid Partner')
            return
        else:
            self.warranty.setText(str(warranty))


    def search_sn(self):
        sn = self.sn.text().strip()
        try:
            partner_id = partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Set partner correctly')
            return

        if not sn:
            return

        try:
            self.lines_model.add(sn, partner_id)
            self.view.resizeColumnsToContents()
            self.sn.clear()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))


    def delete_handler(self):
        try:
            row = {i.row() for i in self.view.selectedIndexes()}.pop()
        except KeyError:
            return
        else:
            try:
                self.lines_model.delete(row)
            except AttributeError:
                return

    def save_handler(self):
        try:
            self.order.date = utils.parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Invalid date format. It is ddmmyyyy')
            return
        try:
            self.order.partner_id = utils.partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Invalid Partner')
            return
        else:

            session.commit()
            QMessageBox.information(self, 'Success', 'Rma order saved successfully')


    def exit_handler(self):
        session.rollback()
        self.close()


    def closeEvent(self, event) -> None:
        session.rollback()
        self.parent.set_mv('rmas_incoming_')




















