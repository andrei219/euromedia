from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QMessageBox

from ui_invoice_form import Ui_InvoiceForm

from db import session, SaleInvoice, PurchaseInvoice

from models import (
    update_sale_warehouse,
    update_purchase_warehouse,
    SaleInvoiceLineModel,
    PurchaseInvoiceLineModel
)

import utils

from utils import parse_date, get_next_num

class Form(Ui_InvoiceForm, QWidget):

    def __init__(self, invoice):
        super().__init__()
        self.setupUi(self)
        self.invoice = invoice
        self.warehouse.setDisabled(True)

        if isinstance(invoice, SaleInvoice):
            self.cls = SaleInvoice
            self.model = SaleInvoiceLineModel(invoice)
            self.update_warehouse_callback = update_sale_warehouse

        elif isinstance(invoice, PurchaseInvoice):
            self.model = PurchaseInvoiceLineModel(invoice)
            self.update_warehouse_callback = update_purchase_warehouse
            self.cls = PurchaseInvoice

        self.view.setModel(self.model)

        self.setCombos()
        utils.setCompleter(self.partner, utils.partner_id_map.keys())

        self.populate_form()

        self.update_totals()

        self.save.clicked.connect(self.save_handler)
        self.delete_.clicked.connect(self.delete_handler)
        self.apply_cn.clicked.connect(self.apply_cn_handler)
        self.view.selectionModel().selectionChanged.connect(self.selection_changed)
        self.set_wildcard()

    def selection_changed(self):
        self.selected.setText(
            'Selected:' + str(
                sum(
                    self.model[row].quantity for row in {
                        i.row() for i in self.view.selectedIndexes()
                    }
                )
            )
        )

    def type_changed(self):
        try:
            d = parse_date(self.date.text())
        except ValueError:
            return
        else:
            _next = get_next_num(self.cls, int(type), d.year)
            self.number_line_edit.setText(str(_next).zfill(6))

    def setCombos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()),
            (self.warehouse, utils.warehouse_id_map.keys()),
            (self.courier, utils.courier_id_map.keys())
        ]:
            combo.addItems(data)

    def populate_form(self):

        p = self.invoice.proformas[0]

        self.type.setCurrentText(str(self.invoice.type))
        self.number.setText(str(self.invoice.number))
        self.date.setText(self.invoice.date.strftime('%d%m%Y'))
        self.eta.setText(self.invoice.eta.strftime('%d%m%Y'))
        self.note.setText(self.invoice.note)
        self.external.setText(self.invoice.external)
        self.tracking.setText(self.invoice.tracking)
        self.agent.setCurrentText(p.agent.fiscal_name)
        self.warehouse.setCurrentText(p.warehouse.description)
        self.courier.setCurrentText(p.courier.description)
        self.incoterms.setCurrentText(p.incoterm)
        self.warranty.setValue(p.warranty)
        self.days_credit.setValue(p.credit_days)
        self.eur.setChecked(p.eur_currency)
        self.usd.setChecked(not p.eur_currency)

        self.with_credit.setValue(p.credit_amount)
        self.they_pay_they_ship.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship.setChecked(p.we_pay_we_ship)

        self.partner.setText(p.partner_name)

    def update_objects(self):
        self.invoice.date = utils.parse_date(self.date.text())
        self.invoice.eta = utils.parse_date(self.eta.text())
        self.invoice.type = int(self.type.currentText())
        self.invoice.number = int(self.number.text())

        for p in self.invoice.proformas:

            p.external = self.external.text()
            p.tracking = self.tracking.text()
            p.partner_id = utils.partner_id_map[self.partner.text()]
            p.agent_id = utils.agent_id_map[self.agent.currentText()]
            p.warehouse_id = utils.warehouse_id_map[self.warehouse.currentText()]
            p.courier_id = utils.courier_id_map[self.courier.currentText()]
            p.warranty = self.warranty.value()
            p.note = self.note.toPlainText()

            p.they_pay_they_ship = self.they_pay_they_ship.isChecked()
            p.we_pay_we_ship = self.we_pay_we_ship.isChecked()

            if isinstance(self.invoice, SaleInvoice):
                p.they_pay_we_ship = self.wildcard.isChecked()
            else:
                p.we_pay_they_ship = self.wildcard.isChecked()

            p.eur_currency = self.eur.isChecked()
            
            p.credit_amount = self.with_credit.value()
            p.credit_days = self.days_credit.value()
            p.incoterm = self.incoterms.currentText()

    def set_wildcard(self):
        if isinstance(self.invoice, SaleInvoice):
            self.wildcard.setText('They Pay We Ship')
        else:
            self.wildcard.setText('We pay they ship')

    def valid_header(self):
        try:
            int(self.number.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Number must be an integer number')
            return

        try:
            utils.parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Error in date format: ddmmyyyy')
            return False

        try:
            utils.parse_date(self.eta.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'Error in eta format: ddmmyyyy')
            return False

        try:
            utils.partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Error', 'Invalid Partner')
            return False

        return True

    def update_totals(self):
        self.total.setText(str(self.invoice.total_debt))
        self.tax.setText(str(self.invoice.tax))
        try:
            self.cn.setText(str(self.invoice.cn_total))
        except AttributeError:
            self.cn.setText(str(0))

        self.pending.setText(str(self.invoice.total_debt - self.invoice.total_paid))
        self.subtotal.setText(str(self.invoice.subtotal))
        self.quantity.setText('Qnt.: ' + str(self.model.quantity))

    def apply_cn_handler(self):
        from apply_credit_note_form import Form
        Form(self, self.invoice).exec_()

    def delete_handler(self):
        self.model.delete({i.row() for i in self.view.selectedIndexes()})
        self.set_totals()
        self.view.clearSelection()

    def save_handler(self):
        if not self.valid_header():
            return
        self.update_objects()

        for proforma in self.invoice.proformas:
            self.update_warehouse_callback(proforma)

        session.commit()
        QMessageBox.information(self, 'Success', 'Data updated')




    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        session.rollback()
