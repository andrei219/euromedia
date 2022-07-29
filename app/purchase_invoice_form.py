from PyQt5 import QtGui

from ui_purchase_invoice_form import Ui_PurchaseProformaForm

from PyQt5.QtWidgets import QWidget, QMessageBox

import db

from models import PurchaseInvoiceLineModel, update_purchase_warehouse

import utils


class Form(Ui_PurchaseProformaForm, QWidget):

    def __init__(self, invoice):
        super().__init__()
        self.setupUi(self)
        # proforma model used for update warehouse model

        self.invoice = invoice
        self.model = PurchaseInvoiceLineModel(invoice)
        self.lines_view.setModel(self.model)
        self.create_line_group.setVisible(False)
        self.create_line_group.setDisabled(True)
        self.note.setPlaceholderText('Purchase Invoice Note (Max 255) ...')
        self.setWindowTitle('Invoice Form')

        self.deleteButton.clicked.connect(self.delete_handler)
        self.save_button.clicked.connect(self.save_handler)

        self.set_combos()
        utils.setCompleter(self.partner_line_edit, utils.partner_id_map.keys())

        self.warehouse_combobox.setDisabled(True)

        self.set_form()

    def delete_handler(self):
        self.model.delete({index.row() for index in self.lines_view.selectedIndexes()})

    def save_handler(self):
        if not self._validHeader():
            return
        self.set_data() # Update orm objects fields, sqlachemy will do the rest
        db.session.commit()
        for proforma in self.invoice.proformas:
            update_purchase_warehouse(proforma)

        QMessageBox.critical(self, 'Success', 'Data saved')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        db.session.rollback()

    def set_combos(self):
        for combo, data in [
            (self.agent_combobox, utils.agent_id_map.keys()),
            (self.warehouse_combobox, utils.warehouse_id_map.keys()),
            (self.courier_combobox, utils.courier_id_map.keys())
        ]: combo.addItems(data)

    def set_form(self):
        p = self.invoice.proformas[0]
        self.type_combo_box.setCurrentText(str(self.invoice.number))
        self.number_line_edit.setText(str(self.invoice.number))
        self.date_line_edit.setText(self.invoice.date.strftime('%d%m%Y'))
        self.eta_line_edit.setText(self.invoice.eta.strftime('%d%m%Y'))

        self.agent_combobox.setCurrentText(p.agent.fiscal_name)
        self.warehouse_combobox.setCurrentText(p.warehouse.description)
        self.courier_combobox.setCurrentText(p.courier.description)
        self.incoterms_combo_box.setCurrentText(p.incoterm)
        self.warranty_spinbox.setValue(p.warranty)
        self.days_credit_spinbox.setValue(p.credit_days)
        self.eur_radio_button.setChecked(p.eur_currency)
        self.usd_radio_button.setChecked(not p.eur_currency)

        self.with_credit_spinbox.setValue(p.credit_amount)
        self.external_line_edit.setText(p.external)
        self.tracking_line_edit.setText(p.tracking)
        self.they_pay_they_ship_shipping_radio_button.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship_shipping_radio_button.setChecked(p.we_pay_we_ship)
        self.we_pay_they_ship_shipping_radio_button.setChecked(p.we_pay_they_ship)
        self.note.setText(p.note)
        self.partner_line_edit.setText(p.partner.fiscal_name)

    def _validHeader(self):
        try:
            utils.partner_id_map[self.partner_line_edit.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False
        try:
            utils.parse_date(self.date_line_edit.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False
        try:
            utils.parse_date(self.eta_line_edit.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in eta field. Format : ddmmyyyy')
            return False
        return True

    def set_data(self):
        for proforma in self.invoice.proformas:
            proforma.warranty = self.warranty_spinbox.value()
            proforma.eta = utils.parse_date(self.eta_line_edit.text())
            proforma.they_pay_they_ship = self.they_pay_they_ship_shipping_radio_button.isChecked()
            proforma.we_pay_we_ship = self.we_pay_we_ship_shipping_radio_button.isChecked()
            proforma.we_pay_they_ship = self.we_pay_they_ship_shipping_radio_button.isChecked()
            proforma.partner_id = utils.partner_id_map[self.partner_line_edit.text()]
            proforma.agent_id = utils.agent_id_map[self.agent_combobox.currentText()]
            proforma.warehouse_id = utils.warehouse_id_map[self.warehouse_combobox.currentText()]
            proforma.courier_id = utils.courier_id_map[self.courier_combobox.currentText()]
            proforma.eur_currency = self.eur_radio_button.isChecked()
            proforma.credit_amount = self.with_credit_spinbox.value()
            proforma.credit_days = self.days_credit_spinbox.value()
            proforma.incoterm = self.incoterms_combo_box.currentText()
            proforma.external = self.external_line_edit.text()
            proforma.tracking = self.tracking_line_edit.text()



