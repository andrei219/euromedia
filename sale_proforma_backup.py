
from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView
from PyQt5.QtCore import QStringListModel, Qt


from utils import parse_date

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import AvailableStockModel, SaleProformaLineModel, IncomingStockModel, \
    FakeLineModel

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

        # var that hold the default config 
        self.proportional_var = None
        self.fake_var = False
        self.normal_var = True 

        self._set_config(default=True)

        self.apply_config.clicked.connect(self._apply_config_clicked)
        self.mixed.toggled.connect(self._mixed_checked)
        self.fake.toggled.connect(self._fake_checked)

        self._set_up_header() 

    def _set_up_header(self):

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

        self.warehouse.addItems(self.warehouse_name_to_id.keys())
        self.agent.addItems(self.agent_name_to_id.keys())
        self.courier.addItems(self.courier_name_to_id.keys())

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

        self.price.valueChanged.connect(priceOrQuantityChanged) 
        self.quantity.valueChanged.connect(priceOrQuantityChanged)
        self.tax.currentIndexChanged.connect(subtotalOrTaxChanged)
        self.subtotal.valueChanged.connect(subtotalOrTaxChanged)
        self.type.currentTextChanged.connect(typeChanged)

        self.partner.returnPressed.connect(self._partner_search)
        

    def _apply_config_clicked(self):
        proportional = None
        if self.mixed.isChecked():
            proportional = self.proportional.isChecked() 
        normal = self.normal_sale.isChecked() 
        fake = self.fake.isChecked() 
        self._set_config() 
        self._configure_handlers_fields(normal, fake, proportional) 
        self._disable_config() 


    def _disable_config(self):
        self.normal_sale.setEnabled(False)
        self.advance_sale.setEnabled(False)
        self.fake.setEnabled(False)
        self.mixed.setEnabled(False)
        self.apply_config.setEnabled(False)

    def _fake_checked(self, on):
        if on:
            self.mixed.setChecked(False)
    
    def _mixed_checked(self, on):
        if on:
            self.fake.setChecked(False)
   
    def _configure_handlers_fields(self, normal, fake, proportional):
        if not normal and fake:
            self.addButton.clicked.connect(self._advance_fake_add)
            self.deleteButton.clicked.connect(self._advance_fake_delete)
            self.save.clicked.connect(self._advance_fake_save)
            self.search.clicked.connect(self._advance_fake_search_stock)
        elif normal and fake:
            self.addButton.clicked.connect(self._normal_fake_add)
            self.search.clicked.connect(self._normal_fake_search_stock)
            self.deleteButton.clicked.connect(self._normal_fake_delete) 
            self.save.clicked.connect(self._normal_fake_save)
            self.lines_model = FakeLineModel(self.model.session)
            self.lines_view.setModel(self.lines_model)

        elif not normal and proportional is not None and proportional:
            # advance, proportional
            self.addButton.clicked.connect(self._advance_proportional_add)
            self.search.clicked.connect(self._advance_proportional_search_stock)
            self.deleteButton.clicked.connect(self._advance_proportional_delete)
            self.save.clicked.connect(self._advance_proportional_save)
        elif not normal and proportional is not None and not proportional:
            # advance, manual
            self.addButton.clicked.connect(self._advance_manual_add)
            self.search.clicked.connect(self._advance_manual_search_stock)
            self.deleteButton.clicked.connect(self._advance_manual_delete)
            self.save.clicked.connect(self._advance_manual_delete) 
        elif normal and proportional is not None and proportional:
            # normal , proportional
            self.addButton.clicked.connect(self._normal_proportional_add)
            self.deleteButton.clicked.connect(self._normal_proportional_delete)
            self.save.clicked.connect(self._normal_proportional_save)
            self.search.clicked.connect(self._normal_proportional_search_stock)
        elif normal and proportional is not None and not proportional:
            # print('normal, manual')
            self.addButton.clicked.connect(self._normal_manual_add)
            self.deleteButton.clicked.connect(self._normal_manual_delete)
            self.save.clicked.connect(self._normal_manual_save)
            self._normal_search_stock.connect(self._normal_manual_search_stock)
        elif normal:
            self.addButton.clicked.connect(self._normal_add)
            self.deleteButton.clicked.connect(self._normal_delete)
            self.save.clicked.connect(self._normal_save)
            self.search.clicked.connect(self._normal_search_stock)
             
            self._normal_setup()
        elif not normal:
            self.addButton.clicked.connect(self._advance_add)
            self.deleteButton.clicked.connect(self._advance_delete)
            self.search.clicked.connect(self._advance_search_stock)
            self.save.clicked.connect(self._advance_save)
            self.stock_view.doubleClicked.connect(self._advance_double_click)
            self._advanced_set_up() 
    
    # BEFORE SEARCH CLICKED, CHECK LAST_CONFIG != ACTUAL_CONFIG
    # def _search_clicked(self):
    #     description = self.description.text() 
    #     try:
    #         item = self.items[description] 
    #     except KeyError:
    #         item = None
    #     warehouse = self.warehouse.currentText() 
    #     normal = self.normal_sale.isChecked() 
    #     specification = self.spec.text() 
    #     condition = self.condition.text()  
    #     if normal:
    #         self._resetStockAvailable(warehouse, condition=condition, specification=specification, \
    #             item=item)
    #     else:
    #         self._resetIncomingStock(warehouse, condition=condition, specification=specification, item=item)

    def _partner_search(self):
        partner_id = self.partner_name_to_id.get(self.partner.text())
        if not partner_id:
            return
        
        try:
            available_credit, max_credit = self._compute_credit_available(partner_id) 
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

    def _compute_credit_available(self, partner_id):
        from db import Partner, SaleProformaLine, SaleProforma, \
            SalePayment, func
        
        max_credit = self.session.query(db.Partner.amount_credit_limit).\
            where(db.Partner.id == partner_id).scalar()

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

    def _reset_stock_available(self, warehouse, *, item, condition, specification):

        self.stock_model = AvailableStockModel(warehouse, item=item, condition=condition, \
            specification=specification, lines=self.lines_model.lines)
        self.stock_view.setModel(self.stock_model)
        self.stock_view.resizeColumnsToContents() 

    def _reset_incoming_stock(self, warehouse, *, item, condition, specification):
        self.stock_model = IncomingStockModel(warehouse, condition=condition, item=item,\
             specification=specification, lines=self.lines_model.lines)
        self.stock_view.setModel(self.stock_model)
        self.stock_view.resizeColumnsToContents() 
    
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
        proforma.cancelled = False
        proforma.note = self.note.toPlainText()[0:255]
        proforma.normal = self.normal_sale.isChecked() 
        return proforma

    def _clearLineFields(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear()
        self.quantity.clear()
        self.price.clear()

    def _dateFromString(self, date_str):
        return date(int(date_str[4:len(date_str)]), int(date_str[2:4]), int(date_str[0:2])) 

    def _update_totals(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

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
    
    def _set_completers(self, normal, fake, proportional):
        pass 

    def _config_changed(self):
        if self.normal_var != self.normal_sale.isChecked():
            return True
        if self.fake_var != self.fake.isChecked():
            return True
        if self.mixed.isChecked() and self.proportional_var is None:
            return True

    def _set_config(self, default=False):
        if default:
            self.proportional_var = None
            self.normal_var = True 
            self.fake_var = False
            self.mixed.setChecked(False)
            self.fake.setChecked(False)
            self.normal_sale.setChecked(True)
        else:
            if self.mixed.isChecked():
                self.proportional_var = self.proportional.isChecked()
            else:
                self.proportional_var = None
            self.normal_var = self.normal_sale.isChecked()
            self.fake_var = self.fake.isChecked() 

    # Controllers : It will be a class of controllers for each
    # configuration combination. The naming system will be:
    # def _type_···_controlname(self): 


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

        if self.credit.value() > self.available_credit.value():
            QMessageBox.critical(self, 'Erro - Update', 'Credit must be < than avaliable credit')
            return False
        return True


    def _line_from_stock(self):
        for stock in self.stock_model.stocks:
            if stock.item == self.description.text() and self.spec.text() == stock.specification and \
                self.condition.text() == stock.condition:
                    return stock.quantity
        return False


    def _normal_valid_line(self):
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

    # Normal case:
    def _normal_add(self):
        title = 'Line - Error'
        if not self._normal_valid_line():
            return 
        
        stock_qnt = self._line_from_stock() 
        if not stock_qnt:
            QMessageBox.critical(self, title, 'That stock is not available')
            return 
        elif stock_qnt < self.quantity.value():
            QMessageBox.critical(self, title, 'Quantity in line exceeds available quantity')
            return 
        else:
            try:
                item, condition, spec, ignore,  quantity, price, tax = self.items[self.description.text()], \
                    self.condition.text(), self.spec.text(), self.ignore.isChecked(), self.quantity.value(), \
                        self.price.value(), int(self.tax.currentText())
                self.lines_model.add(item, condition, spec, ignore, quantity, price, tax)
                self._clearLineFields() 
                self._reset_stock_available(warehouse=self.warehouse.currentText(), item=None, \
                    condition=None, specification=None)
            except DuplicateLine:
                QMessageBox.critical(self, title, 'Duplicate line!. Try another one.')

    def _normal_search_stock(self):
        description = self.description.text() 
        try:
            item = self.items[description] 
        except KeyError:
            item = None
        warehouse = self.warehouse.currentText() 
        normal = self.normal_sale.isChecked() 
        specification = self.spec.text() 
        condition = self.condition.text()
        self._reset_stock_available(warehouse, condition=condition, \
            specification=specification, item=item)

    def _normal_save(self):
        self._common_save() 

    def _normal_delete(self):
        self._common_delete() 
    
    # Advanced case:
    def _advance_add(self):
        QMessageBox.critical(self, 'Information', 'In this config you need to double-click the stocks')
    
    def _advance_search_stock(self):
        description = self.description.text() 
        try:
            item = self.items[description] 
        except KeyError:
            item = None
        warehouse = self.warehouse.currentText() 
        normal = self.normal_sale.isChecked() 
        specification = self.spec.text() 
        condition = self.condition.text()
        self._reset_incoming_stock(warehouse, condition=condition, \
            specification=specification, item=item)

    def _advance_save(self):
        self._common_save() 

    def _advance_delete(self):
        self._common_delete() 
    
    def _advance_double_click(self):
        
        row = {i.row() for i in self.stock_view.selectedIndexes()}.pop()
        stock = self.stock_model.stocks[row]
        pass 

        if QuantityPriceForm(self).exec_():
            pass 


    # Advance - Fake case:
    def _advance_fake_add(self):
        print('_advance_fake_add') 

    def _advance_fake_search_stock(self):
        print('_advance_fake_search_stock')

    def _advance_fake_search_stock(self):
        print('_advance_fake_search_stock')
    
    def _advance_fake_save(self):
        print('_advance_fake_save')
    
    def _advance_fake_delete(self):
        print('_advance_fake_delete')
    
    # Normal - Fake case:
    def _normal_fake_add(self):
        print('_normal_fake')

    def _normal_fake_search_stock(self):
        print('_normal_fake')

    def _normal_fake_save(self):
        print('norma_fake save')

    def _normal_fake_delete(self):
        print('_normal_fake_delete')

    # Advance - Proportional case:
    def _advance_proportional_add(self):
        print('_advance_proportional_add') 

    def _advance_proportional_search_stock(self):
        print('advance_proportional_search_stock')

    def _advance_proportional_save(self):
        print('advance_proportional_save')

    def _advance_proportional_delete(self):
        print('advance_prportional_save')

    # Advance - Manual Case:
    def _advance_manual_add(self):
        print('_advance_manual_add')
    
    def _advance_manual_search_stock(self):
        print('_advanced_manuak_search_stock')
    
    def _advance_manual_delete(self):
        print('_advance_manual_delete')

    def _advance_manual_save(self):
        print('_advance_manual_save')

    # Normal - Proportional case:
    def _normal_proportional_add(self):
        print('_normal_proportional_add')

    def _normal_proportional_search_stock(self):
        print('_normal_proportional_search_stock')

    def _normal_proportional_save(self):
        print('_normal_proportional_save')

    def _normal_proportional_delete(self):
        print('_normal_proportional_delete')


    # Normal - Manual case:
    def _normal_manual_add(self):
        print('_normal_manual_add')

    def _normal_manual_search_stock(self):
        print('_normal_manual_search_stock')

    def _normal_manual_save(self):
        print('_normal_manual_save')

    def _normal_manual_delete(self):
        print('_normal_manual_delete')


    # DEF SETUPS:
    def _advance_fake_setup(self):
        pass 

    def _normal_fake_setup(self):
        pass

    def _advance_proportional(self):
        pass

    def _advance_manual_setup(self):
        pass 

    def _normal_proportional_setup(self):
        pass 

    def _normal_manual_setup(self):
        pass 

    def _normal_setup(self):
        
        self._set_common_setup() 

        self.selected_stock_view.setEnabled(False)
        self.lines_model = SaleProformaLineModel(self.model.session)
        self.lines_view.setModel(self.lines_model) 
        self.showing_condition.setEnabled(False)

    def _advanced_set_up(self):
        
        self._set_common_setup() 

        self.selected_stock_view.setEnabled(False)
        self.lines_model = SaleProformaLineModel(self.model.session)
        self.lines_view.setModel(self.lines_model)
        self.showing_condition.setEnabled(False) 



    # COMMONS:    
    def _set_common_setup(self):
        self.items = {str(item):item for item in self.session.query(db.Item)}
        self.specs = {spec[0] for spec in self.session.query(db.PurchaseProformaLine.specification).distinct()}
        self.conditions = {c[0] for c in self.session.query(db.PurchaseProformaLine.condition).distinct()}

        self.lines_view.setSelectionBehavior(QTableView.SelectRows)
        
        setCommonViewConfig(self.stock_view) 

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


    def _common_delete(self):
        indexes = self.lines_view.selectedIndexes() 
        try:
            self.lines_model.delete(indexes) 
        except:
            raise 
        
    def _common_save(self):
        if not self._valid_header():
            return
        if not self.lines_model.lines:
            QMessageBox.critical(self, 'Error - Lines', 'Empty proforma')
            return
        proforma = self._form_to_proforma() 
        try:
            self.model.add(proforma)
            self.lines_model.save(proforma) 
        except:
            raise 
        else:
            self.close() 

class EditableForm(Form):
    pass 
