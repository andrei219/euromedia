
from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter
from PyQt5.QtCore import QStringListModel, Qt


from utils import parse_date

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import AvailableStockModel, SaleProformaLineModel, IncomingStockModel

import db

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
        self.session = self.model.session 
        self.lines_model = SaleProformaLineModel(self.session)
        self.lines_view.setModel(self.lines_model) 
        
        self.setUp() 

    def setUp(self):

        self.items = {str(item):item for item in self.session.query(db.Item)}
        self.specs = {spec[0] for spec in self.session.query(db.PurchaseProformaLine.specification).distinct()}
        self.conditions = {c[0] for c in self.session.query(db.PurchaseProformaLine.condition).distinct()}

        self.partner.setFocus() 

        self.type.setCurrentText('1')
        self.number.setText(str(self.model.nextNumberOfType(1)).zfill(6))
        self.date.setText(date.today().strftime('%d%m%Y'))

        self.partner_name_to_id = {
            partner.fiscal_name:partner.id for partner in self.session.query(db.Partner.id, db.Partner.fiscal_name).\
                where(db.Partner.active == True)
        }

        self.agent_name_to_id = {
            agent.fiscal_name:agent.id for agent in self.session.query(db.Agent.id, db.Agent.fiscal_name).\
                where(db.Agent.active == True)
        }

        self.warehouse_name_to_id = {
            warehouse.description:warehouse.id for warehouse in self.session.query(db.Warehouse.id, db.Warehouse.description)
        }

        self.courier_name_to_id = {
            courier.description:courier.id for courier in self.session.query(db.Courier.id, db.Courier.description)
        }


        setCommonViewConfig(self.lines_view)
        setCommonViewConfig(self.stock_view)


        self.warehouse.addItems(self.warehouse_name_to_id.keys())
        self.warehouse.setCurrentText('Free Sale')        

        self.agent.addItems(self.agent_name_to_id.keys())
        self.courier.addItems(self.courier_name_to_id.keys())


        # Completers:

        m = QStringListModel()
        m.setStringList(self.items.keys())

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.description.setCompleter(c) 

        m = QStringListModel()
        m.setStringList(self.specs)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.spec.setCompleter(c) 


        m = QStringListModel()
        m.setStringList(self.conditions)

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.condition.setCompleter(c) 

        m = QStringListModel()
        m.setStringList(self.partner_name_to_id.keys())

        c = QCompleter()
        c.setFilterMode(Qt.MatchContains)
        c.setCaseSensitivity(False)
        c.setModel(m)

        self.partner.setCompleter(c) 

        def priceOrQuantityChanged(value):
            self.subtotal.setValue(self.quantity.value() * self.price.value())
        
        def subtotalOrTaxChanged(value):
            self.total.setValue(self.subtotal.value() * (1 + int(self.tax.currentText())/100))

        def typeChanged(type):
            next_num = self.model.nextNumberOfType(int(type))
            self.number.setText(str(next_num))

        def warehouseChanged(text):
            self.lines_model.reset() 

        self.price.valueChanged.connect(priceOrQuantityChanged) 
        self.quantity.valueChanged.connect(priceOrQuantityChanged)
        self.tax.currentIndexChanged.connect(subtotalOrTaxChanged)
        self.subtotal.valueChanged.connect(subtotalOrTaxChanged)
        self.type.currentTextChanged.connect(typeChanged)
        self.warehouse.currentTextChanged.connect(warehouseChanged)


        self.partner.returnPressed.connect(self.partnerSearch)
        self.search.clicked.connect(self.searchClicked)
        self.deleteButton.clicked.connect(self.deleteHandler) 
        self.save.clicked.connect(self.saveHandler) 
        self.advance_sale.toggled.connect(self.advanceSaleToggled)
        self.availbale_stock_label.setText('Available Physical Stock:')

        self.normal_sale.setChecked(True)
        self.searchClicked() 
        self.addButton.clicked.connect(self.normalAddHandler) 

    def searchClicked(self):
        description = self.description.text() 
        try:
            item = self.items[description] 
        except KeyError:
            item = None
        warehouse = self.warehouse.currentText() 
        normal = self.normal_sale.isChecked() 
        specification = self.spec.text() 
        condition = self.condition.text()  
        if normal:
            self._resetStockAvailable(warehouse, condition=condition, specification=specification, \
                item=item)
        else:
            self._resetIncomingStock(warehouse, condition=condition, specification=specification, item=item)

    def stockDoubleClicked(self):
        row = {index.row() for index in self.stock_view.selectedIndexes()}.pop() 
        stock = self.stock_model.stocks[row]
        available_qnt = stock.quantity
        form = QuantityPriceForm(self) 
        form.quantity.setMinimum(1)
        form.quantity.setMaximum(available_qnt)
        if form.exec_():
            if not form.quantity.value():
                QMessageBox.critical(self, 'Line - Error', 'Quantity must be > 0')
                return
            try:
                1 / form.price.value()
            except ZeroDivisionError:
                QMessageBox.critical(self, 'Line - Error', 'Price must be > 0 ') 
                return    
        
            warehouse = self.warehouse.currentText() 
            tax = int(self.tax.currentText()) 
            item = self.items[stock.item]
            try:
                self.lines_model.add(item, stock.condition, stock.specification, form.quantity.value(), \
                    form.price.value(), tax, stock.eta) 
                self._clearLineFields() 
                self._resetIncomingStock(warehouse, item=None, condition=None, specification=None)

            except DuplicateLine:
                QMessageBox.critical(self, 'Line - Error', 'Cant add duplicate line!')
                return

    def advanceSaleToggled(self, checked):
        self.lines_model.reset() 
        if checked:
            self.stock_view.doubleClicked.connect(self.stockDoubleClicked)
            self.addButton.clicked.disconnect(self.normalAddHandler)
            self.addButton.clicked.connect(self.advanceAddHandler) 
            self.availbale_stock_label.setText('Available Incoming Stock:')
        else:
            self.stock_view.doubleClicked.disconnect(self.stockDoubleClicked)
            self.addButton.clicked.disconnect(self.advanceAddHandler)
            self.addButton.clicked.connect(self.normalAddHandler) 
            self.availbale_stock_label.setText('Available Physical Stock:')

    def partnerSearch(self):
        partner_id = self.partner_name_to_id.get(self.partner.text())
        if not partner_id:
            return
        
        try:
            available_credit, max_credit = self._computeCreditAvailable(partner_id) 
            self.available_credit.setValue(float(available_credit))

            def prevent(value):
                if value > available_credit:
                    self.credit.setValue(available_credit)

            self.credit.valueChanged.connect(prevent) 

        except TypeError:
            pass 
            
        result = self.session.query(Agent.fiscal_name, Partner.warranty, Partner.euro,\
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

    def _computeCreditAvailable(self, partner_id):
        from db import Partner, SaleProformaLine, SaleProforma, \
            SalePayment, func
        
        max_credit = self.session.query(db.Partner.amount_credit_limit).scalar()

        total = self.session.query(func.sum(SaleProformaLine.quantity * SaleProformaLine.price)).\
            select_from(Partner, SaleProforma, SaleProformaLine).\
                where(SaleProformaLine.proforma_id == SaleProforma.id).\
                    where(SaleProforma.partner_id == Partner.id).\
                        where(Partner.id == partner_id).scalar() 

        paid = self.session.query(func.sum(SalePayment.amount)).select_from(Partner, \
            SaleProforma, SalePayment).where(SaleProforma.partner_id == Partner.id).\
                where(SalePayment.proforma_id == SaleProforma.id).\
                    where(Partner.id == partner_id).scalar() 

        if total and paid:
            return max_credit + paid - total, max_credit

        # Default returns None, caller will check unpacking error 

    def _resetStockAvailable(self, warehouse, *, item, condition, specification):

        self.stock_model = AvailableStockModel(warehouse, item=item, condition=condition, \
            specification=specification, lines=self.lines_model.lines)

        self.stock_view.setModel(self.stock_model)

    def _resetIncomingStock(self, warehouse, *, item, condition, specification):
        print('in resetInomcing, lines=', self.lines_model.lines)
        self.stock_model = IncomingStockModel(warehouse, condition=condition, item=item,\
             specification=specification, lines=self.lines_model.lines)
        
        self.stock_view.setModel(self.stock_model)
    
    def _validHeader(self):
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

        if self.credit.value() > self.available_credit.value():
            QMessageBox.critical(self, 'Erro - Update', 'Credit must be < than avaliable credit')
            return False
        return True

    def _validLine(self):
        self.title = 'Line - Error'
        try:
            self.items[self.description.text()]
        except KeyError:
            QMessageBox.critical(self, self.title, 'That item does not exist')
            return False
        
        if not self.spec.text():
            QMessageBox.critical(self, self.title, 'Specification cannot be empty')
            return False

        if not self.spec.text() in self.specs:
            QMessageBox.critical(self, self.title, 'Specification must exist')

        if not self.condition.text():
            QMessageBox.critical(self, self.title, 'Conditions cannot be empty')
            return False
        
        if not self.condition.text() in self.conditions:
            QMessageBox.critical(self, self.title, 'Condition must exist')
            return False

        try:
            1 / self.price.value()
        except ZeroDivisionError: 
            QMessageBox.critical(self, self.title, 'Price must be > 0')
            return False
        return True

    def _formToProforma(self):
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
        proforma.cancelled = False
        return proforma


    def _clearLineFields(self):
        self.description.setText('')
        self.spec.setText('')
        self.condition.setText('')
        self.quantity.setValue(1)
        self.price.setValue(0)

    def _dateFromString(self, date_str):
        return date(int(date_str[4:len(date_str)]), int(date_str[2:4]), int(date_str[0:2])) 

    def _updateTotals(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

    def _lineFromStock(self):
        for stock in self.stock_model.stocks:
            if stock.item == self.description.text() and self.spec.text() == stock.specification and \
                self.condition.text() == stock.condition:
                    return stock.quantity
        return False

    def normalAddHandler(self):
        title = 'Line - Error'
        if not self._validLine():
            return 
        
        stock_qnt = self._lineFromStock() 
        if not stock_qnt:
            QMessageBox.critical(self, title, 'That stock is not available')
            return 
        elif stock_qnt < self.quantity.value():
            QMessageBox.critical(self, title, 'Quantity in line exceeds available quantity')
            return 
        else:
            try:
                item, condition, spec, quantity, price, tax = self.items[self.description.text()], \
                    self.condition.text(), self.spec.text(), self.quantity.value(), self.price.value(), \
                        int(self.tax.currentText())
                self.lines_model.add(item, condition, spec, quantity, price, tax)
                self._clearLineFields() 
                self._resetStockAvailable(warehouse=self.warehouse.currentText(), item=None, \
                    condition=None, specification=None)
            except DuplicateLine:
                QMessageBox.critical(self, title, 'Duplicate line!. Try another one.')
                return
    
    def advanceAddHandler(self):
        QMessageBox.information(self, 'Information', 'For advance sale you need to double-click the stock below')
        return

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
            QMessageBox.critical(self, 'Error - Lines', 'Empty proforma')
            return
        proforma = self._formToProforma() 
        try:
            self.model.add(proforma)
            self.lines_model.save(proforma) 
        except:
            raise 
        else:
            self.close() 

    def closeEvent(self, event):
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
        except:
            pass       

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.addButton.hasFocus()\
            and self.normal_sale.isChecked():
                self.normalAddHandler() 
        else:
            super().keyPressEvent(event) 
    
class EditableSaleProformaForm(Ui_SalesProformaForm, QWidget):
    pass 
