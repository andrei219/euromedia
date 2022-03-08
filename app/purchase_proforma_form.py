
from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView

from PyQt5.QtCore import QStringListModel, Qt

from importlib import reload
import utils

from utils import parse_date, setCompleter

from ui_purchase_proforma_form import Ui_PurchaseProformaForm

from decorators import ask_save

import models, db

from datetime import date

from exceptions import DuplicateLine
 
from db import Partner, PurchaseProformaLine, PurchaseProforma, \
    PurchasePayment, func, Agent


def reload_utils():
    from importlib import reload 
    global utils
    utils = reload(utils)


class Form(Ui_PurchaseProformaForm, QWidget):
    
    def __init__(self, parent, view):
        reload_utils()
        super().__init__() 
        self.setupUi(self)
        self.parent = parent 
        self.model = view.model() 
        self.view = view 
        self.lines_model = models.PurchaseProformaLineModel(lines=[], form=self) 
        self.lines_view.setModel(self.lines_model)
        self.title = 'Line - Error'
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.setUp() 
        self.is_invoice = False 


    def setUp(self):

        self.partner_line_edit.setFocus() 

        self.type_combo_box.setCurrentText('1')
        self.number_line_edit.setText(str(self.model.nextNumberOfType(1)).zfill(6))
        self.date_line_edit.setText(date.today().strftime('%d%m%Y'))

        self.setCombos()
        self.setCompleters() 
        

        def priceOrQuantityChanged(value):
            self.subtotal_spinbox.setValue(self.quantity_spinbox.value() * self.price_spinbox.value())
        
        def subtotalOrTaxChanged(value):
            self.total_spinbox.setValue(self.subtotal_spinbox.value() * (1 + int(self.tax_combobox.currentText())/100))

        def typeChanged(type):
            next_num = self.model.nextNumberOfType(int(type))
            self.number_line_edit.setText(str(next_num).zfill(6))

        self.price_spinbox.valueChanged.connect(priceOrQuantityChanged) 
        self.quantity_spinbox.valueChanged.connect(priceOrQuantityChanged)
        self.tax_combobox.currentIndexChanged.connect(subtotalOrTaxChanged)
        self.subtotal_spinbox.valueChanged.connect(subtotalOrTaxChanged)
        self.type_combo_box.currentTextChanged.connect(typeChanged)

        self.partner_line_edit.textChanged.connect(self.partnerSearch)
        self.addButton.clicked.connect(self.addHandler)
        self.deleteButton.clicked.connect(self.deleteHandler)
        self.save_button.clicked.connect(self.saveHandler) 

    def setCombos(self):
        for combo, data in [
            (self.agent_combobox, utils.agent_id_map.keys()), 
            (self.warehouse_combobox, utils.warehouse_id_map.keys()), 
            (self.courier_combobox, utils.courier_id_map.keys())
        ]: combo.addItems(data)

    def setCompleters(self):
        for field, data in [
            (self.partner_line_edit, utils.partner_id_map.keys()),
            (self.description_line_edit, utils.descriptions), 
            (self.spec_line_edit, utils.specs), 
            (self.condition_line_edit, utils.conditions)]:
            setCompleter(field, data)


    def partnerSearch(self):

        partner = self.partner_line_edit.text()
        if partner in utils.partner_id_map.keys():
            partner_id = utils.partner_id_map.get(self.partner_line_edit.text())
            if not partner_id:
                return
            try:
                available_credit = models.computeCreditAvailable(partner_id) 
                self.available_credit_spinbox.setValue(float(available_credit))
                self.with_credit_spinbox.setMaximum(0.0 if available_credit < 0 else available_credit)

            except TypeError:
                raise 

            result = db.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,\
                Partner.they_pay_they_ship, Partner.we_pay_they_ship, Partner.we_pay_we_ship,\
                    Partner.days_credit_limit).join(Agent).where(Partner.id == partner_id).one() 

            agent, warranty, euro, they_pay_they_ship, we_pay_they_ship, we_pay_we_ship, days = \
                result

            self.agent_combobox.setCurrentText(agent)
            self.warranty_spinbox.setValue(warranty) 
            self.eur_radio_button.setChecked(euro) 
            self.usd_radio_button.setChecked( not euro)
            
            
            self.they_pay_they_ship_shipping_radio_button.setChecked(they_pay_they_ship) 
            self.we_pay_they_ship_shipping_radio_button.setChecked(we_pay_they_ship) 
            self.we_pay_we_ship_shipping_radio_button.setChecked(we_pay_we_ship) 


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

    def _clearLineFields(self):
        self.description_line_edit.setText('')
        self.spec_line_edit.setText('')
        self.condition_line_edit.setText('')
        self.quantity_spinbox.setValue(1)
        self.price_spinbox.setValue(0)

    def _updateTotals(self):
        self.total_tax_line_edit.setText(str(self.lines_model.tax))
        self.subtotal_proforma_line_edit.setText(str(self.lines_model.subtotal))
        self.total_proforma_line_edit.setText(str(self.lines_model.total))
        self.quantity.setText('Quantity:' + str(self.lines_model.quantity))

    def _dateFromString(self, date_str):
        return date(int(date_str[4:len(date_str)]), int(date_str[2:4]), int(date_str[0:2])) 

    def keyPressEvent(self, event):
        if self.addButton.hasFocus():
            if event.key() == Qt.Key_Return:
                self.addHandler()
                self.description_line_edit.setFocus()              
        else:
            super().keyPressEvent(event)

    def _formToProforma(self, input_proforma=None):
        # Allow this method to be used in subclass in order to update proforma
        if not input_proforma:
            proforma = db.PurchaseProforma() 
        else:
            proforma = input_proforma

        proforma.type = int(self.type_combo_box.currentText())
        proforma.number = int(self.number_line_edit.text())
        
        if self.is_invoice:
            proforma.invoice.date = self._dateFromString(self.date_line_edit.text())
            proforma.invoice.eta = self._dateFromString(self.eta_line_edit.text())
        else:
            proforma.date = self._dateFromString(self.date_line_edit.text())
            proforma.eta = self._dateFromString(self.date_line_edit.text())
        
        proforma.warranty = self.warranty_spinbox.value()
        proforma.eta = self._dateFromString(self.eta_line_edit.text())
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
        proforma.note = self.note.toPlainText()[0:255]
        return proforma

    def addHandler(self):
        
        description = self.description_line_edit.text()
        condition = self.condition_line_edit.text()
        spec = self.spec_line_edit.text()
        

        if not description:return 


        if description in utils.descriptions:
            if condition not in utils.conditions or spec not in utils.specs:
                QMessageBox.critical(self, 'Error', "Can't add stock without condition and spec")
                return 
        try:

            print('reached, description:', description)
            self.lines_model.add(self.description_line_edit.text(), \
                self.condition_line_edit.text(), self.spec_line_edit.text(), self.quantity_spinbox.value(),\
                    self.price_spinbox.value(), int(self.tax_combobox.currentText()))
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            return         
        
        self._updateTotals() 
        self._clearLineFields()
        self.lines_view.resizeColumnToContents(0)

    def deleteHandler(self):
        indexes = self.lines_view.selectedIndexes() 
        if not indexes:return 
        try:
            self.lines_model.delete(indexes)
        except:
            raise 

    def saveHandler(self):
        if not self._validHeader():
            return 
       
        proforma = self._formToProforma() 
        try:
            
            self.model.add(proforma) 
            self.lines_model.save(proforma) 
        except:
            raise 
        else:
            QMessageBox.information(self, 'Information','Purchase saved successfully')
            self.adjust_view()
            self.close()
    
    def adjust_view(self):
        self.view.resizeColumnToContents(3)
        self.view.resizeColumnToContents(4) 


    def closeEvent(self, event):
        db.session.rollback() 

class EditableForm(Form):
    
    def __init__(self, parent, view, proforma:db.PurchaseProforma, is_invoice=False):
        reload_utils()
        super(QWidget, Form).__init__(self) 
        self.setupUi(self)
        self.parent = parent
        self.proforma = proforma 
        self.view = view 
        self.type_combo_box.setEnabled(False) 
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.title = 'Line - Error'
        self.model = view.model() 
        self.is_invoice = is_invoice 
        if is_invoice:
            self.setWindowTitle('Proforma / Invoice Edit')
        else:
            self.setWindowTitle('Proforma Edit ')

        self.disable_things()
        
        self.lines_model = models.PurchaseProformaLineModel(
            lines = proforma.lines,
            form = self
        )
        
        self._updateTotals()
        self.lines_view.setModel(self.lines_model) 
        self.lines_view.resizeColumnToContents(0)

        self.setUp()
        self.proforma_to_form()

    def disable_things(self):
        try:
            if sum(1 for line in self.proforma.reception.lines for serie in line.series):
                self.warehouse_combobox.setEnabled(False)
        except AttributeError:
            pass 
        
        self.partner_line_edit.setReadOnly(True)
        self.eta_line_edit.setReadOnly(True)
        
    def setHandlers(self):
        self.deleteButton.clicked.connect(self.deleteHandler)
        self.addButton.clicked.connect(self.addHandler)
        self.partner_line_edit.returnPressed.connect(self.partnerSearch)
        self.save_button.clicked.connect(self.saveHandler)

    def proforma_to_form(self):
        p = self.proforma
        self.type_combo_box.setCurrentText(str(p.type))
        self.number_line_edit.setText(str(p.number))
        
        date = p.invoice.date if self.is_invoice else p.date        
        self.eta_line_edit.setText(date.strftime('%d%m%Y'))
        self.partner_line_edit.setText(p.partner.fiscal_name)
        self.agent_combobox.setCurrentText(p.agent.fiscal_name)
        self.warehouse_combobox.setCurrentText(p.warehouse.description)
        self.courier_combobox.setCurrentText(p.courier.description)
        self.incoterms_combo_box.setCurrentText(p.incoterm)
        self.warranty_spinbox.setValue(p.warranty)
        self.days_credit_spinbox.setValue(p.credit_days)
        self.eur_radio_button.setChecked(p.eur_currency)
        self.with_credit_spinbox.setValue(p.credit_amount)
        self.external_line_edit.setText(p.external)
        self.tracking_line_edit.setText(p.tracking)
        self.they_pay_they_ship_shipping_radio_button.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship_shipping_radio_button.setChecked(p.we_pay_we_ship)
        self.we_pay_they_ship_shipping_radio_button.setChecked(p.we_pay_they_ship)
        self.note.setText(p.note) 

    def saveHandler(self):
        if not super()._validHeader():
            return

        self._formToProforma(input_proforma=self.proforma)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise 
        else:
            try:
                warehouse_updated = self.model.updateWarehouse(self.proforma) 
                # advance_sale_updated = self.model.updateAdvancedSale(self.proforma) 
            except:
                raise 
            else:
                message = "Proforma saved successfully."
                if warehouse_updated:
                    message += 'Warehouse Updated' 

                QMessageBox.information(self, "Information", message) 

            self.adjust_view() 
            # self.close()



