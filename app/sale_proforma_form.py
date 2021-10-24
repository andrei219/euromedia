
from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtCore import QAbstractTableModel

from utils import parse_date, setCompleter

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import AvailableStockModel, SaleProformaLineModel, ManualStockModel, \
    ActualLinesFromMixedModel

import db

import models

from db import Agent, Partner, SaleProformaLine, SaleProforma, SalePayment, func

from utils import setCommonViewConfig

from exceptions import DuplicateLine

from quantity_price_form import QuantityPriceForm

class Form(Ui_SalesProformaForm, QWidget):

    def __init__(self, parent, view):
        super().__init__() 
        self.setupUi(self) 
        self.model = view.model() 
        self.parent = parent

        self.lines_model = SaleProformaLineModel()
        self.lines_view.setModel(self.lines_model)
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        
        self.setCombos()
        self.setCompleters()
        self.set_handlers()

    def set_handlers(self):
        self.search.clicked.connect(self.search_handler) 
        self.stock_view.doubleClicked.connect(self.stock_double_clicked)
        self.delete_all.clicked.connect(self.delete_all_handler)
        self.lines_view.clicked.connect(self.lines_view_clicked_handler)
        self.delete_button.clicked.connect(self.delete_handler)
        self.generate.clicked.connect(self.generate_handler) 
        self.save.clicked.connect(self.save_handler)
        self.partner.returnPressed.connect(self.partner_search)
    

    def setCombos(self):
        for combo, data in [
            (self.agent, models.agent_id_map.keys()), 
            (self.warehouse, models.warehouse_id_map.keys()), 
            (self.courier, models.courier_id_map.keys())
        ]: combo.addItems(data)

    def setCompleters(self):
        for field, data in [
            (self.partner, models.partner_id_map.keys()), 
            (self.description, models.descriptions), 
            (self.spec, models.specs), 
            (self.condition, models.conditions)
        ]: setCompleter(field, data)

    def partner_search(self):
        partner_id = models.partner_id_map.get(self.partner.text())
        if not partner_id:
            return
        try:
            available_credit = models.computeCreditAvailable(partner_id) 
            self.available_credit.setValue(float(available_credit))
            self.credit.setMaximum(float(available_credit))
        
        except TypeError:
            raise 
            
        result = db.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,\
            Partner.they_pay_they_ship, Partner.they_pay_we_ship, Partner.we_pay_we_ship,\
                Partner.days_credit_limit).join(Agent).where(Partner.id == partner_id).one() 

        agent, warranty, euro, they_pay_they_ship, they_pay_we_ship, we_pay_we_ship, days = \
            result

        self.agent.setCurrentText(agent)
        self.warranty.setValue(warranty) 
        self.eur.setChecked(euro) 
        self.they_pay_they_ship.setChecked(they_pay_they_ship) 
        self.they_pay_we_ship.setChecked(they_pay_we_ship) 
        self.we_pay_we_ship.setChecked(we_pay_we_ship) 


    def lines_view_clicked_handler(self):
        print('ee')

    def search_handler(self):
        if self.filters_unset():
            QMessageBox.critical(self, 'Error - Search', 'Set filters.')
            return 

    def filters_unset(self):
        return any((
            self.description.text() not in models.descriptions, 
            self.spec.text() not in models.specs, 
            self.condition.text() not in models.conditions
        )) 

    def apply_handler(self):
        pass 

    def remove_handler(self):
        pass 

    def insert_handler(self):
        pass     

    def delete_handler(self):
        pass

    def delete_all_handler(self):
        pass 

    def generate_handler(self):
        pass 

    def save_handler(self):
        pass 

    def stock_double_clicked(self):
        from line_complete_form import Form

        row = self.stock_view.currentIndex().row() 
        stock = self.stock_model.stocks[row]
        f = Form(self) 
        f.qnt.setMaximum(stock.quantity) 
        if f.exec_():
            showing, qnt, price, ignore, tax = \
                f.condition.text(), f.qnt.value(), f.price.value(), \
                    f.ignore_spec.isChecked(), int(f.tax.currentText())
            try:
                item = self.base_items[stock.item] # Database object needs <db.Item> 
                self.lines_model.add(item, stock.condition, stock.spec, \
                    ignore, qnt, price, tax, showing_condition=showing)
               
                warehouse = self.warehouse.currentText()
                self.reset_stock(warehouse, item=None, condition=None, spec=None)
                self.update_total_fields() 
            except:
                raise 
    
    def update_total_fields(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

    def _valid_header(self):
        try:
            self.partner_name_to_id[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False
        try:
            parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False

    def _form_to_proforma(self):
        proforma = db.SaleProforma() 
        proforma.type = int(self.type.currentText())
        proforma.number = int(self.number.text())
        proforma.date = self._dateFromString(self.date.text())
        proforma.warranty = self.warranty.value()
        proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked() 
        proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked() 
        proforma.agent_id = self.agent_name_to_id[self.agent.currentText()]
        proforma.partner_id = self.partner_name_to_id[self.partner.text()]
        proforma.warehouse_id = self.warehouse_name_to_id[self.warehouse.currentText()]
        proforma.courier_id = self.courier_name_to_id[self.courier.currentText()]
        proforma.eur_currency = self.eur.isChecked()
        proforma.credit_amount = self.credit.value()
        proforma.credit_days = self.days.value() 
        proforma.incoterm = self.incoterms.currentText() 
        proforma.external = self.external.text() 
        proforma.tracking = self.tracking.text() 
        proforma.note = self.note.toPlainText()[0:255]
        return proforma

    def clear_filters(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear()


























class EditableForm(Form):

    def __init__(self, parent, view, proforma:db.SaleProforma):
        super(QWidget, Form).__init__(self) 
        self.setupUi(self) 
        self.parent = parent 
        self.type.setEnabled(False)
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.model = view.model() 
        try:
            proforma.invoice
            self.setWindowTitle('Proforma / Invoice Edit')
        except AttributeError:
            self.setWindowTitle('Proforma Edit')
            
    
    def set_warehouse_combo_enabled_if_no_items_processed(self):
        pass 

    
    def proforma_to_form(self):
        p = self.proforma 