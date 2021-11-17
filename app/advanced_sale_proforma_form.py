

from ui_advanced_sale_proforma_form import Ui_Form

from PyQt5.QtWidgets import QWidget

from decorators import ask_save

from utils import setCommonViewConfig

from sale_proforma_form import Form

from utils import (
    setCommonViewConfig, 
    parse_date, 
    setCompleter,
    agent_id_map, 
    partner_id_map, 
    courier_id_map, 
    descriptions, 
    conditions, 
    specs, 
    warehouse_id_map, 
    build_description, 
    setCompleter, 
    parse_date
)

from models import AdvancedLinesModel, IncomingStockModel

import models 
import db 


from db import Agent, Partner, SaleProformaLine, SaleProforma,\
    SalePayment, func


import utils 


class Form(Ui_Form, QWidget):
    def __init__(self, parent, view):
        from importlib import reload
        global utils
        utils = reload(utils)
        super().__init__()
        self.setupUi(self)
        setCommonViewConfig(self.stock_view) 
        self.model = view.model()
        self.init_template()
        self.parent = parent
        self.lines_model = AdvancedLinesModel(None) 
        self.stock_model = IncomingStockModel(None, description=None, item_id=None, condition=None, spec=None)

        self.lines_view.setModel(self.lines_model)
        self.stock_view.setModel(self.stock_model)

        self.set_combos()
        self.set_completers()
        self.set_handlers() 


    def init_template(self):
        pass 
    
    def set_handlers(self):
        self.partner.returnPressed.connect(self.partner_search)

    def set_combos(self):
        for combo, data in [
            (self.agent, agent_id_map.keys()), 
            (self.warehouse, warehouse_id_map.keys()), 
            (self.courier, courier_id_map.keys())
        ]: combo.addItems(data)

    def set_completers(self):
        for field, data in [
            (self.partner, partner_id_map.keys()), 
            (self.description, descriptions), 
            (self.spec, specs), 
            (self.condition, conditions)
        ]: setCompleter(field, data)


    def search_handler(self):
        pass 

    def delete_handler(self):
        pass 

    def add_handler(self):
        pass 

    def partner_search(self):
        partner_id = partner_id_map.get(self.partner.text())
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

    def insert_handler(self):
        pass 

    def type_changed(self):
        pass 


class EditableForm(Form):
    
    def __init__(self, parent, view, proforma):
        self.proforma = proforma 
        super().__init__(parent, view)


    def init_template(self):
        self.proforma_to_form() 

    def save_template(self):
        pass 

def get_form(parent, view, proforma=None):
    return EditableForm(parent, view, proforma) if proforma \
        else Form(parent, view)
