from PyQt5 import QtGui

from ui_warehouse_rma_incoming_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QTableView, QMessageBox, QAbstractItemView

from models import WhRmaIncomingLineModel

from db import session

from delegates import WhDelegate

class Form(Ui_Form, QWidget):

    def __init__(self, parent, order):
        super().__init__()
        self.setupUi(self)
        self.order = order
        self.parent = parent

        self.view.setModel(WhRmaIncomingLineModel(order.lines))
        self.view.setItemDelegate(WhDelegate(self))

        self.populate_form()
        self.set_view_config()
        self.save.clicked.connect(self.save_handler)

        # if self.order.invoices:
        #     self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def set_view_config(self):
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.resizeColumnsToContents()

    def populate_form(self):
        self.partner.setText(self.order.incoming_rma.lines[0].supp)
        self.date.setText(self.order.incoming_rma.date.strftime('%d%m%y'))
        try:
            self.warehouse.setCurrentText(self.order.warehouse.description)
        except AttributeError:
            pass

    def save_handler(self):
        try:
            session.commit()
        except Exception as ex:
            session.rollback()
            raise
        else:
            QMessageBox.information(self, 'Success', 'Rma warehouse check made successfully')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        session.rollback()

