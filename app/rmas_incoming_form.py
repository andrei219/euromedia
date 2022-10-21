from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableView
from ui_rmas_incoming_form import Ui_Form


from utils import setCompleter
from utils import partner_id_map
from utils import today_date

from utils import parse_date
from db import IncomingRma, IncomingRmaLine
from db import session

from models import RmaIncomingLineModel


import utils

class Form(Ui_Form, QWidget):


    def __init__(self, parent, order=None):
        order: IncomingRma
        from importlib import reload
        global utils
        utils = reload(utils)
        super().__init__()
        self.parent = parent
        self.order = None
        self.lines_model = None
        self.setupUi(self)
        self.set_handlers()

        if order is not None:
            self.order = order
            self.date.setText(order.date.strftime('%d%m%Y'))
        else:
            self.date.setText(today_date())
            self.order = IncomingRma()
            session.add(self.order)
            session.flush()

        # try:
        #     if order.wh_incoming_rma.invoices:
        #         self.check.setEnabled(False)
        #         self.sn.setEnabled(False)
        # except AttributeError:
        #     pass


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

    def set_handlers(self):
        self.check.clicked.connect(self.search_sn)
        self.save.clicked.connect(self.save_handler)
        self.delete_.clicked.connect(self.delete_handler)

    def search_sn(self):
        sn = self.sn.text().strip()

        try:
            line = session.query(IncomingRmaLine).where(IncomingRmaLine.sn == sn).all()[-1]
        except IndexError:
            pass
        else:
            message = f'This sn is already processed in order {line.incoming_rma.id} for {line.cust}. Continue?'
            if QMessageBox.question(self, 'Question', message, QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return

        if not sn:
            return
        try:
            self.lines_model.add(sn)
            self.view.resizeColumnsToContents()
            self.sn.clear()
            self.sn.setFocus()
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

        if not self.lines_model:
            QMessageBox.critical(self, 'Error', 'I will not save and empty proforma')
            return

        if len({line.cust for line in self.lines_model}) != 1:
            QMessageBox.critical(self, 'Error', 'Imeis from different customers')
            return

        session.commit()

        try:
            self.lines_model.update_warehouse()
        except Exception:
            raise

        QMessageBox.information(self, 'Success', 'Rma order saved successfully')
        self.close()


    def closeEvent(self, event) -> None:
        session.rollback()

    def exit_handler(self):
        session.rollback()
        self.close()


















