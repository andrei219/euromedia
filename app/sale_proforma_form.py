
from datetime import date

from PyQt5.QtWidgets import QCompleter, QMessageBox, QTableView, QWidget

import db
import models

import utils

from utils import has_certificate

from db import (
    Agent,
    Partner,
)
from models import (
    ActualLinesFromMixedModel,
    SaleProformaLineModel,
    StockModel,
    update_sale_warehouse
)
from ui_sale_proforma_form import Ui_SalesProformaForm

from sqlalchemy.exc import IntegrityError

from utils import get_next_num, parse_date

from bidict import bidict

class StockBase:

    def __init__(self, filters, warehouse_id, form):
        self.filters = filters
        self.warehouse_id = warehouse_id
        self.completer = Completer(self, form)
        self.update()

    def update(self): 
        
        description = self.filters.description
        condition = self.filters.condition
        spec = self.filters.spec

        self.stocks = StockModel.stocks(
            self.warehouse_id, 
            description,
            condition,   
            spec    
        )

        self._set_state()        
        self.completer.update(description, condition, spec)

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

        self.stock_base.update()


class Completer:

    def __init__(self, stock_base, form):
        self.stock_base = stock_base
        self.form = form
    
    def update(self, description, condition, spec):
    
        if spec is None:

            utils.setCompleter(
                self.form.spec, 
                self.stock_base.specs.union({'Mix'})) 

        if description is None:
            utils.setCompleter(
                self.form.description, 
                utils.compute_available_descriptions(self.stock_base.item_ids)
            )
        
        if condition is None:
            utils.setCompleter(
                self.form.condition,
                self.stock_base.conditions.union({'Mix'}) 
            )

from functools import wraps
from typing import Dict, Any, Tuple
def log(func):
    @wraps(func)
    def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        print(func.__name__, args, kwargs)
        # noinspection PyTypeChecker
        return func(*args, **kwargs)
    return wrapper


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

        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.lines_view.setAlternatingRowColors(True)
        self.lines_view.setSelectionMode(QTableView.SingleSelection)

        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        self.stock_view.setSortingEnabled(True)
        self.stock_view.setAlternatingRowColors(True)

        self.selected_stock_view.setSortingEnabled(True)
        self.selected_stock_view.setSelectionBehavior(QTableView.SelectRows)
        self.selected_stock_view.setAlternatingRowColors(True)
        self.selected_stock_view.setSelectionMode(QTableView.SingleSelection)

        self.set_partner_completer()
        self.set_handlers()

        self.view = view
        
        self.lines_view.resizeColumnToContents(0)
        self.lines_view.resizeColumnToContents(2)

        self.address_id_map = None

    def build_address_map_and_init_combo(self, partner_id=None):
        # Populate addresses for partner

        if partner_id is None:
            partner_id = self.proforma.partner_id

        self.shipping_address.clear()
        self.address_id_map = utils.get_address_id_map(partner_id=partner_id)
        self.shipping_address.addItems(self.address_id_map.keys())

        try:
            self.shipping_address.setCurrentText(
                self.address_id_map.inverse[self.proforma.shipping_address_id]
            )
        except KeyError:
            pass

        # Associate the handler after init. Otherwise, conflict.
        self.shipping_address.currentTextChanged.connect(self.shipping_address_changed)

    def adjust_view(self):
        self.view.resizeColumnToContents(2)
        self.view.resizeColumnToContents(3)

    def init_template(self):

        self.proforma = db.SaleProforma() 

        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        self.proforma.warehouse_id = warehouse_id 
        db.session.add(self.proforma)
        db.session.flush() 
 
        self.date.setText(date.today().strftime('%d%m%Y'))
        self.type.setCurrentText('1')

        self.typeChanged(1)
		
        # Only for new form.

        self.warehouse.currentTextChanged.connect(self.warehouse_changed)

        warehouse_id = utils.warehouse_id_map[self.warehouse.currentText()]

        self.filters = Filters(warehouse_id, self)

    def set_handlers(self):
        self.search.clicked.connect(self.search_handler) 
        self.lines_view.clicked.connect(self.lines_view_clicked_handler)
        self.delete_button.clicked.connect(self.delete_handler)
        self.add.clicked.connect(self.add_handler) 
        self.save.clicked.connect(self.save_handler)
        self.partner.returnPressed.connect(self.partner_search)
        self.insert.clicked.connect(self.insert_handler)
        self.type.currentTextChanged.connect(self.typeChanged)
        self.delete_selected_stock.clicked.connect(self.delete_selected_stock_clicked)
        self.deselect.clicked.connect(lambda: self.lines_view.clearSelection())
        self.prop.returnPressed.connect(self.prop_return_pressed)
        self.description.editingFinished.connect(self.description_editing_finished)
        self.condition.editingFinished.connect(self.condition_editing_finished)
        self.spec.editingFinished.connect(self.spec_editing_finished)
        self.sync.clicked.connect(self.sync_wh_handler)

    def sync_wh_handler(self):
        try:
            self.lines_model.sync_with_warehouse()
        except:
            raise

    def prop_return_pressed(self):

        try:
            value = int(self.prop.text())
        except ValueError:
            return 

        rows = {index.row() for index in self.stock_view.selectedIndexes()}
        try:
            total = sum(self.stock_model.stocks[row].quantity for row in rows)
            
            for row in rows:
                index = self.stock_model.index(row, 4)
                perc = self.stock_model.stocks[row].quantity / total
                self.stock_model.setData(index, round(perc*value))

        except AttributeError:
            pass 

    def warehouse_changed(self, text):

        if hasattr(self, 'stock_model'):
            self.stock_model.reset()

        if hasattr(self, 'lines_model'):
            self.lines_model.delete_all()

        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        self.proforma.warehouse_id = warehouse_id
        self.filters = Filters(warehouse_id, self)
        self.update_totals()
        db.session.flush()

        # removing objects in pending state
        # db.session.rollback()

        self.lines_view.clearSelection()

    def description_editing_finished(self):
        description = self.description.text() 
        stock_base = self.filters.stock_base 
        
        condition, spec = self.condition.text(), self.spec.text()
        if condition == '' or condition not in stock_base.conditions:
            condition = None
        
        if spec == '' or spec not in stock_base.specs:
            spec = None 

        self.filters.set(description, condition, spec)

        self.condition.setFocus(True)

    def condition_editing_finished(self):
        condition = self.condition.text()
        stock_base = self.filters.stock_base
        
        description, spec = self.description.text(), self.spec.text()
        
        if not description or description not in stock_base.descriptions:
            description = None
        
        if not spec or spec == 'Mix' or spec not in stock_base.specs:
            spec = None
        
        if not spec or spec == 'Mix' or spec not in stock_base.specs:
            spec = None 

        self.filters.set(description, condition, spec)

        self.spec.setFocus(True)
        
    def spec_editing_finished(self):  
        spec = self.spec.text()
        stock_base = self.filters.stock_base 

        description, condition = self.description.text(), self.condition.text()
        
        if not description or description not in stock_base.descriptions:
            description = None
        
        if not condition or condition == 'Mix' or condition not in stock_base.conditions:
            condition = None

        if not spec or spec == 'Mix' or spec not in stock_base.specs:
            spec = None 
        
        self.filters.set(description, condition, spec)

        self.search.setFocus(True)

    def typeChanged(self, type):
        try:
            parse_date(self.date.text())
        except ValueError:
            return
        else:
            _next = get_next_num(db.SaleProforma, int(type))
            self.number.setText(str(_next).zfill(6))

    def setCombos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()), 
            (self.warehouse, utils.warehouse_id_map.keys()), 
            (self.courier, utils.courier_id_map.keys())
        ]:
            combo.addItems(data)

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
                
            result = db.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,
                Partner.they_pay_they_ship, Partner.they_pay_we_ship, Partner.we_pay_we_ship,
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

            if self.type.currentText() == '2':
                if not has_certificate(partner_id):
                    QMessageBox.information(self, 'Information', 'This partner has no reseller certificate.')

            self.build_address_map_and_init_combo(partner_id=partner_id)

    def shipping_address_changed(self, new_address):
        try:
            self.proforma.shipping_address_id = self.address_id_map[new_address]
        except KeyError:
            pass

    def proforma_to_form(self):
        p = self.proforma

        self.type.setCurrentText(str(p.type))
        self.number.setText(str(p.number))
        self.date.setText(str(p.date.strftime('%d%m%Y')))
        self.external.setText(p.external)
        self.partner.setText(p.partner.trading_name)
        self.agent.setCurrentText(p.agent.fiscal_name)
        self.warehouse.setCurrentText(p.warehouse.description)
        self.courier.setCurrentText(p.courier.description)
        self.incoterms.setCurrentText(p.incoterm)
        self.warranty.setValue(p.warranty)
        self.days.setValue(p.credit_days)
        self.eur.setChecked(p.eur_currency)
        self.credit.setValue(p.credit_amount)
        self.tracking.setText(p.tracking)
        self.they_pay_we_ship.setChecked(p.they_pay_we_ship)
        self.they_pay_they_ship.setChecked(p.they_pay_they_ship)
        self.we_pay_we_ship.setChecked(p.we_pay_we_ship)
        self.note.setText(p.note)
    

    def lines_view_clicked_handler(self, index):
        self.set_selected_stock_mv() 
        self.selected_stock_view.resizeColumnToContents(0)
        price = self.lines_model.get_price(index.row())
        self.price.setValue(price)

    def set_selected_stock_mv(self):
        try:
            i = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            return  
        else:
            lines = self.lines_model.actual_lines_from_mixed(i)
            self.selected_stock_view.setModel(ActualLinesFromMixedModel(lines))
            self.selected_stock_view.resizeColumnsToContents()

    def delete_selected_stock_clicked(self):
        try:
            i = {i.row() for i in self.lines_view.selectedIndexes()}.pop() 
        except KeyError:
            QMessageBox.information(self, 'Information', 'No line selected')
            return 
        try:
            j = {i.row() for i in self.selected_stock_view.selectedIndexes()}.pop()
        except KeyError:
            QMessageBox.information(self, 'Information', 'No stock from line stock selected')
            return
        
        try:
            self.lines_model.delete(i, j)
            self.set_selected_stock_mv() 
            self.set_stock_mv()
            self.lines_view.clearSelection()
            self.update_totals()
        except:
            QMessageBox.information(self, 'Information', 'Error reaching database')
            raise 

    def search_handler(self):
        self.set_stock_mv()
        self.stock_view.setFocus(True)

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
        self.stock_view.resizeColumnToContents(0) 

    def filters_unset(self):
        return any((
            self.description.text() not in self.filters.stock_base.descriptions, 
            self.condition.text() not in self.filters.stock_base.conditions, 
            self.spec.text() not in self.filters.stock_base.specs
        ))

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
                    dialog.price.value(),
                    int(dialog.tax.currentText())
                )
            
            except:
                QMessageBox.critical(self, 'Error', 'Error adding free line')
                raise
            else:
                self.update_totals()
                self.resize_lines_view()

    def delete_handler(self):
        try:
            row = {i.row() for i in self.lines_view.selectedIndexes()}.pop()
        except KeyError:
            QMessageBox.information(self, 'Information', 'No line selected')
        else:
            update = self.lines_model.delete(row)
            if update:
                self.set_stock_mv()
                self.set_selected_stock_mv() 

            self.lines_view.clearSelection()
            self.update_totals()
            self.resize_lines_view()

    def resize_lines_view(self):
        self.lines_view.resizeColumnToContents(0)
        self.lines_view.resizeColumnToContents(2)
        self.stock_view.resizeColumnToContents(3)

    def add_handler(self):
        if not hasattr(self, 'stock_model'):
            return

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
            QMessageBox.information(self, 'Information', str(ex))
            for stock in requested_stocks:
                stock.request = 0
        else:
            # self.stock_model.reset() 
            self.update_totals() 
            # self.clear_filters()
            self.set_stock_mv()
            self.filters.set(None, None, None)

        self.resize_lines_view()
        self.description.setFocus(True)

    def save_handler(self):

        # 1 . restore original __eq__ method
        from db import SaleProformaLine, original_sale_proforma_line_eq
        SaleProformaLine.__eq__ = original_sale_proforma_line_eq

        if not self._valid_header():
            return
        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        if hasattr(self, 'stock_model'):
            
            lines = [
                line
                for line in self.model
                if not utils.is_object_persisted(line)
            ]
            if self.stock_model.lines_against_stock(warehouse_id, lines):
                QMessageBox.critical(
                    self, 
                    'Error', 
                    'These stocks are no longer available'
                )
                return 

        self._form_to_proforma() 
        try:
            self.save_template()
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            QMessageBox.critical(self, 'Error', 'Document with that type and number already exists')
        else:
            QMessageBox.information(self, 'Success', 'Sale saved successfully')
            self.adjust_view()

    def save_template(self):

        if not utils.is_object_persisted(self.proforma):
            self.model.add(self.proforma) 

    def closeEvent(self, event):
        db.session.rollback()

    def update_totals(self):

        self.proforma.lines = self.lines_model.lines

        self.total.setText(str(self.lines_model.total))
        self.ptax.setText(str(self.lines_model.tax))
        self.cn.setText(str(self.proforma.cn_total))
        self.pending.setText(str(self.proforma.owing))
        self.subtotal.setText(str(self.lines_model.subtotal))
        self.quantity_label.setText('Qnt.: ' + str(self.lines_model.quantity))

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
        self.proforma.external = self.external.text()
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
        self.proforma.tracking = self.tracking.text()
        self.proforma.note = self.note.toPlainText()[0:255]

        self.proforma.shipping_address_id = self.address_id_map[self.shipping_address.currentText()]


    def clear_filters(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear()


class EditableForm(Form):
    
    def __init__(self, parent, view, proforma):
        self.proforma = proforma

        super().__init__(parent, view)
        self.build_address_map_and_init_combo()
        self.update_totals()
        self.disable_warehouse()
        self.proforma_to_form()


    def init_template(self): 
        self.filters = Filters(self.proforma.warehouse_id, self)

    def save_template(self):
        update_sale_warehouse(self.proforma)

    def disable_warehouse(self):
        self.warehouse.setEnabled(False)


def get_form(parent, view, proforma=None):
    return EditableForm(parent, view, proforma ) \
        if proforma else Form(parent, view)
