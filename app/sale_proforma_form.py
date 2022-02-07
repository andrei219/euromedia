
from datetime import date

from PyQt5.QtCore import QAbstractTableModel, QStringListModel, Qt
from PyQt5.QtWidgets import QCompleter, QMessageBox, QTableView, QWidget

import db
import decorators
import models
import utils
from db import (Agent, Partner, SalePayment, SaleProforma, SaleProformaLine,
                func)
from models import ActualLinesFromMixedModel, SaleProformaLineModel, StockModel
from ui_sale_proforma_form import Ui_SalesProformaForm


class StockBase:

    def __init__(self, filters, warehouse_id, form):
        self.filters = filters
        self.warehouse_id = warehouse_id 
        self.stocks = StockModel.stocks(warehouse_id=warehouse_id) 
        self.completer = Completer(self, form) 

        self._set_state()
        self.completer.update() 

    def update(self): 
        print('SockBase.update', self.filters.description, self.filters.condition, self.filters.spec)
        self.stocks = StockModel.stocks(
            warehouse_id = self.warehouse_id, 
            description  = self.filters.description, 
            condition    = self.filters.condition, 
            spec         = self.filters.spec 
        )

        self._set_state()        
        self.completer.update()

    
    def _set_state(self):
        self._item_ids = {s.item_id for s in self.stocks}
        self._conditions = {s.condition for s in self.stocks}
        self._specs = {s.spec for s in self.stocks}
        self._descriptions = utils.compute_available_descriptions(self._item_ids)

    @property
    def item_ids(self):
        return self._item_ids

    @property
    def conditions(self):
        return self._conditions

    @property
    def specs(self):
        return self._specs

    @property
    def descriptions(self):
        return self._descriptions

class Filters:

    def __init__(self, warehouse_id, form):
        self._description = None
        self._condition = None
        self._spec = None
        self._stock_base = StockBase(self, warehouse_id, form)

    @property
    def description(self):
        return self._description
    
    @property
    def condition(self):
        return self._condition

    @property
    def spec(self):
        return self._spec 
    
    @description.setter
    def description(self, description):
        self._description = description
    
    @condition.setter
    def condition(self, condition):
        self._condition = condition

    @spec.setter 
    def spec(self, spec):
        self._spec = spec

    @property
    def stock_base(self):
        return self._stock_base

    def set(self, description, condition, spec):
        self._description = description
        self._condition = condition
        self._spec = spec 
        print('Filters.set:', description, condition, spec)

        self.stock_base.update()


class Completer:

    def __init__(self, stock_base, form):
        self.stock_base = stock_base
        self.form = form
    
    def update(self):
    
        utils.setComboCompleter(
            self.form.spec, 
            self.stock_base.specs.union({''})) 
    
        utils.setComboCompleter(
            self.form.description, 
            utils.compute_available_descriptions(self.stock_base.item_ids).union({''})
        )
    
        utils.setComboCompleter(
            self.form.condition,
            self.stock_base.conditions.union({''}) 
        )


class Form(Ui_SalesProformaForm, QWidget):

    def __init__(self, parent, view):
        from importlib import reload
        global utils
        utils = reload(utils)
        super().__init__() 
        self.setupUi(self) 
        self.setCombos()

        
        self.model = view.model() 
        self.init_template() 
        self.parent = parent
        self.lines_model = SaleProformaLineModel(self.proforma, self)
        self.lines_view.setModel(self.lines_model)
        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        utils.setCommonViewConfig(self.selected_stock_view)
        
        self.set_partner_completer()
        self.set_handlers()

        warehouse_id = utils.warehouse_id_map[self.warehouse.currentText()]

        self.filters = Filters(warehouse_id, self)
        

    def init_template(self):
        self.proforma = db.SaleProforma() 

        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        self.proforma.warehouse_id = warehouse_id 

        db.session.add(self.proforma)
        db.session.flush() 
 
        self.date.setText(date.today().strftime('%d%m%Y'))
        self.type.setCurrentText('1')
        self.number.setText(str(self.model.nextNumberOfType(1)).zfill(6))

    def set_handlers(self):
        self.search.clicked.connect(self.search_handler) 
        self.lines_view.clicked.connect(self.lines_view_clicked_handler)
        self.delete_button.clicked.connect(self.delete_handler)
        self.add.clicked.connect(self.add_handler) 
        self.save.clicked.connect(self.save_handler)
        self.partner.textChanged.connect(self.partner_search)
        self.apply.clicked.connect(self.apply_handler)
        self.remove.clicked.connect(self.remove_handler) 
        self.insert.clicked.connect(self.insert_handler) 
        self.type.currentTextChanged.connect(self.typeChanged)
        self.delete_selected_stock.clicked.connect(self.delete_selected_stock_clicked)
        self.deselect.clicked.connect(lambda : self.lines_view.clearSelection())
        self.warehouse.currentTextChanged.connect(self.warehouse_changed)
        
        self.description.returnPressed.connect(self.description_return_pressed)
        self.condition.returnPressed.connect(self.condition_return_pressed)
        self.spec.returnPressed.connect(self.spec_return_pressed)


    def warehouse_changed(self, text):
        # warehouse_id = utils.warehouse_id_map.get(text)
        # db.session.rollback() 
        # self.proforma = SaleProforma() 
        # self.proforma.warehouse_id = warehouse_id 
        # self.lines_model = SaleProformaLineModel(self.proforma) 
        # self.lines_view.setModel(self.lines_model)

        # if hasattr(self, 'stock_model'):
        #     self.stock_model.reset() 

        # self.stock_view.setModel(self.stock_model) 
        # db.session.add(self.proforma) 

        if hasattr(self, 'stock_model'):
            self.stock_model.reset()

        if hasattr(self, 'lines_model'):
            self.lines_model.reset()   

        warehouse_id = utils.warehouse_id_map.get(
            self.warehouse.currentText()
        )

        self.filters = Filters(warehouse_id, self)

        self.update_totals() 
        
        # removing objects in pending state 
        db.session.rollback() 

    def description_return_pressed(self):
        description = self.description.text() 
        stock_base = self.filters.stock_base 
        if description not in stock_base.descriptions or description == '':
            return 
        
        condition, spec = self.condition.text(), self.spec.text()
        if condition == '' or condition not in stock_base.conditions:
            condition = None
        
        if spec == '' or spec not in stock_base.specs:
            spec = None 

        self.filters.set(description, condition, spec)
        
        self.description.setCurrentText(description)
        
        if condition is not None:
            self.condition.setCurrentText(condition)

        if spec is not None:
            self.spec.setCurrentText(spec)

        for stock in self.filters.stock_base.stocks:
            print(stock)

    def condition_return_pressed(self):
        condition = self.condition.text()
        stock_base = self.filters.stock_base
        if condition not in stock_base.conditions or condition == '':
            return
        
        description ,spec = self.description.text(), self.spec.text()
        if description =='' or description not in stock_base.descriptions:
            description=None
        
        if spec == '' or spec not in stock_base.specs:
            spec = None
        
        self.filters.set(description, condition, spec)
        
        self.condition.setCurrentText(condition)

        if spec is not None:
            self.spec.setCurrentText(spec)
        
        if description is not None:
            self.description.setCurrentText(description)

    def spec_return_pressed(self):  

        spec = self.spec.text()
        stock_base = self.filters.stock_base 

        if spec not in stock_base.specs or spec == '':
            return
        
        description, condition = self.description.text(), self.condition.text()
        
        if description == '' or description not in stock_base.descriptions:
            description = None
        
        if condition == '' or condition not in stock_base.conditions:
            condition = None 
        
        self.filters.set(description, condition, spec)

        self.spec.setCurrentText(spec)
        if description is not None:
            self.description.setCurrentText(description)

        if condition is not None:
            self.condition.setCurrentText(condition)

        for stock in stock_base.stocks:
            print(stock)


    def typeChanged(self, type):
        next_num = self.model.nextNumberOfType(int(type))
        self.number.setText(str(next_num).zfill(6))

    def setCombos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()), 
            (self.warehouse, utils.warehouse_id_map.keys()), 
            (self.courier, utils.courier_id_map.keys())
        ]: combo.addItems(data)

    def set_partner_completer(self):
        utils.setCompleter(self.partner, utils.partner_id_map.keys())


    def partner_search(self):
        partner = self.partner.text()
        if partner in utils.partner_id_map.keys():
            partner_id = utils.partner_id_map.get(partner)
            if not partner_id:
                return
            try:
                available_credit = models.computeCreditAvailable(partner_id) 
                self.available_credit.setValue(float(available_credit))
                self.credit.setMaximum(0.0 if available_credit < 0 else available_credit)

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
            self.usd.setChecked(not euro)
            self.they_pay_they_ship.setChecked(they_pay_they_ship) 
            self.they_pay_we_ship.setChecked(they_pay_we_ship) 
            self.we_pay_we_ship.setChecked(we_pay_we_ship) 


    def proforma_to_form(self):
        p = self.proforma

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
        except KeyError:
            QMessageBox.critical(self, 'Error', 'No line selected')
            return 
        try:
            j = {i.row() for i in self.selected_stock_view.selectedIndexes()}.pop()
        except KeyError:
            QMessageBox.critical(self, 'Error', 'No stock from line stock selected')
            return
        
        try:
            self.lines_model.delete(i, j)
            self.set_selected_stock_mv() 
            self.set_stock_mv()
            self.lines_view.clearSelection() 
        except:
            QMessageBox.critical(self, 'Error', 'Error reaching database')
            raise 

    def search_handler(self):
        self.set_stock_mv()
        self.clear_filters()
        self.filters.set(None, None, None)

    def set_stock_mv(self):
        warehouse_id = utils.warehouse_id_map.get(
            self.warehouse.currentText()
        )
        description = self.description.text()
        condition = self.condition.text()
        spec = self.spec.text() 
        
        if spec == 'Mix':
            spec = None
        
        if condition == 'Mix':
            condition = None
        
        self.stock_model = \
            StockModel(
                warehouse_id, 
                description, 
                condition, spec,
            ) 
        self.stock_view.setModel(self.stock_model) 
        self.stock_view.resizeColumnsToContents() 

    def filters_unset(self):
        return any((
            self.description.text() not in self.filters.stock_base.descriptions, 
            self.condition.text() not in self.filters.stock_base.conditions, 
            self.spec.text() not in self.filters.stock_base.specs
        ))


    def apply_handler(self):
        pass 

    def remove_handler(self):
        pass 

    def insert_handler(self):
        from free_line_form import Dialog
        dialog = Dialog(self)
        if dialog.exec_():
            try:
                description = dialog.description.text()
                if not description:
                    return 

                self.lines_model.insert_free(
                    description,
                    dialog.quantity.value(),
                    dialog.price.value() ,
                    int(dialog.tax.currentText())
                )
            except:
                raise 
                QMessageBox.critical(
                    self, 
                    'Error', 
                    'Error adding free line'
                )


    def delete_handler(self):
        try:
            row = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            QMessageBox.critical(self, 'Error', 'No line selected')
        else:
            self.lines_model.delete(row)
            self.set_stock_mv()
            self.set_selected_stock_mv() 
            self.lines_view.clearSelection() 
            self.update_totals() 
    
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
            self.update_totals() 
            self.clear_filters()
            self.filters.set(None, None, None)

    def save_handler(self):
        if not self._valid_header(): return
        # if not self.lines_model:
        #     QMessageBox.critical(self, 'Error', "Can't process empty proforma")
        #     return 

        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        lines = self.lines_model.lines 
        if hasattr(self, 'stock_model'):
            if self.stock_model.lines_against_stock(warehouse_id, lines):
                QMessageBox.critical(
                    self, 
                    'Error', 
                    'Someone took those stocks. Start again.'
                )
                self.close() 
                return 

        self._form_to_proforma() 
        try:
            self.save_template()
            db.session.commit()
            # self.parent.set_mv('proformas_sales_')
        except:
            raise 
            db.session.rollback() 
        else:
            QMessageBox.information(self, 'Success', 'Sale saved successfully')
        
        self.close() 

    def save_template(self):
        self.model.add(self.proforma) 

    def closeEvent(self, event):
        db.session.rollback()     
        # self.parent.set_mv('proformas_sales_')

    def update_totals(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

    def _valid_header(self):
        try:
            utils.partner_id_map[self.partner.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False
        try:
            utils.parse_date(self.date.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False
        return True

    def _form_to_proforma(self):

        self.proforma.type = int(self.type.currentText())
        self.proforma.number = int(self.number.text())
        self.proforma.date = utils.parse_date(self.date.text())
        self.proforma.warranty = self.warranty.value()
        self.proforma.they_pay_they_ship = self.they_pay_they_ship.isChecked()
        self.proforma.they_pay_we_ship = self.they_pay_we_ship.isChecked() 
        self.proforma.we_pay_we_ship = self.we_pay_we_ship.isChecked() 
        self.proforma.agent_id = utils.agent_id_map[self.agent.currentText()]
        self.proforma.partner_id = utils.partner_id_map[self.partner.text()]
        self.proforma.warehouse_id = utils.warehouse_id_map[self.warehouse.currentText()]
        self.proforma.courier_id = utils.courier_id_map[self.courier.currentText()]
        self.proforma.eur_currency = self.eur.isChecked()
        self.proforma.credit_amount = self.credit.value()
        self.proforma.credit_days = self.days.value() 
        self.proforma.incoterm = self.incoterms.currentText() 
        self.proforma.external = self.external.text() 
        self.proforma.tracking = self.tracking.text() 
        self.proforma.note = self.note.toPlainText()[0:255]

    def clear_filters(self):
        self.description.setCurrentText('')
        self.spec.setCurrentText('')
        self.condition.setCurrentText('')

class EditableForm(Form):
    
    def __init__(self, parent, view, proforma):
        self.proforma = proforma
        super().__init__(parent, view)
        self.update_totals() 

    def init_template(self): 
        self.proforma_to_form() 
        self.disable_warehouse() 
    
    def save_template(self):
        self.model.updateWarehouse(self.proforma)

    def disable_warehouse(self):
        # try:
        #     if sum(
        #         1 for line in self.proforma.expedition.lines
        #         for serie in line.series
        #     ): self.warehouse.setEnabled(False) 
        # except AttributeError:
        #     pass 

        self.warehouse.setEnabled(False)

def get_form(parent, view, proforma=None):
    return EditableForm(parent, view, proforma) \
        if proforma else Form(parent, view)
