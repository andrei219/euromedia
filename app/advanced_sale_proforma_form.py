
from datetime import date 

from ui_advanced_sale_proforma_form import Ui_Form

from PyQt5.QtWidgets import QWidget, QMessageBox

from decorators import ask_save

from utils import setCommonViewConfig

from sale_proforma_form import Form


from models import (
    AdvancedLinesModel, 
    IncomingStockModel, 
    computeCreditAvailable
) 


from db import Agent, Partner, SaleProformaLine, SaleProforma,\
    SalePayment, func


import utils, db

def reload_utils():
    global utils
    from importlib import reload
    utils = reload(utils) 

class Form(Ui_Form, QWidget):
    def __init__(self, parent, view):
        reload_utils()
        super().__init__()
        self.setupUi(self)
        setCommonViewConfig(self.stock_view) 
        self.model = view.model()
        self.init_template()
        self.parent = parent
        self.lines_model = AdvancedLinesModel(self.proforma) 
        self.lines_view.setModel(self.lines_model)
        self.set_combos()
        self.set_completers()
        self.set_handlers() 


    def init_template(self):
        self.proforma = db.SaleProforma() 
        db.session.add(self.proforma)
        db.session.flush() 
        self.date.setText(date.today().strftime('%d%m%Y'))
        self.type.setCurrentText('1')
        self.number.setText(str(self.model.nextNumberOfType(1)).zfill(6))
    
    def set_handlers(self):
        self.partner.returnPressed.connect(self.partner_search)
        self.delete_.clicked.connect(self.delete_handler)
        self.add.clicked.connect(self.add_handler) 
        self.save.clicked.connect(self.save_handler)
        self.insert.clicked.connect(self.insert_handler) 
        self.type.currentTextChanged.connect(self.type_changed)
        self.search.clicked.connect(self.search_handler) 
        self.warehouse.currentTextChanged.connect(self.warehouse_handler) 


    def set_combos(self):
        for combo, data in [
            (self.agent, utils.agent_id_map.keys()), 
            (self.warehouse, utils.warehouse_id_map.keys()), 
            (self.courier, utils.courier_id_map.keys())
        ]: combo.addItems(data)

    def set_completers(self):
        for field, data in [
            (self.partner, utils.partner_id_map.keys()), 
            (self.description, utils.descriptions), 
            (self.spec, utils.specs), 
            (self.condition, utils.conditions)
        ]: utils.setCompleter(field, data)


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

        self.stock_model = IncomingStockModel(
            warehouse_id, 
            description=description,
            condition = condition, 
            spec = spec, 
        )

        self.stock_view.setModel(self.stock_model) 

    def filters_unset(self):
        return any((
            self.description.text() not in utils.descriptions, 
            self.spec.text() not in utils.specs, 
            self.condition.text() not in utils.conditions
        )) 

    def search_handler(self):
        if self.filters_unset():
            QMessageBox.critical(self, 'Error - Search', 'Set filters.')
            return 
        self.set_stock_mv()

    def warehouse_handler(self):
        if hasattr(self, 'stock_model'):
            self.stock_model.reset()

        if hasattr(self, 'lines_model'):
            self.lines_model.reset()   

        self.update_totals() 
        # removing objects in pending state 
        db.session.rollback() 
    
    def update_totals(self):
        
        self.subtotal.setText(str(self.lines_model.subtotal))
        self.sale_tax.setText(str(self.lines_model.tax))
        self.total.setText(str(self.lines_model.total))

    def delete_handler(self):
        indexes = self.lines_view.selectedIndexes()
        if not indexes:return 
        row = {index.row() for index in indexes}.pop()
        self.lines_model.delete(row)
        self.lines_view.clearSelection() 

        self.set_stock_mv()
        self.update_totals() 

    def add_handler(self):
        if not hasattr(self, 'stock_model'):return 
        indexes = self.stock_view.selectedIndexes()
        if not indexes: return 
        row = {i.row() for i in indexes}.pop()
        vector = self.stock_model[row]

        quantity = self.quantity.value() 
        if quantity > vector.available:
            QMessageBox.critical(
                self, 
                'Error', 
                'quantity must be less than available'
            )
            return 

        price = self.price.value()
        ignore = self.ignore.isChecked()
        tax = int(self.tax.currentText())
        showing = self.showing_condition.text() 
        
        try:
            self.lines_model.add(quantity, price, ignore, tax, showing, vector)
        except ValueError as ex:
            raise 
            QMessageBox.critical(self, 'Error', str(ex))
        else:
            self.update_totals()
            self.set_stock_mv()

    def partner_search(self):
        partner_id = utils.partner_id_map.get(self.partner.text())
        if not partner_id:
            return
        try:
            available_credit = computeCreditAvailable(partner_id) 
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

    def type_changed(self, type):
        next_num = self.model.nextNumberOfType(int(type))
        self.number.setText(str(next_num).zfill(6))

    def save_handler(self):
        if not self._valid_header(): return
        if not self.lines_model:
            QMessageBox.critical(self, 'Error', "Can't process empty proforma")
            return 

        warehouse_id = utils.warehouse_id_map.get(self.warehouse.currentText())
        lines = self.lines_model.lines 
        
        if hasattr(self, 'stock_model'):
            if self.stock_model.lines_against_stock(warehouse_id, lines):
                QMessageBox.critical(
                    self, 
                    'Error', 
                    'Someone took those incoming stocks. Start again.'
                )
                self.close() 
                return   

        self._form_to_proforma() 
        try:
            self.save_template()
            db.session.commit()

        except:
            raise 
            db.session.rollback() 
        else:
            QMessageBox.information(self, 'Success', 'Sale saved successfully')
        
        self.close() 

    def save_template(self):
        self.model.add(self.proforma) 
        self.proforma.advanced_lines.extend(self.lines_model.lines)

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


    def closeEvent(self, event):
        db.session.rollback() 

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
        self.description.clear()
        self.spec.clear()
        self.condition.clear()


class EditableForm(Form):
    
    def __init__(self, parent, view, proforma):
        reload_utils()
        self.proforma = proforma 
        super().__init__(parent, view)
        self.update_totals() 


    def init_template(self):
        self.proforma_to_form() 
        self.warehouse.setEnabled(False)
        self.disable_if_cancelled()


    def save_template(self):
        for o in db.session:
            if type(o) == db.AdvancedLine:
                print(o)

    
    def disable_if_cancelled(self):
        if self.proforma.cancelled:
            self.delete_.setEnabled(False)
            self.header.setEnabled(False)
            self.create_line.setEnabled(False)
            self.search.setEnabled(False)
            self.insert.setEnabled(False)
            self.add.setEnabled(False)
            self.save.setEnabled(False)      





def get_form(parent, view, proforma=None):
    return EditableForm(parent, view, proforma) if proforma \
        else Form(parent, view)
