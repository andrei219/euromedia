from sqlalchemy import create_engine, event, insert, select, update, delete, and_
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb') 

# pool_size=20, max_overflow=0)

# engine = create_engine('sqlite:///euro.db')

Session = scoped_session(sessionmaker(bind=engine, autoflush=False))

from datetime import datetime

from sqlalchemy import ( 
    Table, Column, Integer, Numeric, String, Enum, DateTime, 
    ForeignKey, UniqueConstraint, SmallInteger, Boolean, LargeBinary,
    Date, CheckConstraint
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base() 

session = Session() 

class Warehouse(Base):

    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description 

class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description

class Item(Base):

    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(50))
    category = Column(String(50))
    model = Column(String(50))
    capacity = Column(String(50))
    color = Column(String(50))

    __table_args__ = ( 
        UniqueConstraint('manufacturer', 'category', 'model', 'capacity', 'color', \
            name='uix_1'), 
    )

    def __init__(self, manufacturer, category, model, capacity, color):
        self.manufacturer = manufacturer
        self.category = category
        self.model = model
        self.capacity = capacity
        self.color = color 
    
    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if self.manufacturer == other.manufacturer and self.category == other.category \
            and self.model == other.model and self.capacity == other.capacity and self.color == other.color:
                return True
        return False

    def __hash__(self):
        return hash(''.join(str(v) for v in self.__dict__.values()))
    
    def __str__(self):
        return self.manufacturer + ' ' + self.category + ' ' + self.model + ' ' + str(self.capacity) +\
            ' GB ' + self.color 

    
# Agents:
class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True) 
    fiscal_number = Column(String(50))
    fiscal_name = Column(String(50), unique=True) # To differentiate 
    email = Column(String(50))
    phone = Column(String(60))
    active = Column(Boolean, default=True)
    country = Column(String(50), default='Spain')
    
    # Optional, check when populating form:
    fixed_salary = Column(Numeric(10, 2))
    from_profit = Column(Numeric(10, 2))
    from_turnover = Column(Numeric(10, 2))
    fixed_perpiece = Column(Numeric(10, 2))
    bank_name = Column(String(50))
    iban = Column(String(50))
    swift = Column(String(50))
    bank_address = Column(String(50))
    bank_postcode = Column(String(50))
    bank_city = Column(String(50))
    bank_state = Column(String(50))
    bank_country = Column(String(50))
    bank_routing = Column(String(50))

    __table_args__ = (
        CheckConstraint('fiscal_number != ""', name='no_empty_fiscal_number'), 
        CheckConstraint('fiscal_name != ""', name='no_empty_fiscal_name'), 
        CheckConstraint('email != ""', name='no_empty_email'), 
        CheckConstraint('phone != ""', name='no_empty_phone')
    )
    

class AgentDocument(Base):
    __tablename__ = 'agent_documents'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    name = Column(String(50), unique=True)
    document = Column(LargeBinary(length=(2**32)-1))

    agent = relationship('Agent', backref=backref('documents'))
    
# Partners:
class Partner(Base):
    __tablename__ = 'partners'
    
    id = Column(Integer, primary_key=True)
    fiscal_number = Column(String(50), nullable=False)
    fiscal_name = Column(String(50), nullable=False)
    trading_name = Column(String(50), nullable=False, unique=True)
    warranty = Column(Integer, default=0)
    note = Column(String(255))
    amount_credit_limit = Column(Numeric(10, 2), default=0)
    days_credit_limit = Column(Integer, default=0)
    
    agent_id = Column(Integer, ForeignKey('agents.id')) 

    they_pay_they_ship = Column(Boolean, default=False, nullable=False)
    they_pay_we_ship = Column(Boolean, default=False, nullable=False)
    we_pay_they_ship = Column(Boolean, default=False, nullable=False)
    we_pay_we_ship = Column(Boolean, default=False, nullable=False)

    euro = Column(Boolean, default=True)
    
    active = Column(Boolean, default=True)
    
    isp = Column(Boolean, default=False)
    re = Column(Boolean, default=False)

    # Addresses:
    shipping_line1 = Column(String(50))
    shipping_line2 = Column(String(50))
    shipping_line3 = Column(String(50))
    
    shipping_city = Column(String(50))
    shipping_state = Column(String(50))
    shipping_country = Column(String(50))
    shipping_postcode = Column(String(50))

    billing_line1 = Column(String(50))
    billing_line2 = Column(String(50))
    billing_line3 = Column(String(50))

    billing_city = Column(String(50))
    billing_state = Column(String(50))
    billing_country = Column(String(50))
    billing_postcode = Column(String(50))

    agent = relationship('Agent', uselist=False)

    __table_args__ = (
        CheckConstraint('fiscal_name != ""', name='no_empty_partner_fiscal_name'), 
        CheckConstraint('fiscal_number != ""', name='no_empty_partner_fiscal_number'), 
        CheckConstraint('trading_name != ""', name='no_empty_partner_trading_name')
    )

class PartnerDocument(Base):
    __tablename__ = 'partner_documents'
    
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'))
    name = Column(String(50), unique=True)
    document = Column(LargeBinary(length=(2**32)-1))

    partner = relationship('Partner', backref=backref('documents'))

class PartnerContact(Base):
    __tablename__ = 'partner_contacts'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'))
    name = Column(String(50))
    position = Column(String(50))
    phone = Column(String(50))
    email = Column(String(50))
    note = Column(String(50))

    preferred = Column(Boolean, default=True)
 
    partner = relationship('Partner', backref=backref('contacts', cascade='delete-orphan, \
        delete, save-update'))
        
    def __init__(self, name, position, phone, email, note=None):
        self.name = name
        self.position = position
        self.phone = phone
        self.email = email
        self.note = note
        

    __table_args__ = (
        CheckConstraint("name != ''", name='no_empty_contact_name'), 
        CheckConstraint("position != ''", name='no_empty_position'), 
        CheckConstraint("email != ''", name='no_empty_contact_email')
    )


class PurchaseProforma(Base):

    __tablename__ = 'purchase_proformas'
    
    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger, nullable=False)
    number = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.now)
    date = Column(Date, nullable=False)
    warranty = Column(Integer, default=0)
    eta = Column(Date, nullable=False) 

    cancelled = Column(Boolean, nullable=False, default=False)
    sent = Column(Boolean, nullable=False, default=False) 
    note = Column(String(255))
    mixed = Column(Boolean, nullable=False, default=False)

    eur_currency = Column(Boolean, nullable=False, default=True)

    they_pay_they_ship = Column(Boolean, default=False, nullable=False)
    we_pay_they_ship = Column(Boolean, default=False, nullable=False)
    we_pay_we_ship = Column(Boolean, default=False, nullable=False)

    partner_id = Column(Integer, ForeignKey('partners.id'))
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'))
    invoice_id = Column(Integer, ForeignKey('purchase_invoices.id'))

    invoice = relationship('PurchaseInvoice', uselist=False)
    partner = relationship('Partner', uselist=False) 
    courier = relationship('Courier', uselist=False)
    warehouse = relationship('Warehouse', uselist=False)
    agent = relationship('Agent', uselist=False)
    order = relationship('PurchaseOrder', uselist=False, back_populates='proforma') 

    tracking = Column(String(50))
    external = Column(String(50))

    credit_amount = Column(Numeric(10, 2), nullable=False, default=0)
    credit_days = Column(Integer, default=0, nullable=False) 

    incoterm = Column(String(3), nullable=False)

    __table_args__ = (
        UniqueConstraint('type', 'number'), 
    )


class PurchaseProformaLine(Base):

    __tablename__ = 'purchase_proforma_lines'
    
    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id')) 
    item_id = Column(Integer, ForeignKey('items.id'))
    condition = Column(String(50), nullable=False)
    specification = Column(String(50), nullable=False)

    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    tax = Column(Integer, nullable=False)

    item = relationship('Item', uselist=False)
    proforma = relationship('PurchaseProforma', backref=backref('lines'))

    def __init__(self, item, condition, specification, price, quantity, tax):
        self.quantity = quantity
        self.price = price 
        self.item = item 
        self.condition = condition
        self.tax = tax 
        self.specification = specification


class MixedPurchaseLine(Base):

    __tablename__ = 'mixed_purchase_lines'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))
    description = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)
    specification = Column(String(50), nullable=False)

    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    tax = Column(Integer, nullable=False)

    proforma = relationship('PurchaseProforma', backref=backref('mixed_lines'))

    def __init__(self, description, condition, specification, quantity, price, tax):
        self.quantity = quantity
        self.price = price 
        self.description = description 
        self.condition = condition
        self.tax = tax 
        self.specification = specification


class PurchaseDocument(Base):
    
    __tablename__ = 'purchase_documents'

    id = Column(Integer, primary_key=True) 
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))
    name = Column(String(50), nullable=False)
    document = Column(LargeBinary(length=(2**32)-1))

    proforma = relationship('PurchaseProforma', backref=backref('documents')) 


    __table_args__ = (
        UniqueConstraint('proforma_id', 'name', name='unique_document_name'), 
    )

class PurchaseInvoice(Base):
    __tablename__ = 'purchase_invoices'
    
    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False) 
    

    def __init__(self, type, number):
        self.type = type
        self.number = number 

    __table_args__ = (
        UniqueConstraint('type', 'number'), 
    )

class PurchasePayment(Base):

    __tablename__ = 'purchase_payments'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'), index=True)

    date = Column(Date)
    amount = Column(Numeric(10, 2))
    note = Column(String(255))
    
    proforma = relationship('PurchaseProforma', backref=backref('payments'))

    def __init__(self, date, amount, note, proforma):
        self.date = date 
        self.amount = amount
        self.note = note 
        self.proforma = proforma


class PurchaseExpense(Base):

    __tablename__ = 'purchase_expenses'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))

    date = Column(Date)
    amount = Column(Numeric(10, 2))
    note = Column(String(255))

    proforma = relationship('PurchaseProforma', backref=backref('expenses'))

    def __init__(self, date, amount, note, proforma):
        self.date = date 
        self.amount = amount
        self.note = note 
        self.proforma = proforma


class SaleProforma(Base):
    
    __tablename__ = 'sale_proformas'
    
    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger)
    number = Column(Integer)
    created_on = Column(DateTime, default=datetime.now)
 
    normal = Column(Boolean, nullable=False, default=True)

    date = Column(Date, nullable=False)
    warranty = Column(Integer, nullable=False, default=0)

    cancelled = Column(Boolean, nullable=False, default=False)
    sent = Column(Boolean, nullable=False, default=False)
    note = Column(String(255))

    eur_currency = Column(Boolean, nullable=False, default=True)

    they_pay_they_ship = Column(Boolean, default=False, nullable=False)
    they_pay_we_ship = Column(Boolean, default=False, nullable=False)
    we_pay_we_ship = Column(Boolean, default=False, nullable=False)


    partner_id = Column(Integer, ForeignKey('partners.id'))
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'))
    sale_invoice_id = Column(Integer, ForeignKey('sale_invoices.id'))
    # sale_order_id = Column(Integer, ForeignKey('sale_orders.id'))

    
    credit_amount = Column(Numeric(10, 2), nullable=False, default=0)
    credit_days = Column(Integer, nullable=False, default=0)
    tracking = Column(String(50))
    external = Column(String(50))

    partner = relationship('Partner', uselist=False) 
    courier = relationship('Courier', uselist=False)
    warehouse = relationship('Warehouse', uselist=False)
    agent = relationship('Agent', uselist=False)
    invoice = relationship('SaleInvoice', uselist=False)
    order = relationship('SaleOrder', uselist=False, back_populates='proforma')


    incoterm = Column(String(3), nullable=False) 

    __table_args__ = (

        UniqueConstraint('type', 'number'), 
    )


class SalePayment(Base):
    __tablename__ = 'sale_payments'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))

    date = Column(Date)
    amount = Column(Numeric(10, 2))
    note = Column(String(255))
    
    def __init__(self, date, amount, note, proforma):
        self.date = date 
        self.amount = amount
        self.note = note 
        self.proforma = proforma

    proforma = relationship('SaleProforma', backref=backref('payments'))
    
class SaleExpense(Base):
    __tablename__ = 'sale_expenses'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))

    date = Column(Date)
    amount = Column(Numeric(10, 2))
    note = Column(String(255))

    def __init__(self, date, amount, note, proforma):
        self.date = date 
        self.amount = amount
        self.note = note 
        self.proforma = proforma

    proforma = relationship('SaleProforma', backref=backref('expenses'))

class SaleDocument(Base):
    
    __tablename__ = 'sale_documents'
    
    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))
    name = Column(String(50), nullable=False)
    document = Column(LargeBinary(length=(2**32)-1))
    
    __table_args__ = (
        UniqueConstraint('proforma_id', 'name', name='unique_document_name'), 
    )


    proforma = relationship('SaleProforma', backref=backref('documents'))

class SaleInvoice(Base):

    __tablename__ = 'sale_invoices'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False) 
    number = Column(Integer, nullable=False) 


    def __init__(self, type, number):
        self.type = type
        self.number = number 


    __table_args__ = (
        UniqueConstraint('type', 'number', name='unique_sales_sale_invoices'), 
    )


class SaleProformaLine(Base):

    __tablename__ = 'sale_proforma_lines'

    id = Column(Integer, primary_key=True) 
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'), nullable=False)

    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    mixed_group_id = Column(Integer, nullable=True)
    
    condition = Column(String(50), nullable=False)
    showing_condition = Column(String(50), nullable=True)
    specification = Column(String(50), nullable=False)
    ignore_specification = Column(Boolean, nullable=False) 
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    tax = Column(Integer, nullable=False)

    item = relationship('Item', uselist=False)
    proforma = relationship('SaleProforma', backref=backref('lines'))
    

    eta = Column(Date, nullable=True) 

    __table_args__ = (
        UniqueConstraint('id', 'proforma_id'), 
    )


    def __init__(self, item, condition, specification,
        ignore, price, quantity, tax, showing_condition=None, eta=None):
        self.quantity = quantity
        self.price = price 
        self.item = item 
        self.condition = condition
        self.tax = tax 
        self.specification = specification
        self.eta = eta
        self.ignore_specification = ignore
        self.showing_condition = showing_condition


    # An alternative constructor: 
    @classmethod
    def from_stock(cls, ser, ignore, price, tax):
        # ser stands for StockEntryRequest, is a pair relating 
        # a stock entry with a quantity requested . Defined as a named tuple
        
        return cls(ser.item_object, ser.stock_entry.condition, \
            ser.stock_entry.specification , ignore, price, ser.requested_quantity, tax)

class SaleOrder(Base):
    
    __tablename__ = 'sale_orders'
     
    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'), nullable=False)
    note = Column(String(50))
    created_on = Column(DateTime, default=datetime.now)

    def __init__(self, proforma, note):
        self.proforma = proforma 
        self.note = note 

    proforma = relationship('SaleProforma', back_populates='order')

    __table_args__ = (
        UniqueConstraint('proforma_id', name='sale_order_from_onlyone_proforma'), 
    )

class SaleOrderLine(Base):
    __tablename__ = 'sale_order_lines'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('sale_orders.id'))
    
    item_id = Column(Integer, ForeignKey('items.id'))
    condition = Column(String(50))
    specification = Column(String(50))
    quantity = Column(Integer)

    item = relationship('Item', uselist=False)
    order = relationship('SaleOrder', backref=backref('lines'))

    def __init__(self, order, item, condition, specification, quantity):
        self.order = order
        self.item = item
        self.condition = condition
        self.specification = specification
        self.quantity = quantity

    __table_args__ = (
        UniqueConstraint('id', 'order_id'), 
    )

class PurchaseOrder(Base):

    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'), nullable=False)
    note = Column(String(50))
    created_on = Column(DateTime, default=datetime.now)

    proforma = relationship('PurchaseProforma', back_populates='order')

    def __init__(self, proforma, note ):
        self.proforma = proforma 
        self.note = note 

    __table_args__ = (
        UniqueConstraint('proforma_id', name='purchase_order_from_onlyone_proforma'),
    )

class PurchaseOrderLine(Base):

    __tablename__ = 'purchase_order_lines'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('purchase_orders.id'))
    
    item_id = Column(Integer, ForeignKey('items.id'))
    condition = Column(String(50))
    specification = Column(String(50))
    quantity = Column(Integer)

    order = relationship('PurchaseOrder', backref=backref('lines'))
    item = relationship('Item', uselist=False)


    def __init__(self, order, item, condition, specification, quantity):
        self.order = order
        self.item = item
        self.condition = condition
        self.specification = specification
        self.quantity = quantity


    __table_args__ = (
        UniqueConstraint('id', 'order_id'), 
    )


class MixedPurchaseOrderLine(Base):

    __tablename__ = 'mixed_purchase_order_lines'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('purchase_orders.id'))

    description = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)
    specification = Column(String(50), nullable=False)

    quantity = Column(Integer, nullable=False)

    order = relationship('PurchaseOrder', backref=backref('mixed_lines'))

    def __init__(self, order, description, condition, specification, quantity):
        self.order = order 
        self.description = description
        self.condition = condition
        self.specification = specification
        self.quantity = quantity


class MixedPurchaseSerie(Base):

    __tablename__ = 'mixed_purchase_series'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    line_id = Column(Integer, ForeignKey('mixed_purchase_order_lines.id'), nullable=False)
    sn = Column(String(50), nullable=False)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)

    item = relationship('Item', uselist=False)
    line = relationship('MixedPurchaseOrderLine', backref=backref('series'))

    def __init__(self, item_id, line_id, sn, condition, spec):
        self.item_id = item_id
        self.line_id = line_id
        self.sn = sn 
        self.condition = condition
        self.spec = spec


class PurchaseSerie(Base):
    __tablename__ = 'purchase_series'
    
    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey('purchase_order_lines.id'))
    serie = Column(String(50))

    line = relationship('PurchaseOrderLine', backref=backref('series'))

    __table_args__ = (
        UniqueConstraint('id', 'line_id', 'serie'), 
    )

class SaleSerie(Base):
    __tablename__ = 'sale_series'

    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey('sale_order_lines.id'))
    serie = Column(String(50), nullable=False)

    line = relationship('SaleOrderLine', backref=backref('series')) 

    __table_args__ = (
        UniqueConstraint('id', 'line_id', 'serie'), 
    )

class Imei(Base):

    __tablename__ = 'imeis'

    imei = Column(String(50), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50))
    specification = Column(String(50))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))

    item = relationship('Item', uselist=False) 
    warehouse = relationship('Warehouse', uselist=False) 

class EagerImeiOutput(Base):
    
    __tablename__ = 'eager_outputs'

    imei = Column(String(50), primary_key=True)

    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50))
    specification = Column(String(50))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))


    item = relationship('Item', uselist=False) 
    warehouse = relationship('Warehouse', uselist=False) 


def create_and_populate(): 

    import sys

    if sys.platform == 'win32':
        testpath = r'.\app\SalesInvoice_LWI003703.pdf'
    elif sys.platform == 'darwin':
        testpath = r'./app/SalesInvoice_LWI003703.pdf'
    else:
        print('I dont know in which platform I am')
        sys.exit() 

    Base.metadata.create_all(engine)

    session = Session() 

    agent = Agent() 

    agent.fiscal_name = 'Andrei Enache'
    agent.fiscal_number = 'X4946057E'
    agent.email = 'andrei.officee@gmail.com'
    agent.phone = '604178304'
    agent.country = 'Spain'
    agent.active = True

    partner = Partner()

    partner.fiscal_name = 'Euromedia Investment Group, S.L.'
    partner.fiscal_number = 'B98815608'
    partner.trading_name = 'Euromedia'
    partner.billing_country = 'Spain'
    partner.agent = agent

    contact1 = PartnerContact('Angel Mirchev', 'CEO', '673567274', \
        'angel.bn@euromediagroup.com', 'Boss of the people')
    
    contact2 = PartnerContact('Tihomir Damyianov', 'Sales Manager', '772342343',\
        'tihomir.dv@euromediagroup.com', 'The boss of the salesman')


    partner.contacts.extend([contact1, contact2])

    partner.agent = agent
    partner.we_pay_they_ship = True
    partner.days_credit_limit = 30 
    partner.amount_credit_limit = 10000

    session.add(partner)
    session.add(agent)


    from utils import base64Pdf 

    ad1 = AgentDocument()
    ad1.name = 'NIE'
    ad1.document = base64Pdf(testpath) 
    ad1.agent = agent

    ad2 = AgentDocument()
    ad2.name = 'Passport'
    ad2.document = base64Pdf(testpath)
    ad2.agent = agent


    pd = PartnerDocument()
    pd.name = 'TAF'
    pd.document = base64Pdf(testpath)
    pd.partner = partner

    session.add(ad1)
    session.add(ad2)
    session.add(pd)

    a = Agent()
    a.fiscal_name = 'Raimundo Lopez'
    a.fiscal_number = 'X34234234'
    a.active = False
    a.country = 'Spain'
    a.email = 'aasdasdnwe@fas.com'
    a.phone = '7723324324'


    item1 = Item('Apple', 'Iphone', 'X', 128, 'Black')
    item2 = Item('Samnsung', 'Galaxy', 'Lite', 256, 'Red')
    item3 = Item('Apple', 'Iphone', 'X', 128, 'Red')
    item4 = Item('Apple', 'Iphone', 'X', 128, 'Yellow')
    item5 = Item('Apple', 'Iphone', 'X', 128, 'Purple')


    session.add(item1)
    session.add(item2)
    session.add(item3)
    session.add(item4)
    session.add(item5)

    session.add(a)

    w = Warehouse('Free Sale')
    session.add_all([Warehouse('Drebno'), w, Warehouse('Trash')])

    session.add_all([Courier('DHL'), Courier('MRV'), Courier('Fedex')])
    
    proforma = PurchaseProforma() 
    proforma.type = 1
    proforma.number = 1
    proforma.date = datetime(2020, 10, 11)
    proforma.warranty = 100
    from datetime import timedelta
    proforma.eta = proforma.date + timedelta(days=5) 
    proforma.partner = partner
    proforma.agent = agent
    proforma.warehouse = Warehouse('WarehouseB')
    proforma.courier = Courier('USP')
    proforma.eur_currency = True
    proforma.incoterm = 'FOB'


    proforma.lines = [
        PurchaseProformaLine(item1, 'NEW', 'EEUU', 100.0, 10, 21), 
        PurchaseProformaLine(item2, 'USED', 'FRANCE', 500, 10, 21)
    ]

    session.add(proforma) 

    pd = PurchaseDocument() 
    pd.name = 'customs'
    pd.document = base64Pdf(testpath)
    pd.proforma = proforma

    session.add(pd)

    from datetime import date
    pp1 = PurchasePayment(date.today(), 5000, 'Caixa / 33423', proforma) 
    pp2 = PurchasePayment(date.today() + timedelta(days=2), 200, 'Santander / 23423', proforma) 

    session.add(pp1)
    session.add(pp2)


    proforma = PurchaseProforma() 
    proforma.type = 1
    proforma.number = 2
    proforma.date = datetime(2020, 10, 11)
    proforma.warranty = 100
    from datetime import timedelta
    proforma.eta = proforma.date + timedelta(days=5) 
    proforma.partner = partner
    proforma.agent = agent
    proforma.warehouse = w
    proforma.courier = Courier('XXX')
    proforma.eur_currency = True
    proforma.incoterm = 'FOB'


    proforma.lines = [
        PurchaseProformaLine(item2, 'A+/B', 'JAPAN', 100.0, 10, 21), 
        PurchaseProformaLine(item1, 'A+', 'JAPAN', 500, 10, 21)
    ]

    session.add(proforma) 

    pay = PurchasePayment(date.today(), 112, 'santander', proforma)

    session.add(pay) 

    session.commit() 

def create_sale(type):
    
    proforma = SaleProforma() 
    proforma.type = type
    number = session.query(func.max(SaleProforma.number)).where(SaleProforma.type == type).scalar()
    
    proforma.number = 1 if not number else number + 1 
    proforma.date = datetime(2020, 10, 11)
    proforma.warranty = 100
    from datetime import timedelta
    proforma.eta = proforma.date + timedelta(days=5) 
    proforma.partner = session.query(Partner).first() 
    proforma.agent = session.query(Agent).first() 
    proforma.warehouse = session.query(Warehouse).where(Warehouse.id == 4).one() 
    proforma.courier = session.query(Courier).first()
    proforma.eur_currency = True
    proforma.incoterm = 'FOB'

    proforma.sent = False
    proforma.cancelled = False

    proforma.lines = [
        SaleProformaLine(session.query(Item)[-1] , 'USED', 'FRANCE', 100.0, 1, 21, datetime(2020, 10, 11) + timedelta(days=5)), 
        # SaleProformaLine(session.query(Item).first(), 'A+', 'JAPAN', 500, 5, 21, datetime(2020, 10, 11) + timedelta(days=5))
    ]
    
    session.add(proforma)

    session.commit() 

def create_imeis():
    
    item1 = session.query(Item)[0]
    item2 = session.query(Item)[-1]

    w = session.query(Warehouse).where(Warehouse.description == 'Free Sale').one() 

    imei = Imei() 
    imei.condition = 'NEW'
    imei.specification = 'EEUU'
    imei.warehouse = w
    imei.item = item1
    imei.imei = '234551234512ZXC DFSSCD5'

    session.add(imei) 

    imei = Imei() 
    imei.condition = 'NEW'
    imei.specification = 'EEUU'
    imei.warehouse = w
    imei.item = item2
    imei.imei = '2345562345DFVCZ 45'

    session.add(imei) 

    imei = Imei() 
    imei.condition = 'NEW'
    imei.specification = 'FRANCE'
    imei.warehouse = w
    imei.item = item1
    imei.imei = '23455623XCZXDs2345'

    session.add(imei)

    imei = Imei() 
    imei.condition = 'USED'
    imei.specification = 'EEUU'
    imei.warehouse = w
    imei.item = item2
    imei.imei = '2345562CVFpl2345'

    session.add(imei) 

    session.commit()


@event.listens_for(PurchaseSerie, 'after_insert')
def insert_imei_after_purchase(mapper, connection, target):
    stmt = insert(Imei).values(
        imei = target.serie, 
        item_id = target.line.item_id, 
        condition = target.line.condition, 
        specification = target.line.specification, 
        warehouse_id = target.line.order.proforma.warehouse.id
    )
    connection.execute(stmt)


from exceptions import NotExistingStockOutput


@event.listens_for(PurchaseSerie, 'after_delete')
def delete_imei_after_purchase(mapper, connection, target):
    condition = target.line.condition 
    specification = target.line.specification 
    stmt = delete(Imei).where(Imei.imei == target.serie).where(Imei.condition == condition).\
        where(Imei.specification == specification)
    result = connection.execute(stmt) 
    if not result.rowcount:
        raise NotExistingStockOutput
    

@event.listens_for(SaleSerie, 'after_insert')
def delete_imei_after_sale(mapper, connection, target:SaleSerie):
    condition = target.line.condition 
    specification = target.line.specification 
    stmt = delete(Imei).where(Imei.imei == target.serie).where(Imei.condition == condition).\
        where(Imei.specification == specification)
    print(stmt)
    result = connection.execute(stmt) 
    if not result.rowcount:
        raise NotExistingStockOutput


@event.listens_for(SaleSerie, 'after_delete')
def insert_imei_after_sale(mapper, connection, target):
    stmt = insert(Imei).values(
        imei = target.serie, 
        item_id = target.line.item_id, 
        condition = target.line.condition, 
        specification = target.line.specification, 
        warehouse_id = target.line.order.proforma.warehouse.id
    )
    
    connection.execute(stmt)

class SpecificationChange(Base):

    __tablename__ = 'specification_changes'

    id = Column(Integer, primary_key=True) 
    sn = Column(String(50), nullable=False) 
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.now)

class WarehouseChange(Base):

    __tablename__ = 'warehouse_changes'

    id = Column(Integer, primary_key=True)
    sn = Column(String(50), nullable=False) 
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.now)    


class ConditionChange(Base):

    __tablename__ = 'condition_changes'

    id = Column(Integer, primary_key=True)
    sn = Column(String(50), nullable=False) 
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.now) 


# Patch to ser objects 
# Bad practice, no time for better solution 
if __name__ == '__main__':
    

    create_and_populate() 
