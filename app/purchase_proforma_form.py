
from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView

from PyQt5.QtCore import QStringListModel, Qt

from utils import parse_date, build_description

from ui_purchase_proforma_form import Ui_PurchaseProformaForm

from models import PurchaseProformaLineModel

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
        self.session = view.model().session 
        self.lines_model = PurchaseProformaLineModel(self.session) 
        self.lines_view.setModel(self.lines_model)
        self.title = 'Line - Error'
        self.setUp() 

    def setUp(self):

        self.lines_view.setSelectionBehavior(QTableView.SelectRows) 

        self.partner_line_edit.setFocus() 

        self.type_combo_box.setCurrentText('1')
        self.number_line_edit.setText(str(self.model.nextNumberOfType(1)).zfill(6))
        self.date_line_edit.setText(date.today().strftime('%d%m%Y'))

        self.partner_name_to_id = {
            partner.fiscal_name:partner.id for partner in self.session.query(db.Partner.id, db.Partner.fiscal_name).\
                where(db.Partner.active == True)
        }        
    
        self.agent_name_to_id = {
            agent.fiscal_name:agent.id for agent in self.session.query(db.Agent.id, db.Agent.fiscal_name)
        }


        self.warehouse_name_to_id = {
            warehouse.description:warehouse.id for warehouse in self.session.query(db.Warehouse.id, db.Warehouse.description)
        }

        self.courier_name_to_id = {
            courier.description:courier.id for courier in self.session.query(db.Courier.id, db.Courier.description)
        }
        
        self.desc_to_item = {build_description(item):item for item in self.session.query(db.Item)}

        self.specs = set() 
        for r in self.session.query(PurchaseProformaLine.specification).distinct():
            self.specs.add(r[0])

        self.conditions = set() 
        for r in self.session.query(PurchaseProformaLine.condition).distinct():
            self.conditions.add(r[0])

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

        m = QStringListModel()
        m.setStringList(self.desc_to_item.keys())

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.description_line_edit.setCompleter(c) 


        m = QStringListModel()
        m.setStringList(self.conditions)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.condition_line_edit.setCompleter(c) 

        
        m = QStringListModel()
        m.setStringList(self.specs)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.spec_line_edit.setCompleter(c)        

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

        result = self.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,\
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
        
        max_credit = self.session.query(db.Partner.amount_credit_limit).scalar()

        total = self.session.query(func.sum(PurchaseProformaLine.quantity * PurchaseProformaLine.price)).\
            select_from(Partner, PurchaseProforma, PurchaseProformaLine).\
                where(PurchaseProformaLine.proforma_id == PurchaseProforma.id).\
                    where(PurchaseProforma.partner_id == Partner.id).\
                        where(Partner.id == partner_id).scalar() 

        paid = self.session.query(func.sum(PurchasePayment.amount)).select_from(Partner, \
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
        self.title = 'Line - Error'
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
        self.total_proforma_line_edit.setText(str(self.lines_model.total))
        self.total_tax_line_edit.setText(str(self.lines_model.tax))
        self.subtotal_proforma_line_edit.setText(str(self.lines_model.subtotal))

    def _dateFromString(self, date_str):
        return date(int(date_str[4:len(date_str)]), int(date_str[2:4]), int(date_str[0:2])) 

    def keyPressEvent(self, event):
        if self.addButton.hasFocus():
            if event.key() == Qt.Key_Return:
                self.addHandler()
                self.description_line_edit.setFocus()              
        else:
            super().keyPressEvent(event)

    def _formToProforma(self):
        proforma = db.PurchaseProforma() 
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
            self.close() 
        
class EditableForm(Ui_PurchaseProformaForm, QWidget):
    
    def __init__(self, index):
        super().__init__() 
        
    
