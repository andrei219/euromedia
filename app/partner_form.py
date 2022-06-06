
from PyQt5.QtWidgets import QWidget, QTableView, QMessageBox
from PyQt5.QtCore import Qt

from ui_partner_form import Ui_Partner_Form

from db import Partner, PartnerDocument, Agent, engine, Courier 

from models import PartnerContactModel


import utils

from sqlalchemy import select 


import db 

class PartnerForm(Ui_Partner_Form, QWidget):

    EDITABLE_MODE, NEW_MODE = 0, 1 

    def __init__(self, parent, view, index=None):
        super().__init__()
        self.setupUi(self) 
        self.partner_model = view.model() 
        self.parent = parent
        self.view = view 

        self.billing_country_combobox.addItems(utils.countries) 
        self.shipemnt_country_combobox.addItems(utils.countries)
        
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
            self.shipemnt_country_combobox.setCurrentText('Spain')
            self.billing_country_combobox.setCurrentText('Spain')

        self.setUpContactView(self.partner.contacts)
        
    def copyAddress(self):
        self.shipment_address_line_edit.setText(self.billing_address1_line_edit.text())
        self.shipment_address2_line_edit.setText(self.billing_address2_line_edit.text())
        self.shipment_postcode_line_edit.setText(self.billing_postcode_line_edit.text())
        self.shipment_state_line_edit.setText(self.billing_state_line_edit.text())
        self.shipment_city_line_edit.setText(self.billing_city_line_edit.text())
        self.shipemnt_country_combobox.setCurrentText(self.billing_country_combobox.currentText())

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
        if not self.partner.contacts:
            QMessageBox.critical(self, 'Partner - Update', 'At least one contact must be provided!')
            return

        if ' ' in self.fiscal_number_line_edit.text():
            QMessageBox.critical(self, 'Partner', 'Vesi, Sin espacio el fiscal number!')
            return

        if self.mode == PartnerForm.EDITABLE_MODE:
            self.formToPartner() 
            try:
                db.session.commit()
                QMessageBox.information(self, 'Partner - Update', 'Partner Updated Successfully')
                self.close() 
            except:
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
            except:
                raise 
                QMessageBox.critical(self, 'Partner - Update', ' Error Updating Partner')

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
                self.copyAddress() 
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
        self.partner.shipping_line1 = self.shipment_address_line_edit.text()
        self.partner.shipping_line2 = self.shipment_address2_line_edit.text()
        self.partner.shipping_postcode = self.shipment_postcode_line_edit.text()
        self.partner.shipping_state = self.shipment_state_line_edit.text()
        self.partner.shipping_city = self.shipment_city_line_edit.text()
        self.partner.shipping_country = self.shipemnt_country_combobox.currentText() 
        
        try:
            self.partner.agent = db.session.query(Agent).where(Agent.fiscal_name == \
                self.associated_agent_combobox.currentText()).one() 
        except:
            raise

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
        self.shipment_address_line_edit.setText(self.partner.shipping_line1)
        self.shipment_address2_line_edit.setText(self.partner.shipping_line2)
        self.shipment_postcode_line_edit.setText(self.partner.shipping_postcode)
        self.shipment_state_line_edit.setText(self.partner.shipping_state)
        self.shipment_city_line_edit.setText(self.partner.shipping_city)
        self.shipemnt_country_combobox.setCurrentText(self.partner.shipping_country)
        
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

    def setUpContactView(self, contacts):
        self.contact_model = PartnerContactModel(self.contact_view, contacts)
        self.contact_view.setModel(self.contact_model)
        self.contact_view.setSelectionBehavior(QTableView.SelectRows)
        self.contact_view.setSelectionMode(QTableView.SingleSelection)
        self.contact_view.resizeColumnsToContents() 

    def disableDocuments(self):
        self.docs_button.setToolTip('Save partner to enable attaching documents and contact people')
        self.docs_button.setToolTipDuration(2000)
        self.docs_button.setEnabled(False)

    def enableDocuments(self):
        self.docs_button.setToolTipDuration(0)
        self.docs_button.setEnabled(True)

    def setUpHandlers(self):
        self.copy_address_button.clicked.connect(self.copyAddress)
        self.billing_country_combobox.currentTextChanged.connect(self.enablecheckboxs)
        self.shipemnt_country_combobox.currentTextChanged.connect(self.enablecheckboxs) 
        self.add_row_button.clicked.connect(self.addContact)
        self.delete_row_button.clicked.connect(self.removeContact)
        self.docs_button.clicked.connect(self.docsButtonHandler)
        self.save_button.clicked.connect(self.saveButtonHandler)
        self.bank_button.clicked.connect(self.bank_button_handler) 

    
    def bank_button_handler(self):
        import bank_form 
        bank_form.Dialog(self, self.partner).exec_()

    def closeEvent(self, event):
        # if not self.partner.contacts and self.mode == PartnerForm.EDITABLE_MODE:
        #     QMessageBox.critical(self, 'Error - Update', 'You need to provide at least one contact')
        #     event.ignore()

        # if not self.partner.contacts:
        #     QMessageBox.critical(self, 'Error', 'At least one contact mus be provided')
        #     event.ignore()
    
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
        except:
            pass