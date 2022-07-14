from PyQt5 import QtGui

from ui_credit_note_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QTableView
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from models import CreditNoteLineModel

import utils
from db import session


def mouse_press_event(self, event):
    if event.button() == Qt.LeftButton:
        print('eee')


class Form(Ui_Form, QWidget):

    def __init__(self, parent, proforma, is_invoice=False):
        super(Form, self).__init__()
        self.setupUi(self)
        self.is_invoice = is_invoice
        self.proforma = proforma
        self.model = CreditNoteLineModel(proforma.credit_note_lines)
        self.view.setModel(self.model)
        self.set_view_config()
        self.setCombos()
        self.save.clicked.connect(self.save_handler)
        self.set_form()


    def set_handlers(self):

        self.save.clicked.connect(self.save_handler)



    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        session.rollback()

    def setCombos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()),
            (self.courier, utils.courier_id_map.keys())
        ]:
            combo.addItems(data)

    def save_handler(self):
        self.set_proforma()
        try:
            session.commit()
        except Exception:
            raise
        else:
            QMessageBox.information(self, 'Success', 'Credit note updated successfully')


    def set_view_config(self):
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.setAlternatingRowColors(True)
        self.view.resizeColumnToContents(0)

    def set_form(self):
        p = self.proforma

        if self.is_invoice:
            self.type.setCurrentText(str(self.proforma.invoice.type))
            self.number.setText(str(self.proforma.invoice.number))
            self.date.setText(self.proforma.invoice.date.strftime('%d%m%Y'))
        else:
            self.type.setCurrentText(str(self.proforma.type))
            self.number.setText(str(self.proforma.number))
            self.date.setText(self.proforma.date.strftime('%d%m%Y'))

        self.partner.setText(p.partner.fiscal_name)
        self.agent.setCurrentText(p.agent.fiscal_name)
        self.courier.setCurrentText(p.courier.description)
        self.incoterms.setCurrentText(p.incoterm)
        self.eur.setChecked(p.eur_currency)
        self.external.setText(p.external)
        self.tracking.setText(p.tracking)
        self.they_pay_we_ship.setChecked(p.they_pay_we_ship)
        self.they_pay_they_ship.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship.setChecked(p.we_pay_we_ship)
        self.note.setText(p.note)

        self.quantity.setText(f'Quantity: {self.model.quantity}')
        self.proforma_total.setText(str(self.model.total))
        self.proforma_tax.setText(str(self.model.tax))
        self.subtotal_proforma.setText(str(self.model.subtotal))

    def set_proforma(self):
        if self.is_invoice:
            self.proforma.invoice.type = int(self.type.currentText())
            self.proforma.invoice.number = int(self.number.text())
            self.proforma.invoice.date = utils.parse_date(self.date.text())
        else:
            self.proforma.type = int(self.type.currentText())
            self.proforma.number = int(self.number.text())
            self.proforma.date = utils.parse_date(self.date.text())

        self.proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        self.proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked()
        self.proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked()
        self.proforma.agent_id = utils.agent_id_map[self.agent.currentText()]
        self.proforma.partner_id = utils.partner_id_map[self.partner.text()]
        self.proforma.courier_id = utils.courier_id_map[self.courier.currentText()]
        self.proforma.eur_currency = self.eur.isChecked()
        self.proforma.incoterm = self.incoterms.currentText()
        self.proforma.external = self.external.text()
        self.proforma.tracking = self.tracking.text()
        self.proforma.note = self.note.toPlainText()[0:255]



