
from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter,\
    QTableView
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtCore import QAbstractTableModel

from utils import parse_date, setCompleter

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import SaleProformaLineModel, ActualLinesFromMixedModel,\
    StockModel

import db

import models

from db import Agent, Partner, SaleProformaLine, SaleProforma,\
    SalePayment, func

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
        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        
        self.setCombos()
        self.setCompleters()
        self.set_handlers()

        self.date.setText(date.today().strftime('%d%m%Y'))
        self.type.setCurrentText('1')
        self.number.setText(str(self.model.nextNumberOfType(1)).zfill(6))

    def set_handlers(self):
        self.search.clicked.connect(self.search_handler) 
        self.lines_view.clicked.connect(self.lines_view_clicked_handler)
        self.delete_button.clicked.connect(self.delete_handler)
        self.add.clicked.connect(self.add_handler) 
        self.save.clicked.connect(self.save_handler)
        self.partner.returnPressed.connect(self.partner_search)
        self.apply.clicked.connect(self.apply_handler)
        self.remove.clicked.connect(self.remove_handler) 
        self.insert.clicked.connect(self.insert_handler) 
        self.type.currentTextChanged.connect(self.typeChanged)

    def typeChanged(self, type):
        next_num = self.model.nextNumberOfType(int(type))
        self.number_line_edit.setText(str(next_num).zfill(6))

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
        self.set_stock_mv()

    def set_stock_mv(self):
        warehouse_id = models.warehouse_id_map.get(
            self.warehouse.currentText()
        )
        description = self.description.text()
        condition = self.condition.text()
        spec = self.spec.text() 
        lines = self.lines_model.lines 
        
        if spec == 'Mix':
            spec = None
        
        if condition == 'Mix':
            condition = None
        
        self.stock_model = \
            StockModel(warehouse_id, description, condition, spec, lines) 
        self.stock_view.setModel(self.stock_model) 
        self.stock_view.resizeColumnsToContents() 

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

    def delete_handler(self):
        indexes = self.lines_view.selectedIndexes()
        if not indexes:
            return
        try:
            self.lines_model.delete(indexes)
        except:
            raise 
        else:
            self.set_stock_mv()
    
    def add_handler(self):
        if not hasattr(self, 'stock_model'):return

        requested_stocks = self.stock_model.requested_stocks

        if not requested_stocks:return 
        if not self.valid_mix(requested_stocks):return 

        price = self.price.value()
        ignore = self.ignore.isChecked()
        tax = int(self.tax.currentText())
        showing = self.showing_condition.text() or None

        try:
            self.lines_model.add(
                price, 
                ignore, 
                tax, 
                showing, 
                *requested_stocks
            )
        except ValueError:
            QMessageBox.critical(self, 'Error', 'I cant process duplicate stocks')
            return 
        else:
            self.set_stock_mv() 
            self.update_total_fields() 

    def valid_mix(self, requested_stocks):
        s = set() 
        for stock in requested_stocks:
            manufacturer, category, model, *_ = \
                models.description_id_map.inverse[stock.item_id].split() 
            s.add(''.join((manufacturer, category, model)))

        if len(s) != 1:
            QMessageBox.critical(
                self, 
                'Error', 
                'You can mix capacity or color'
            )
            return False 
        return True 

    def save_handler(self):
        if not self._valid_header():
            return 
        if not self.lines_model.lines:
            QMessageBox.critical(self, 'Error', "You cant let an empty proforma")
            return 
        
        proforma = self._form_to_proforma()
        try:
            self.model.add(proforma)             
            self.lines_model.save(proforma) 
        except:
            raise 
        else:
            QMessageBox.information(self, 'Information',\
                'Sale saved successfully')
            self.close()
    
    def update_total_fields(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

    def _valid_header(self):
        try:
            models.partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False
        try:
            parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False
        return True

    def _form_to_proforma(self, input_proforma=None):

        if not input_proforma:
            proforma = db.SaleProforma() 
        else:
            proforma = input_proforma

        proforma.type = int(self.type.currentText())
        proforma.number = int(self.number.text())
        proforma.date = parse_date(self.date.text())
        proforma.warranty = self.warranty.value()
        proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked() 
        proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked() 
        proforma.agent_id = models.agent_id_map[self.agent.currentText()]
        proforma.partner_id = models.partner_id_map[self.partner.text()]
        proforma.warehouse_id = models.warehouse_id_map[self.warehouse.currentText()]
        proforma.courier_id = models.courier_id_map[self.courier.currentText()]
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