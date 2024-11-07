from PyQt5.QtWidgets import QWidget, QTableView, QMessageBox
from PyQt5.QtCore import Qt

from ui_partner_form import Ui_Partner_Form

from db import Partner, Agent, ShippingAddress

from models import PartnerContactModel, ShippingAddressModel
from delegates import AddressEditDelegate

import utils

from sqlalchemy import select 

import db 
import contextlib

from sqlalchemy.exc import DatabaseError

class PartnerForm(Ui_Partner_Form, QWidget):

    EDITABLE_MODE, NEW_MODE = 0, 1 

    def __init__(self, parent, view, index=None):
        super().__init__()
        self.setupUi(self) 
        self.partner_model = view.model() 
        self.parent = parent
        self.view = view 

        self.billing_country_combobox.addItems(utils.countries) 

        self.active_checkbox.setFocus()
        self.re_checkbox.setEnabled(False)
        self.re_checkbox.setEnabled(False)

        self.setUpHandlers() 

        agent_names = [r[0] for r in db.session.query(Agent.fiscal_name).\
            where(Agent.active == True)]

        self.associated_agent_combobox.addItems(agent_names)
        
        if index:
            self.mode = PartnerForm.EDITABLE_MODE
            self.partner = self.partner_model.partners[index.row()]
            self.partnerToForm() 
        else:
            self.mode = PartnerForm.NEW_MODE
            self.euro_radiobutton.setChecked(True)
            self.they_pay_we_ship_radiobutton.setChecked(True)
            self.disableDocuments() 
            self.partner = Partner() 
            self.billing_country_combobox.setCurrentText('Spain')

        self.setUpContactView(self.partner.contacts)
        self.set_up_shipping_view(self.partner.shipping_addresses)

    def copy_address(self):
        self.partner.shipping_addresses.append(
            ShippingAddress(
                line1=self.billing_address1_line_edit.text(),
                line2=self.billing_address2_line_edit.text(),
                city=self.billing_city_line_edit.text(),
                state=self.billing_state_line_edit.text(),
                zipcode=self.billing_postcode_line_edit.text(),
                country=self.billing_country_combobox.currentText()
            )
        )
        self.set_up_shipping_view(self.partner.shipping_addresses)

    def enablecheckboxs(self, text):
        if text == 'Spain':
            self.isp_checkbox.setEnabled(True)
            self.re_checkbox.setEnabled(True)
        else:
            self.isp_checkbox.setEnabled(False)
            self.re_checkbox.setEnabled(False)

    def docsButtonHandler(self):
        from documents_form import Form
        f = Form(self, self.partner)
        f.exec_()

    def saveButtonHandler(self):
        # pre-fix some stuff 
        self.fiscal_number_line_edit.setText(self.fiscal_number_line_edit.text().replace(' ', '')) 

        if not self.partner.contacts:
            self.partner.contacts.append(db.PartnerContact.default()) 
            self.setUpContactView(self.partner.contacts)

        if self.shipping_model.empty:
            self.copy_address()

        if not self.shipping_model.valid:
            QMessageBox.critical(self, 'Partner', 'Invalid Shipping address. Only Line2 and State are optional.')
            return

        if self.mode == PartnerForm.EDITABLE_MODE:
            self.formToPartner() 
            try:
                db.session.commit()
                QMessageBox.information(self, 'Partner - Update', 'Partner Updated Successfully')
                self.close() 
            except Exception as ex:
                db.session.rollback()
                QMessageBox.critical(self, 'Partner - Update ', ' Error Updating Partner')

        elif self.mode == PartnerForm.NEW_MODE:
            self.formToPartner() 
            try:
                self.view.model().add(self.partner)
                self.partner_code_line_edit.setText(str(self.partner.id))
                self.mode = PartnerForm.EDITABLE_MODE
                self.enableDocuments() 
                QMessageBox.information(self, 'Partner - Update', 'Partner Created Successfully')                
            
            except DatabaseError as ex:
                db.session.rollback()
                QMessageBox.critical(self, 'Partner - Creation - Error', 'Fiscal name, Fiscal Number and Trading name must be provided')

            except Exception as ex:
                db.session.rollback()
                QMessageBox.critical(self, 'Partner - Update', f'Error Updating Partner: {ex}')	

    def addContact(self):
        row = self.contact_view.model().rowCount()
        self.contact_view.model().insertRow(row)
        index = self.contact_view.model().index(row, 0)
        self.contact_view.setCurrentIndex(index) 
        self.contact_view.edit(index)

    def removeContact(self):
        index = self.contact_view.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        self.contact_view.model().removeRows(row)
        self.contact_view.resizeColumnsToContents() 

    def keyPressEvent(self, event):
        if self.contact_view.hasFocus():
            if event.modifiers() & Qt.ControlModifier:
                if event.key() == Qt.Key_N:
                    self.addContact()
                elif event.key() == Qt.Key_D:
                    self.removeContact()
        elif self.copy_address_button.hasFocus():
            if event.key() == Qt.Key_Return:
                self.copy_address()
        elif self.active_checkbox.hasFocus():
            if event.key() == Qt.Key_Return and self.active_checkbox.isChecked():
                self.active_checkbox.setChecked(False)
            else:
                self.active_checkbox.setChecked(True)
        else:
            super().keyPressEvent(event)
                
    def formToPartner(self):
        self.partner.active = self.active_checkbox.isChecked()
        self.partner.fiscal_name = self.fical_name_line_edit.text()
        self.partner.fiscal_number = self.fiscal_number_line_edit.text()
        self.partner.trading_name = self.trading_name_line_edit.text()
        self.partner.warranty = self.warranty_spinbox.value()
        self.partner.billing_line1 = self.billing_address1_line_edit.text()
        self.partner.billing_line2 = self.billing_address2_line_edit.text()
        self.partner.billing_postcode = self.billing_postcode_line_edit.text()
        self.partner.billing_city = self.billing_city_line_edit.text()
        self.partner.billing_state = self.billing_state_line_edit.text()
        self.partner.billing_country = self.billing_country_combobox.currentText()

        self.partner.has_certificate = self.has_certificate.isChecked()
        
        # Should never raise exception. Input comes from combobox. 
        # we have a closed space of object. 
        # On db, there there as unique restriction on fiscal name.
        self.partner.agent = db.session.query(Agent).where(Agent.fiscal_name == \
            self.associated_agent_combobox.currentText()).one() 
    
        self.partner.days_credit_limit = self.credit_days_spinbox.value()
        self.partner.amount_credit_limit = self.credit_amount_spinbox.value()

        self.partner.euro = self.euro_radiobutton.isChecked() 

        self.partner.they_pay_they_ship = self.they_pay_we_ship_radiobutton.isChecked() 
        self.partner.they_pay_we_ship = self.they_pay_we_ship_radiobutton.isChecked() 
        self.partner.we_pay_they_ship = self.we_pay_they_ship_radiobutton.isChecked() 
        self.partner.we_pay_we_ship = self.we_pay_we_ship_radiobutton.isChecked() 

        self.partner.isp = self.isp_checkbox.isChecked()
        self.partner.re = self.re_checkbox.isChecked() 

        self.partner.note = self.note_text_edit.toPlainText() 

    def partnerToForm(self):
        self.partner_code_line_edit.setText(str(self.partner.id))
        self.active_checkbox.setChecked(self.partner.active)
        self.fiscal_number_line_edit.setText(self.partner.fiscal_number)
        self.fical_name_line_edit.setText(self.partner.fiscal_name)
        self.trading_name_line_edit.setText(self.partner.trading_name)
        self.associated_agent_combobox.setCurrentText(self.partner.agent.fiscal_name)
        self.warranty_spinbox.setValue(self.partner.warranty)
        self.billing_address1_line_edit.setText(self.partner.billing_line1)
        self.billing_address2_line_edit.setText(self.partner.billing_line2)
        self.billing_postcode_line_edit.setText(self.partner.billing_postcode)
        self.billing_state_line_edit.setText(self.partner.billing_state)
        self.billing_country_combobox.setCurrentText(self.partner.billing_country)
        self.billing_city_line_edit.setText(self.partner.billing_city)

        self.credit_amount_spinbox.setValue(self.partner.amount_credit_limit)
        self.credit_days_spinbox.setValue(self.partner.days_credit_limit)

        self.dolar_radiobutton.setChecked(True if not self.partner.euro else False)
        self.euro_radiobutton.setChecked(True if self.partner.euro else False)
    
        self.they_pay_they_ship_radiobutton.setChecked(self.partner.they_pay_they_ship)
        self.they_pay_we_ship_radiobutton.setChecked(self.partner.they_pay_we_ship)
        self.we_pay_they_ship_radiobutton.setChecked(self.partner.we_pay_they_ship)
        self.we_pay_we_ship_radiobutton.setChecked(self.partner.we_pay_we_ship)

        self.note_text_edit.setText(self.partner.note)

        self.isp_checkbox.setChecked(self.partner.isp)
        self.re_checkbox.setChecked(self.partner.re)
        self.has_certificate.setChecked(self.partner.has_certificate)

    def setUpContactView(self, contacts):
        self.contact_model = PartnerContactModel(self.contact_view, contacts)
        self.contact_view.setModel(self.contact_model)
        self.contact_view.resizeColumnsToContents()

    def set_up_shipping_view(self, addresses):
        self.shipping_model = ShippingAddressModel(self.shipping_view, addresses)
        self.shipping_view.setItemDelegate(AddressEditDelegate())
        self.shipping_view.setModel(self.shipping_model)
        self.shipping_view.resizeColumnsToContents()

    def disableDocuments(self):
        self.docs_button.setToolTip('Save partner to enable attaching documents and contact people')
        self.docs_button.setToolTipDuration(2000)
        self.docs_button.setEnabled(False)

    def enableDocuments(self):
        self.docs_button.setToolTipDuration(0)
        self.docs_button.setEnabled(True)

    def setUpHandlers(self):
        self.copy_address_button.clicked.connect(self.copy_address)
        self.billing_country_combobox.currentTextChanged.connect(self.enablecheckboxs)
        self.add_row_button.clicked.connect(self.addContact)
        self.delete_row_button.clicked.connect(self.removeContact)
        self.docs_button.clicked.connect(self.docsButtonHandler)
        self.save_button.clicked.connect(self.saveButtonHandler)
        self.bank_button.clicked.connect(self.bank_button_handler)
        self.shipping_add.clicked.connect(self.add_shipping_address)
        self.shipping_delete.clicked.connect(self.remove_shipping_address)

    def add_shipping_address(self):
        row = self.shipping_view.model().rowCount()
        self.shipping_view.model().insertRow(row)
        index = self.shipping_view.model().index(row, 0)
        self.shipping_view.setCurrentIndex(index)
        self.shipping_view.edit(index)

    def remove_shipping_address(self):
        index = self.shipping_view.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        
        try:
            self.shipping_view.model().removeRows(row)
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
        else:
            self.shipping_view.resizeColumnsToContents()

    def bank_button_handler(self):
        import bank_form 
        bank_form.Dialog(self, self.partner).exec_()

    def closeEvent(self, event):
        with contextlib.suppress(Exception):
            self.parent.opened_windows_classes.remove(self.__class__) 
