
from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView

from PyQt5.QtCore import QStringListModel, Qt

from utils import parse_date, build_description

from ui_purchase_proforma_form import Ui_PurchaseProformaForm

from models import PurchaseProformaLineModel, MixedPurchaseLineModel, \
    FullEditableMixedPurchaseLineModel, SemiEditableMixedPurchaseLineModel, \
        FullEditablePurchaseProformaModel, SemiEditablePurchaseProformaModel

import db

from datetime import date

from exceptions import DuplicateLine
 
from db import Partner, PurchaseProformaLine, PurchaseProforma, \
    PurchasePayment, func, Agent


class Form(Ui_PurchaseProformaForm, QWidget):
    
    def __init__(self, parent, view):
        super().__init__() 
        self.setupUi(self)
        self.parent = parent 
        self.model = view.model() 
        self.lines_model = PurchaseProformaLineModel() 
        self.lines_view.setModel(self.lines_model)
        self.title = 'Line - Error'
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.setUp() 

    def setUp(self):

        self.partner_line_edit.setFocus() 

        self.type_combo_box.setCurrentText('1')
        self.number_line_edit.setText(str(self.model.nextNumberOfType(1)).zfill(6))
        self.date_line_edit.setText(date.today().strftime('%d%m%Y'))

        self.partner_name_to_id = {
            partner.fiscal_name:partner.id for partner in db.session.query(db.Partner.id, db.Partner.fiscal_name).\
                where(db.Partner.active == True)
        }        
    
        self.agent_name_to_id = {
            agent.fiscal_name:agent.id for agent in db.session.query(db.Agent.id, db.Agent.fiscal_name).\
                where(db.Agent.active == True)
        }


        self.warehouse_name_to_id = {
            warehouse.description:warehouse.id for warehouse in db.session.query(db.Warehouse.id, db.Warehouse.description)
        }

        self.courier_name_to_id = {
            courier.description:courier.id for courier in db.session.query(db.Courier.id, db.Courier.description)
        }
        
        self.desc_to_item = {str(item):item for item in db.session.query(db.Item)}

        self.mixed_descriptions = self.getMixedDescriptions()

        self.specs = set() 
        for r in db.session.query(PurchaseProformaLine.specification).distinct():
            self.specs.add(r[0])

        self.mixed_specs = self.specs.union({'Mixed'})

        self.conditions = set() 
        for r in db.session.query(PurchaseProformaLine.condition).distinct():
            self.conditions.add(r[0])
        self.mixed_conditions = self.conditions.union({'Mixed'})

        self.agent_combobox.addItems(self.agent_name_to_id.keys())
        self.courier_combobox.addItems(self.courier_name_to_id.keys())
        self.warehouse_combobox.addItems(self.warehouse_name_to_id.keys())

        m = QStringListModel()
        m.setStringList(self.partner_name_to_id.keys())

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.partner_line_edit.setCompleter(c) 

        self.setDescriptionCompleter()
        self.setConditionsCompleter()
        self.setSpecsCompleter() 
       

        def priceOrQuantityChanged(value):
            self.subtotal_spinbox.setValue(self.quantity_spinbox.value() * self.price_spinbox.value())
        
        def subtotalOrTaxChanged(value):
            self.total_spinbox.setValue(self.subtotal_spinbox.value() * (1 + int(self.tax_combobox.currentText())/100))

        def typeChanged(type):
            next_num = self.model.nextNumberOfType(int(type))
            self.number_line_edit.setText(str(next_num))

        self.price_spinbox.valueChanged.connect(priceOrQuantityChanged) 
        self.quantity_spinbox.valueChanged.connect(priceOrQuantityChanged)
        self.tax_combobox.currentIndexChanged.connect(subtotalOrTaxChanged)
        self.subtotal_spinbox.valueChanged.connect(subtotalOrTaxChanged)
        self.type_combo_box.currentTextChanged.connect(typeChanged)

        self.partner_line_edit.returnPressed.connect(self.partnerSearch)
        self.addButton.clicked.connect(self.addHandler)
        self.deleteButton.clicked.connect(self.deleteHandler)
        self.save_button.clicked.connect(self.saveHandler) 
        self.mixed.toggled.connect(self.mixedToggled) 

    def mixedToggled(self, on):
        self.setDescriptionCompleter(on)
        self.setSpecsCompleter(on)
        self.setConditionsCompleter(on)
        self.switchAddHanlder(on)
        if on:
            self.lines_model = MixedPurchaseLineModel()
            self.lines_view.setModel(self.lines_model)
        else:
            self.lines_model = PurchaseProformaLineModel() 
            self.lines_view.setModel(self.lines_model)

    def _mixedValidLine(self):
        
        if self.description_line_edit.text() not in self.mixed_descriptions:
            QMessageBox.critical(self, self.title, 'That mixed description does not exist')
            return False

        if self.condition_line_edit.text() not in self.mixed_conditions:
            QMessageBox.critical(self, self.title, 'That condition does not exist')
            return False
        
        if self.spec_line_edit.text() not in self.mixed_specs:
            QMessageBox.critical(self, self.title, 'That spec does not exist')
            return False

        try:
            1 / self.price_spinbox.value()
        except ZeroDivisionError:
            QMessageBox.critical(self, self.title, 'Price must be > 0')
            return False

        return True 


    def addMixedHandler(self):
        if not self._mixedValidLine():
            return
        try:
            self.lines_model.add(self.description_line_edit.text(), \
                self.condition_line_edit.text(), self.spec_line_edit.text(),\
                    self.quantity_spinbox.value(), self.price_spinbox.value(), \
                    int(self.tax_combobox.currentText()))
            
            self._updateTotals() 
        except DuplicateLine:
            QMessageBox.critical(self, self.title, 'Duplicate Line')
            return
        else:
            self._clearLineFields() 
        

    def switchAddHanlder(self, mixed):
        if mixed:
            self.addButton.clicked.disconnect(self.addHandler)
            self.addButton.clicked.connect(self.addMixedHandler) 
        else:
            self.addButton.clicked.disconnect(self.addMixedHandler)
            self.addButton.clicked.connect(self.addHandler) 


    def setConditionsCompleter(self, mixed=False):
        m = QStringListModel()
        conditions = self.mixed_conditions if mixed else self.conditions
        m.setStringList(conditions)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.condition_line_edit.setCompleter(c) 


    def setSpecsCompleter(self, mixed=False):
        m = QStringListModel()
        specs = self.mixed_specs if mixed else self.specs
        m.setStringList(specs)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.spec_line_edit.setCompleter(c) 


    def setDescriptionCompleter(self, mixed=False):
        m = QStringListModel()
        descriptions = self.mixed_descriptions if mixed else self.desc_to_item.keys() 
        m.setStringList(descriptions)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.description_line_edit.setCompleter(c) 


    def getMixedDescriptions(self):
        ds = set() 
        for description in self.desc_to_item.keys():
            manufacturer, category, model, *_ = description.split(' ')
            description = ' '.join([manufacturer, category, model, 'Mixed GB', 'Mixed Color'])
            ds.add(description)
        for description in self.desc_to_item.keys():
            index = description.index('GB') + 2 
            description = description[0:index] + ' Mixed Color'
            ds.add(description)
        for description in self.desc_to_item.keys():
            manufacturer, category, model, capacity, gb, color = description.split(' ')
            description = ' '.join([manufacturer, category, model, 'Mixed', gb, color])
            ds.add(description)
        return ds

    def partnerSearch(self):

        partner_id = self.partner_name_to_id.get(self.partner_line_edit.text())
        if not partner_id:
            return
        
        try:
            available_credit, max_credit = self._computeCreditAvailable(partner_id) 
            self.available_credit_spinbox.setValue(float(available_credit))

            def prevent(value): 
                if value > available_credit:
                    self.with_credit_spinbox.setValue(available_credit)

            self.with_credit_spinbox.valueChanged.connect(prevent) 

        except TypeError:
            pass 

        result = db.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,\
            Partner.they_pay_they_ship, Partner.we_pay_they_ship, Partner.we_pay_we_ship,\
                Partner.days_credit_limit).join(Agent).where(Partner.id == partner_id).one() 

        agent, warranty, euro, they_pay_they_ship, we_pay_they_ship, we_pay_we_ship, days = \
            result

        self.agent_combobox.setCurrentText(agent)
        self.warranty_spinbox.setValue(warranty) 
        self.eur_radio_button.setChecked(euro) 
        self.they_pay_they_ship_shipping_radio_button.setChecked(they_pay_they_ship) 
        self.we_pay_they_ship_shipping_radio_button.setChecked(we_pay_they_ship) 
        self.we_pay_we_ship_shipping_radio_button.setChecked(we_pay_we_ship) 

    def closeEvent(self, event):
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
        except:
            pass 

    def _computeCreditAvailable(self, partner_id):
        
        from db import Partner, PurchaseProformaLine, PurchaseProforma, \
            PurchasePayment, func
        
        max_credit = db.session.query(db.Partner.amount_credit_limit).\
             where(db.Partner.id == partner_id).scalar()

        total = db.session.query(func.sum(PurchaseProformaLine.quantity * PurchaseProformaLine.price)).\
            select_from(Partner, PurchaseProforma, PurchaseProformaLine).\
                where(PurchaseProformaLine.proforma_id == PurchaseProforma.id).\
                    where(PurchaseProforma.partner_id == Partner.id).\
                        where(Partner.id == partner_id).scalar() 

        paid = db.session.query(func.sum(PurchasePayment.amount)).select_from(Partner, \
            PurchaseProforma, PurchasePayment).where(PurchaseProforma.partner_id == Partner.id).\
                where(PurchasePayment.proforma_id == PurchaseProforma.id).\
                    where(Partner.id == partner_id).scalar() 
        if total and paid:
            return max_credit + paid - total, max_credit 
    

    def _validHeader(self):
        try:
            self.partner_name_to_id[self.partner_line_edit.text()]
        except KeyError:
            QMessageBox.critical(self, 'Update - Error', 'Invalid Partner')
            return False

        try:
            parse_date(self.date_line_edit.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in date field. Format: ddmmyyyy')
            return False
        try:
            parse_date(self.eta_line_edit.text())
        except ValueError:
            QMessageBox.critical(self, 'Update - Error', 'Error in eta field. Format : ddmmyyyy')
            return False

        if self.with_credit_spinbox.value() > self.available_credit_spinbox.value():
            QMessageBox.critical(self, 'Erro - Update', 'Credit must be < than avaliable credit')
            return False
        return True

    def _validLine(self):
        try:
            self.desc_to_item[self.description_line_edit.text()]
        except KeyError:
            QMessageBox.critical(self, self.title, 'That item does not exist')
            return False
        
        if not self.spec_line_edit.text():
            QMessageBox.critical(self, self.title, 'Specification cannot be empty')
            return False

        if not self.condition_line_edit.text():
            QMessageBox.critical(self, self.title, 'Conditions cannot be empty')
            return False

        try:
            1 / self.price_spinbox.value()
        except ZeroDivisionError: 
            QMessageBox.critical(self, self.title, 'Price must be > 0')
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
        proforma.date = self._dateFromString(self.date_line_edit.text())
        proforma.warranty = self.warranty_spinbox.value()
        proforma.eta = self._dateFromString(self.eta_line_edit.text())
        proforma.they_pay_they_ship = self.they_pay_they_ship_shipping_radio_button.isChecked() 
        proforma.we_pay_we_ship = self.we_pay_we_ship_shipping_radio_button.isChecked() 
        proforma.we_pay_they_ship = self.we_pay_they_ship_shipping_radio_button.isChecked() 
        proforma.partner_id = self.partner_name_to_id[self.partner_line_edit.text()]
        proforma.agent_id = self.agent_name_to_id[self.agent_combobox.currentText()]
        proforma.warehouse_id = self.warehouse_name_to_id[self.warehouse_combobox.currentText()]
        proforma.courier_id = self.courier_name_to_id[self.courier_combobox.currentText()]
        proforma.eur_currency = self.eur_radio_button.isChecked()
        proforma.credit_amount = self.with_credit_spinbox.value()
        proforma.credit_days = self.days_credit_spinbox.value()
        proforma.incoterm = self.incoterms_combo_box.currentText()
        proforma.external = self.external_line_edit.text() 
        proforma.tracking = self.tracking_line_edit.text() 
        proforma.note = self.note.toPlainText()[0:255]
        proforma.mixed = self.mixed.isChecked()
        return proforma

    def addHandler(self):

        if not self._validLine():
            return 
        try:
            self.lines_model.add(self.desc_to_item[self.description_line_edit.text()], \
                self.condition_line_edit.text(), self.spec_line_edit.text(), self.quantity_spinbox.value(),\
                    self.price_spinbox.value(), int(self.tax_combobox.currentText()))
            self._updateTotals() 

        except DuplicateLine:
            QMessageBox.critical(self, self.title, 'Duplicate Line')
            return 
        self._clearLineFields()

    def deleteHandler(self):
        indexes = self.lines_view.selectedIndexes() 
        try:
            self.lines_model.delete(indexes)
        except:
            raise 

    def saveHandler(self):
        if not self._validHeader():
            return 
        if not self.lines_model.lines:
            QMessageBox.critical(self, 'Error - Update', 'Empty Proforma')
            return 
        proforma = self._formToProforma() 
        try:
            self.model.add(proforma) 
            self.lines_model.save(proforma) 
        except:
            raise 
        else:
            QMessageBox.information(self, 'Information',\
                'Purchase saved successfully')
            self.close() 


# Estoy hasta los huevos me voy a hinchar a poner ifs y a repetir codigo mas de lo ya 
# hecho y a tomar por culo . 
class EditableForm(Form):
    
    def __init__(self, parent, proforma:db.PurchaseProforma):
        super(QWidget, Form).__init__(self) 
        self.setupUi(self)
        self.parent = parent
        self.proforma = proforma 
        self.mixed.setChecked(proforma.mixed) 
        self.mixed.setEnabled(False) 
        self.type_combo_box.setEnabled(False) 
        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        self.title = 'Line - Error'

        if proforma.mixed and proforma.order is not None:
            self.lines_model = SemiEditableMixedPurchaseLineModel(proforma)
        elif proforma.mixed and proforma.order is None:
            self.lines_model = FullEditableMixedPurchaseLineModel(proforma)
        elif not proforma.mixed and proforma.order is not None:
            self.lines_model = SemiEditablePurchaseProformaModel(proforma)
        elif not proforma.mixed and proforma.order is None:
            self.lines_model = FullEditablePurchaseProformaModel(proforma) 

        self.lines_view.setModel(self.lines_model) 
        self.deleteButton.clicked.connect(self.deleteHandler)
        self.addButton.clicked.connect(self.addHandler)
        self.partner_line_edit.returnPressed.connect(self.partnerSearch)

        self.setUp()

    def partnerSearch(self):
        super().partnerSearch() 

    def setUp(self):

        self.partner_name_to_id = {
            partner.fiscal_name:partner.id for partner in db.session.query(db.Partner.id, db.Partner.fiscal_name).\
                where(db.Partner.active == True)
        }        

        self.agent_name_to_id = {
            agent.fiscal_name:agent.id for agent in db.session.query(db.Agent.id, db.Agent.fiscal_name).\
                where(db.Agent.active == True)
        }


        self.warehouse_name_to_id = {
            warehouse.description:warehouse.id for warehouse in db.session.query(db.Warehouse.id, db.Warehouse.description)
        }

        self.courier_name_to_id = {
            courier.description:courier.id for courier in db.session.query(db.Courier.id, db.Courier.description)
        }
        

        self.desc_to_item = {str(item):item for item in db.session.query(db.Item)}

        self.mixed_descriptions = super().getMixedDescriptions()

        self.specs = set() 
        for r in db.session.query(PurchaseProformaLine.specification).distinct():
            self.specs.add(r[0])

        self.mixed_specs = self.specs.union({'Mixed'})

        self.conditions = set() 
        for r in db.session.query(PurchaseProformaLine.condition).distinct():
            self.conditions.add(r[0])
        self.mixed_conditions = self.conditions.union({'Mixed'})

        super().setConditionsCompleter(mixed=self.proforma.mixed)
        super().setDescriptionCompleter(mixed=self.proforma.mixed)
        super().setSpecsCompleter(mixed=self.proforma.mixed)


        m = QStringListModel()
        m.setStringList(self.partner_name_to_id.keys())

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.partner_line_edit.setCompleter(c) 

        def priceOrQuantityChanged(value):
            self.subtotal_spinbox.setValue(self.quantity_spinbox.value() * self.price_spinbox.value())
        
        def subtotalOrTaxChanged(value):
            self.total_spinbox.setValue(self.subtotal_spinbox.value() * (1 + int(self.tax_combobox.currentText())/100))

        self.price_spinbox.valueChanged.connect(priceOrQuantityChanged) 
        self.quantity_spinbox.valueChanged.connect(priceOrQuantityChanged)
        self.tax_combobox.currentIndexChanged.connect(subtotalOrTaxChanged)
        self.subtotal_spinbox.valueChanged.connect(subtotalOrTaxChanged)

        self.populate_combos()
        self.proforma_to_form()        


    def populate_combos(self):
        self.warehouse_combobox.addItems(r[0] for r in \
            db.session.query(db.Warehouse.description))
        self.courier_combobox.addItems(r[0] for r in \
            db.session.query(db.Courier.description))
        self.agent_combobox.addItems(r[0] for r in \
            db.session.query(db.Agent.fiscal_name).\
                where(db.Agent.active == True))

    def proforma_to_form(self):
        p = self.proforma
        self.mixed.setChecked(p.mixed)
        self.type_combo_box.setCurrentText(str(p.type))
        self.number_line_edit.setText(str(p.number))
        self.date_line_edit.setText(p.date.strftime('%d%m%Y'))
        self.eta_line_edit.setText(p.eta.strftime('%d%m%Y'))
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
        
    
    def addHandler(self):
        super().addHandler() 

    def deleteHandler(self):
        indexes = self.lines_view.selectedIndexes() 
        if not indexes:
            return
        try:
            self.lines_model.delete(indexes)
        except: raise 

    def save(self):
        pass 