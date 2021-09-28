
from datetime import date

from PyQt5.QtWidgets import QWidget, QMessageBox, QCompleter, QTableView
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtCore import QAbstractTableModel

from utils import parse_date

from ui_sale_proforma_form import Ui_SalesProformaForm

from models import AvailableStockModel, SaleProformaLineModel, ManualStockModel

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
        self.session = self.model.session 
        self.parent = parent

        self.lines_model = SaleProformaLineModel(self.session)
        self.lines_view.setModel(self.lines_model)

        self.base_items = {str(item):item for item in self.session.query(db.Item)}

        self.base_specs = {spec[0] for spec in \
            self.session.query(db.PurchaseProformaLine.specification).distinct()}

        self.base_conditions = {c[0] for c in \
            self.session.query(db.PurchaseProformaLine.condition).distinct()}

        self.set_up_header() 

        self.set_filter_completers()

        self.search.clicked.connect(self.normal_search) 
        self.stock_view.doubleClicked.connect(self.stock_double_clicked)
        self.delete_all.clicked.connect(self.delete_all_clicked)
        self.lines_view.clicked.connect(self.lines_view_clicked)
        self.delete_button.clicked.connect(self.delete_clicked)
        self.mixed.toggled.connect(self.mixed_toggled)
        self.automatic.toggled.connect(self.automatic_toggled)
        self.generate_line.clicked.connect(self.generate_line_clicked) 

    def set_up_header(self):

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

        def typeChanged(type):
            next_num = self.model.nextNumberOfType(int(type))
            self.number.setText(str(next_num))

        self.type.currentTextChanged.connect(typeChanged)
        self.partner.returnPressed.connect(self.partner_search)

    def partner_search(self):
        partner_id = self.partner_name_to_id.get(self.partner.text())
        if not partner_id:
            return
        try:
            available_credit = self._compute_credit_available(partner_id) 
            self.available_credit.setValue(float(available_credit))
            self.credit.setMaximum(float(available_credit))
        
        except TypeError:
            raise 
            
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


        # Protect against None results from partners with no credits.
        if max_credit is None:
            max_credit = 0
        if total is None:
            total = 0
        if paid is None:
            paid = 0 

        return max_credit + paid - total 

    def clear_filters(self):
        self.description.clear()
        self.spec.clear()
        self.condition.clear() 

    def mixed_toggled(self, on):
        self.set_filter_completers(mixed=on)
        self.clear_filters()
        self.reconnect(on)
    
    def reconnect(self, mixed_on):
        try:
            self.search.disconnect()
            self.stock_view.disconnect() 
        except TypeError:
            pass 

        if mixed_on:
            self.search.clicked.connect(self.manual_search)
        else:
            self.search.clicked.connect(self.normal_search)
            self.stock_view.doubleClicked.connect(self.stock_double_clicked)
        

    def automatic_toggled(self, on):
        # No model yet 
        if not hasattr(self, 'stock_model'): return 
        if isinstance(self.stock_model, ManualStockModel):
            for row in range(self.stock_model.rowCount()):
                index = self.stock_model.index(row, ManualStockModel.REQUEST)
                self.stock_model.setData(index, 0) 
        
        # Change flags method of the model, in order to make all cells
        # non-editable, editable by you computing the proportionals.
        # uuuuuuuuuuuuuuuuu goood job my frei .
        if on:
            def flags(index):
                if not index.isValid():
                    return
                return Qt.ItemFlags(~Qt.ItemIsEditable) 
            self.stock_model.flags = flags
        else:
            def flags(index):
                if not index.isValid():
                    return
                if index.column() == 4:
                    return Qt.ItemFlags(QAbstractTableModel.flags(self.stock_model, index) |
                        Qt.ItemIsEditable)
                else:
                    return Qt.ItemFlags(~Qt.ItemIsEditable)
            
            self.stock_model.flags = flags 

    def clear_request_stock_model_column(self):
        pass 

    def set_filter_completers(self, mixed=False):
            m = QStringListModel()
            if mixed:
                s = set() 
                for desc in self.base_items.keys():
                    s.add(desc[0:desc.index('GB') + 2] + ' GB Mixed Color')
                self.current_items = s 
            else:
                self.current_items = self.base_items.keys() 
            
            m.setStringList(self.current_items) 
            c = QCompleter()
            c.setFilterMode(Qt.MatchContains)
            c.setCaseSensitivity(False)
            c.setModel(m)
            self.description.setCompleter(c) 

            m = QStringListModel()
            self.current_specs = self.base_specs if not mixed else {'Mix'}.union(self.base_specs) 
            m.setStringList(self.current_specs)
            c = QCompleter()
            c.setFilterMode(Qt.MatchContains)
            c.setCaseSensitivity(False)
            c.setModel(m)

            self.spec.setCompleter(c) 


            m = QStringListModel()
            self.current_conditions = self.base_conditions if not mixed else \
                {'Mix'}.union(self.base_conditions) 
            m.setStringList(self.current_conditions)

            c = QCompleter()
            c.setFilterMode(Qt.MatchContains)
            c.setCaseSensitivity(False)
            c.setModel(m)

            self.condition.setCompleter(c)


    def delete_all_clicked(self):
        self.lines_model.reset() 
        warehouse = self.warehouse.currentText()
        self.reset_stock(warehouse, item=None,condition=None, specification=None)

    def lines_view_clicked(self):
        row = self.lines_view.currentIndex().row() 

    def delete_clicked(self):
        indexes = self.lines_view.selectedIndexes() 
        try:
            self.lines_model.delete(indexes)
        except:
            raise 
        else:
            warehouse = self.warehouse.currentText()
            self.reset_stock(warehouse, item=None, condition=None, specification=None)

    def stock_double_clicked(self):
        from line_complete_form import Form

        row = self.stock_view.currentIndex().row() 
        stock = self.stock_model.stocks[row]
        f = Form(self) 
        f.qnt.setMaximum(stock.quantity) 
        if f.exec_():
            showing, qnt, price, ignore, tax = \
                f.condition.text(), f.qnt.value(), f.price.value(), \
                    f.ignore_spec.isChecked(), int(f.tax.currentText())
            try:
                self.lines_model.add(stock.item, stock.condition, showing, stock.specification, \
                    ignore, qnt, price, tax)
               
                self.lines_view.setSelectionBehavior(QTableView.SelectRows)
                warehouse = self.warehouse.currentText()
                self.reset_stock(warehouse, item=None, condition=None, specification=None)
                self.update_total_fields() 
            except:
                raise 
    
    def not_valid_filters(self):
        description, condition, spec = self.description.text(), \
            self.condition.text(), self.spec.text() 

        aux_conditions, aux_items, aux_specs = {''}.union(self.current_conditions), \
            {''}.union(self.current_items), {''}.union(self.current_specs)

        if description not in aux_items or spec not in aux_specs or \
            condition not in aux_conditions:
                return True 

    def better_normal_line(self):
        f = lambda stock_entry_request:stock_entry_request.requested_quantity > 0
        aux = list(filter(f,self.stock_model.stocks.values()))
        return len(aux) == 1

    def generate_line_clicked(self):
        # No model yet or is not the correct type
        # Remember lazy eval , this is valid
        if not hasattr(self, 'stock_model') or not isinstance(self.stock_model, ManualStockModel):
            return
        elif self.better_normal_line():
            # I dont do it from code because we would need showing condition field
            QMessageBox.critical(self, 'Error', "Make a normal line!")
            return
        else:
            print('process here')


    def normal_search(self):
        if self.not_valid_filters():
            QMessageBox.critical(self, 'Error', 'You must choose an option given by the autocompleter')
            return 
        description = self.description.text() 
        try:
            item = self.base_items[description]
        except KeyError:
            item = None
        warehouse = self.warehouse.currentText() 
        specification = self.spec.text() 
        condition = self.condition.text()
        if not condition:
            condition = None
        if not specification:
            specification = None
        
        self.reset_stock(warehouse, condition=condition, specification=specification, item=item)

    def update_total_fields(self):
        self.proforma_total.setText(str(self.lines_model.total))
        self.proforma_tax.setText(str(self.lines_model.tax))
        self.subtotal_proforma.setText(str(self.lines_model.subtotal))

    def reset_stock(self, warehouse, *, item, condition, specification):
        self.stock_model = AvailableStockModel(warehouse, item=item, condition=condition,\
            specification=specification, lines=self.lines_model.lines)
        
        self.stock_view.setModel(self.stock_model)
        self.set_stock_view_config() 

    def set_stock_view_config(self, mixed=False):
        self.stock_view.setSelectionBehavior(QTableView.SelectRows)
        if not mixed:
            self.stock_view.setSelectionMode(QTableView.SingleSelection)
        # self.stock_view.setAlternatingRowColors(True)
        self.stock_view.resizeColumnsToContents() 

    def manual_search(self):
        if self.not_valid_filters():
            QMessageBox.critical(self, 'Error', 'You must choose an option given by the autocompleter')
            return
        warehouse = self.warehouse.currentText() 
        specification = self.spec.text() 
        condition = self.condition.text()
        description = self.description.text() 

        if specification == 'Mix' or not specification:
            specification = None
        if condition == 'Mix' or not condition:
            condition = None
        if not description:
            description = None

        self.reset_manual_stock(warehouse, mixed_description=description, \
            condition=condition, specification=specification)

    def reset_manual_stock(self, warehouse, *, mixed_description ,condition, specification):

        self.stock_model = ManualStockModel(warehouse, mixed_description, condition, \
            specification, self.lines_model.lines) 
        self.stock_view.setModel(self.stock_model) 
        self.set_stock_view_config(mixed=True) 

    def closeEvent(self, event):
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
        except:
            pass
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.quantity.hasFocus():
            indexes = self.stock_view.selectedIndexes()
            if not indexes:
                return
            try:
                self.set_proportional_stock_request(indexes)
            except ValueError:
                pass 
        else:
            super().keyPressEvent(event) 
        
    
    def set_proportional_stock_request(self, indexes):
        rows = {index.row() for index in indexes}
        total = 0
        for row in rows:
            stock_entry = self.stock_model.stocks[row].stock_entry 
            total += stock_entry.quantity 
        if total < self.quantity.value():
            raise ValueError
        
