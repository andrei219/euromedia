
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


class Form(Ui_SalesProformaForm, QWidget):

    def __init__(self, parent, view):
        super().__init__() 
        self.setupUi(self) 
        self.model = view.model() 
        self.init_template() 
        self.parent = parent
        self.lines_model = SaleProformaLineModel(self.proforma)
        self.lines_view.setModel(self.lines_model)
        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        setCommonViewConfig(self.selected_stock_view)
        
        self.setCombos()
        self.setCompleters()
        self.set_handlers()


    def init_template(self):
        
        print('init from form')
        self.proforma = db.SaleProforma() 
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
        self.delete_selected_stock.clicked.connect(self.delete_selected_stock_clicked)
        self.deselect.clicked.connect(lambda : self.lines_view.clearSelection())

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

    def proforma_to_form(self):
        p = self.proforma
        print('proforma to form:', p.warehouse.description)


        self.type.setCurrentText(str(p.type))
        self.number.setText(str(p.number))
        self.date.setText(p.date.strftime('%d%m%Y'))
        self.partner.setText(p.partner.fiscal_name)
        self.agent.setCurrentText(p.agent.fiscal_name)
        self.warehouse.setCurrentText(p.warehouse.description)
        self.courier.setCurrentText(p.courier.description)
        self.incoterms.setCurrentText(p.incoterm)
        self.warranty.setValue(p.warranty)
        self.days.setValue(p.credit_days)
        self.eur.setChecked(p.eur_currency)
        self.credit.setValue(p.credit_amount)
        self.external.setText(p.external)
        self.tracking.setText(p.tracking)
        self.they_pay_we_ship.setChecked(p.they_pay_we_ship)
        self.they_pay_they_ship.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship.setChecked(p.we_pay_we_ship)

    def lines_view_clicked_handler(self):
        self.set_selected_stock_mv() 

    def set_selected_stock_mv(self):
        try:
            i = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            return
        else:
            lines = self.lines_model.actual_lines_from_mixed(i)
     
            from collections import Iterable
            if not isinstance(lines, Iterable) or not lines:
                lines = None
            self.selected_stock_view.setModel(
                ActualLinesFromMixedModel(lines)
            )

    def delete_selected_stock_clicked(self):
        try:
            i = {i.row() for i in self.lines_view.selectedIndexes()}.pop() 
            j = {i.row() for i in self.selected_stock_view.selectedIndexes()}.pop()
        except KeyError: 
            return 
        else:
            self.lines_model.delete(i, j)
            self.set_selected_stock_mv() 
            self.set_stock_mv()
            self.lines_view.clearSelection() 

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
        deleted_lines = self.lines_model.deleted_lines
        added_lines = self.lines_model.added_lines 

        
        if spec == 'Mix':
            spec = None
        
        if condition == 'Mix':
            condition = None
        
        self.stock_model = \
            StockModel(
                warehouse_id, 
                description, 
                condition, spec,
                deleted_lines = deleted_lines, 
                added_lines = added_lines
            ) 
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
        row = self.lines_view.model().rowCount() 
        self.lines_view.model().insertRow(row)
        index = self.lines_view.model().index(row, 0)
        self.lines_view.setCurrentIndex(index)
        self.lines_view.edit(index) 

    def delete_handler(self):
        try:
            row = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            return 
        else:
            self.lines_model.delete(row)
            self.set_stock_mv()
            self.set_selected_stock_mv() 
            self.lines_view.clearSelection() 
    
    def add_handler(self):
        if not hasattr(self, 'stock_model'):return

        requested_stocks = self.stock_model.requested_stocks

        price = self.price.value()
        ignore = self.ignore.isChecked()
        tax = int(self.tax.currentText())
        showing = self.showing_condition.text() or None

        try:
            row = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            row = None

        try:
            self.lines_model.add(
                price, 
                ignore, 
                tax, 
                showing, 
                *requested_stocks, 
                row=row
            )
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            for stock in requested_stocks:
                stock.request = 0
        else:
            self.set_stock_mv() 
            self.set_selected_stock_mv() 
            self.update_total_fields() 


    def save_handler(self):
        if not self._valid_header(): return
        if not self.lines_model:
            QMessageBox.critical(self, 'Error', 'Cant save empty proforma')
            return 
        self._form_to_proforma() 
        try:
            self.save_template() 
            db.session.commit() 
        except:
            raise 
        else:
            QMessageBox.information(self, 'Success', 'Sale saved successfully')
            self.close() 

    def save_template(self):
        self.model.add(self.proforma) 

    def closeEvent(self, event):
        models.refresh() 
        self.parent.set_mv('proformas_sales_')

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

    def _form_to_proforma(self):

        self.proforma.type = int(self.type.currentText())
        self.proforma.number = int(self.number.text())
        self.proforma.date = parse_date(self.date.text())
        self.proforma.warranty = self.warranty.value()
        self.proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        self.proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked() 
        self.proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked() 
        self.proforma.agent_id = models.agent_id_map[self.agent.currentText()]
        self.proforma.partner_id = models.partner_id_map[self.partner.text()]
        self.proforma.warehouse_id = models.warehouse_id_map[self.warehouse.currentText()]
        self.proforma.courier_id = models.courier_id_map[self.courier.currentText()]
        self.proforma.eur_currency = self.eur.isChecked()
        self.proforma.credit_amount = self.credit.value()
        self.proforma.credit_days = self.days.value() 
        self.proforma.incoterm = self.incoterms.currentText() 
        self.proforma.external = self.external.text() 
        self.proforma.tracking = self.tracking.text() 
        self.proforma.note = self.note.toPlainText()[0:255]

    def clear_filters(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear()


class EditableForm(Form):
    
    def __init__(self, parent, view, proforma):
        self.proforma = proforma
        super().__init__(parent, view)

    def init_template(self):
        self.proforma_to_form() 
        self.disable_warehouse() 

    def save_template(self):
        self.model.updateWarehouse(self.proforma) 
    

    def disable_warehouse(self):
        try:
            if sum(
                1 for line in self.proforma.expedition.lines
                for serie in line.series
            ): self.warehouse.setEnabled(False) 
        except AttributeError:
            pass 

def get_form(parent, view, proforma=None):
    return EditableForm(parent, view, proforma) \
        if proforma else Form(parent, view)

