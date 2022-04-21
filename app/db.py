from sqlalchemy import create_engine, event, insert, update, delete
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

import sys
import os
import math

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, UniqueConstraint, SmallInteger, Boolean, LargeBinary,
    Date, CheckConstraint, Float
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import functools
import operator

from sqlalchemy.sql.operators import exists

engine = create_engine('mysql+mysqlconnector://andrei:hnq#4506@192.168.2.253:3306/appdb', echo=False)
dev_engine = create_engine('mysql+mysqlconnector://root:hnq#4506@localhost:3306/appdb', echo=False)

# from sale types:

NORMAL, FAST, DEFINED = 0, 1, 2


def get_engine():
    try:
        debug = os.environ['APP_DEBUG'] == 'TRUE'
        if debug:
            print('Debug Mode')
        else:
            print('Production Mode')

        return dev_engine if debug else engine
    except KeyError:
        print('SET APP_DEBUG VARIABLE')
        sys.exit()


Session = scoped_session(sessionmaker(bind=get_engine(), autoflush=False))
session = Session()

Base = declarative_base()


class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description

    def __eq__(self, other):
        if type(other) is Warehouse:
            return self.description == other.description
        elif type(other) is str:
            return self.description == other


class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description


class Spec(Base):
    __tablename__ = 'specs'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description

    def __eq__(self, other):
        if type(other) is Spec:
            return self.description == other.description
        elif type(other) is str:
            return self.description == other

    def __repr__(self):
        clsname = self.__class__.__name__
        return f"{clsname}(description='{self.description}')"


class Condition(Base):
    __tablename__ = 'conditions'

    id = Column(Integer, primary_key=True)

    description = Column(String(50), nullable=False, unique=True)

    def __init__(self, description):
        self.description = description

    def __eq__(self, other):
        if type(other) is Condition:
            return self.description == other.description
        elif type(other) is str:
            return self.description == other


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    mpn = Column(String(50))
    manufacturer = Column(String(50))
    category = Column(String(50))
    model = Column(String(50))
    capacity = Column(String(50))
    color = Column(String(50))
    has_serie = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('mpn', 'manufacturer', 'category', 'model', 'capacity', 'color', name='uix_1'),
    )

    def __init__(self, mpn, manufacturer, category, model, capacity, color,
                 has_serie):
        self.mpn = mpn.strip()
        self.manufacturer = manufacturer.strip()
        self.category = category.strip()
        self.model = model.strip()
        self.capacity = capacity.strip()
        self.color = color.strip()
        self.has_serie = has_serie

    @property
    def clean_repr(self):
        repr = ''

        if self.mpn: repr += self.mpn + ' '
        repr += self.manufacturer + ' '
        repr += self.category + ' '
        repr += self.model

        if self.capacity:
            repr += ' ' + self.capacity + ' GB'
        if self.color:
            repr += ' ' + self.color

        return repr

        # repr = self.dirty_repr[:-1] # remove y or n 
        # return ' '.join(repr.replace('|', ' ').replace('?', '').strip().split()) 

    @property
    def dirty_repr(self):
        # A special char ? for absence, and | for separation
        return '|'.join(
            [
                self.mpn or '?',
                self.manufacturer or '?',
                self.category or '?',
                self.model or '?',
                self.capacity or '?',
                self.color or '?',
                'y' if self.has_serie else 'n'
            ]
        )


# Agents:
class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    fiscal_number = Column(String(50))
    fiscal_name = Column(String(50), unique=True)  # To differentiate
    email = Column(String(50))
    phone = Column(String(60))
    active = Column(Boolean, default=True)
    country = Column(String(50), default='Spain')
    created_on = Column(DateTime, default=datetime.now)

    # Optional, check when populating form:

    fixed_salary = Column(Float(precision=32, decimal_return_scale=None), default=1.0, nullable=False)
    from_profit = Column(Float(precision=32, decimal_return_scale=None), default=1.0, nullable=False)
    from_turnover = Column(Float(precision=32, decimal_return_scale=None), default=1.0, nullable=False)
    fixed_perpiece = Column(Float(precision=32, decimal_return_scale=None), default=1.0, nullable=False)
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
    name = Column(String(50))
    document = Column(LargeBinary(length=(2 ** 32) - 1))

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
    amount_credit_limit = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
    days_credit_limit = Column(Integer, default=0)

    created_on = Column(DateTime, default=datetime.now)
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

    accounts = relationship('PartnerAccount', backref='partner', cascade='delete-orphan, save-update, delete')

    __table_args__ = (
        CheckConstraint('fiscal_name != ""', name='no_empty_partner_fiscal_name'),
        CheckConstraint('fiscal_number != ""', name='no_empty_partner_fiscal_number'),
        CheckConstraint('trading_name != ""', name='no_empty_partner_trading_name')
    )

class PartnerDocument(Base):
    __tablename__ = 'partner_documents'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'))
    name = Column(String(50))
    document = Column(LargeBinary(length=(2 ** 32) - 1))
    created_on = Column(DateTime, default=datetime.now)
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


class PartnerAccount(Base):
    __tablename__ = 'partner_accounts'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'))
    bank_name = Column(String(50))
    iban = Column(String(50))
    swift = Column(String(50))
    bank_address = Column(String(50))
    bank_postcode = Column(String(50))
    bank_city = Column(String(50))
    bank_state = Column(String(50))
    bank_country = Column(String(50))
    bank_routing = Column(String(50))
    currency = Column(String(50), default='')

    def __init__(self, bank_name, iban, swift, bank_address,
                 bank_postcode, bank_city, bank_state, bank_country,
                 bank_routing, currency):
        self.bank_name = bank_name
        self.iban = iban
        self.swift = swift
        self.bank_address = bank_address
        self.bank_postcode = bank_postcode
        self.bank_city = bank_city
        self.bank_state = bank_state
        self.bank_country = bank_country
        self.bank_routing = bank_routing
        self.currency = currency


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
    note = Column(String(255), default='')

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
    reception = relationship('Reception', uselist=False, backref='proforma')

    tracking = Column(String(50))
    external = Column(String(50))

    credit_amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
    credit_days = Column(Integer, default=0, nullable=False)

    incoterm = Column(String(3), nullable=False)

    __table_args__ = (
        UniqueConstraint('type', 'number'),
    )

    @property
    def subtotal(self):
        return sum(line.price * line.quantity for line in self.lines)

    @property
    def tax(self):
        return sum(line.price * line.quantity * line.tax / 100 for line in self.lines)

    @property
    def total_debt(self):
        return self.subtotal + self.tax

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments)

    @property
    def not_paid(self):
        return math.isclose(self.total_paid, 0)

    @property
    def partially_paid(self):
        return 0 < self.total_paid < self.total_debt

    @property
    def fully_paid(self):
        return math.isclose(self.total_debt, self.total_paid)

    @property
    def overpaid(self):
        return 0 < self.total_debt < self.total_paid

    @property
    def total_quantity(self):
        import utils
        return sum(
            line.quantity for line in self.lines
            if line.item_id or line.description in utils.descriptions
        )

    @property
    def total_processed(self):
        try:
            return sum(
                1 for line in self.reception.lines for serie in line.series
            )
        except AttributeError:
            return 0

    @property
    def empty(self):
        return self.total_processed == 0

    @property
    def partially_processed(self):
        return 0 < self.total_processed < self.total_quantity

    @property
    def completed(self):
        return self.total_processed == self.total_quantity

    @property
    def overflowed(self):
        try:
            for line in self.reception.lines:
                if len(line.series) > line.quantity:
                    return True
        except AttributeError:
            return False
        return False


class PurchaseProformaLine(Base):
    __tablename__ = 'purchase_proforma_lines'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    description = Column(String(100), nullable=True)
    condition = Column(String(50), nullable=True)
    spec = Column(String(50), nullable=True)

    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float(precision=32, decimal_return_scale=None), default=1.0, nullable=False)
    tax = Column(Integer, nullable=False, default=0)

    item = relationship('Item', uselist=False)

    proforma = relationship(
        'PurchaseProforma',
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update'
        )
    )

    # This __eq__ method is a callback
    # For the set difference between reception lines 
    # and proforma purchase lines, in order to update the
    # receptions when they are already created and user 
    # wants the update proforma. 

    def __eq__(self, other):
        return all((
            other.item_id == self.item_id,
            other.description == self.description,
            other.condition == self.condition,
            other.spec == self.spec
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (
            self.item_id, self.description, self.spec,
            self.condition
        ))
        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(item_id={self.item_id}, description={self.description}, condition={self.condition}"
        s += f", spec={self.spec})"
        return s


class PurchaseDocument(Base):
    __tablename__ = 'purchase_documents'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))
    name = Column(String(50), nullable=False)
    document = Column(LargeBinary(length=(2 ** 32) - 1))

    proforma = relationship('PurchaseProforma', backref=backref('documents'))

    __table_args__ = (
        UniqueConstraint('proforma_id', 'name', name='unique_document_name'),
    )


class PurchaseInvoice(Base):
    __tablename__ = 'purchase_invoices'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(Date, default=datetime.now)
    eta = Column(Date, default=datetime.now)

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
    amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
    rate = Column(Float(precision=32, decimal_return_scale=None), default=0.0, nullable=False)
    note = Column(String(255))

    proforma = relationship('PurchaseProforma', backref=backref('payments'))

    def __init__(self, date, amount, rate, note, proforma):
        self.date = date
        self.amount = amount
        self.note = note
        self.rate = rate
        self.proforma = proforma


class PurchaseExpense(Base):
    __tablename__ = 'purchase_expenses'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'))

    date = Column(Date)
    amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
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

    date = Column(Date, default=datetime.now)
    warranty = Column(Integer, default=0)
    eta = Column(Date, default=datetime.now)

    cancelled = Column(Boolean, default=False)
    sent = Column(Boolean, default=False)
    note = Column(String(255), default='')

    eur_currency = Column(Boolean, default=True)

    they_pay_they_ship = Column(Boolean, default=False)
    they_pay_we_ship = Column(Boolean, default=False)
    we_pay_we_ship = Column(Boolean, default=False)

    partner_id = Column(Integer, ForeignKey('partners.id'))
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'))
    sale_invoice_id = Column(Integer, ForeignKey('sale_invoices.id'))

    credit_amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
    credit_days = Column(Integer, default=0)
    tracking = Column(String(50))
    external = Column(String(50))

    ready = Column(Boolean, nullable=False, default=False)

    partner = relationship('Partner', uselist=False)
    courier = relationship('Courier', uselist=False)
    warehouse = relationship('Warehouse', uselist=False)
    agent = relationship('Agent', uselist=False)
    invoice = relationship('SaleInvoice', uselist=False)
    expedition = relationship('Expedition', uselist=False, back_populates='proforma')

    warning = Column(String(50), nullable=True)

    incoterm = Column(String(3), default='gbc')

    def __repr__(self):
        clasname = self.__class__.__name__
        return f'{clasname}(type={self.type}, number={self.number})'

    __table_args__ = (
        UniqueConstraint('type', 'number'),
    )

    @property
    def subtotal(self):
        return sum(line.price * line.quantity for line in self.lines) or \
               sum(line.price * line.quantity for line in self.advanced_lines)

    @property
    def tax(self):
        return sum(line.price * line.quantity * line.tax / 100 for line in self.lines) or \
               sum(line.price * line.quantity * line.tax / 100 for line in self.advanced_lines)

    @property
    def total_debt(self):
        return self.subtotal + self.tax

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments)

    @property
    def not_paid(self):
        return math.isclose(self.total_paid, 0)

    @property
    def partially_paid(self):
        return 0 < self.total_paid < self.total_debt

    @property
    def fully_paid(self):
        return math.isclose(self.total_debt, self.total_paid)

    @property
    def overpaid(self):
        return 0 < self.total_debt < self.total_paid

    @property
    def total_quantity(self):
        return sum(line.quantity for line in self.lines if line.item_id) or \
            sum(line.quantity for line in self.advanced_lines if line.item_id)

    @property
    def total_processed(self):
        try:
            return sum(1 for line in self.expedition.lines for serie in line.series)
        except AttributeError:
            return 0

    @property
    def empty(self):
        return self.total_processed == 0

    @property
    def partially_processed(self):
        return 0 < self.total_processed < self.total_quantity

    @property
    def completed(self):
        return self.total_processed == self.total_quantity

    @property
    def overflowed(self):
        try:
            for line in self.expedition.lines:
                if len(line.series) > line.quantity:
                    return True
        except AttributeError:
            return False
        return False


class SalePayment(Base):
    __tablename__ = 'sale_payments'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))

    date = Column(Date)
    amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0, nullable=False)
    rate = Column(Float(precision=32, decimal_return_scale=None), default=0.0, nullable=False)

    note = Column(String(255))

    def __init__(self, date, amount, rate, note, proforma):
        self.date = date
        self.amount = amount
        self.rate = rate
        self.note = note
        self.proforma = proforma

    proforma = relationship('SaleProforma', backref=backref('payments'))


class SaleExpense(Base):
    __tablename__ = 'sale_expenses'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))

    date = Column(Date)
    amount = Column(Float(precision=32, decimal_return_scale=None), default=0.0, nullable=False)
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
    document = Column(LargeBinary(length=(2 ** 32) - 1))

    __table_args__ = (
        UniqueConstraint('proforma_id', 'name', name='unique_document_name'),
    )

    proforma = relationship('SaleProforma', backref=backref('documents'))


class SaleInvoice(Base):
    __tablename__ = 'sale_invoices'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(Date, default=datetime.now)
    eta = Column(Date, default=datetime.now)

    def __repr__(self):
        clasname = self.__class__.__name__
        return f'{clasname}(type={self.type}, number={self.number})'

    def __init__(self, type, number):
        self.type = type
        self.number = number

    __table_args__ = (
        UniqueConstraint('type', 'number', name='unique_sales_sale_invoices'),
    )


class SaleProformaLine(Base):
    __tablename__ = 'sale_proforma_lines'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))

    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    mix_id = Column(String(36), nullable=True)

    # No stock related line 
    description = Column(String(100))

    condition = Column(String(50))
    showing_condition = Column(String(50))
    spec = Column(String(50))
    ignore_spec = Column(Boolean, default=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float(precision=32, decimal_return_scale=None), default=0.0, nullable=False)
    tax = Column(Integer, default=0, nullable=False)

    item = relationship('Item')
    proforma = relationship(
        'SaleProforma',
        backref=backref('lines',
                        cascade='delete-orphan, delete, save-update',
                        # lazy = 'joined'
                        )
    )
    # options lazyjoined to the query 
    __table_args__ = (
        UniqueConstraint('id', 'proforma_id'),
    )

    def __eq__(self, other):
        description = False
        if hasattr(other, 'description') and hasattr(self, 'description'):
            description = other.description == self.description

        return all((
            other.item_id == self.item_id,
            other.condition == self.condition,
            other.spec == self.spec,
        )) and description

    def __hash__(self):
        hashes = (hash(x) for x in (
            self.item_id, self.spec, self.condition, self.description)
                  )
        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}(item_id={self.item_id}, condition={self.condition}, spec={self.spec},mix_id={self.mix_id}, quantity={self.quantity})"


# @event.listens_for(session, 'transient_to_pending')
# def object_is_pending(session, object):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print('new pending %s' %object)

# @event.listens_for(Base, "init", propagate=True)
# def intercept_init(instance, args, kwargs):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("new transient: %s" % instance)

# @event.listens_for(session, "pending_to_persistent")
# def intercept_pending_to_persistent(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("pending to persistent: %s" % object_)


# @event.listens_for(session, "pending_to_transient")
# def intercept_pending_to_transient(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("transient to pending: %s" % object_)

# @event.listens_for(session, "loaded_as_persistent")
# def intercept_loaded_as_persistent(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("object loaded into persistent state: %s" % object_)

# @event.listens_for(session, "persistent_to_deleted")
# def intercept_persistent_to_deleted(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("object was DELETEd, is now in deleted state: %s" % object_)

# @event.listens_for(session, "deleted_to_detached")
# def intercept_deleted_to_detached(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("deleted to detached: %s" % object_)

# @event.listens_for(session, "persistent_to_detached")
# def intercept_persistent_to_detached(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("object became detached: %s" % object_)


# @event.listens_for(session, "detached_to_persistent")
# def intercept_detached_to_persistent(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("object became persistent again: %s" % object_)

# @event.listens_for(session, "deleted_to_persistent")
# def intercept_deleted_to_persistent(session, object_):
#     if type(object) in (SaleProforma, SaleProformaLine, AdvancedLine, AdvancedLineDefinition):
#         print("deleted to persistent: %s" % object_)


class AdvancedLine(Base):

    __tablename__ = 'advanced_lines'

    id = Column(Integer, primary_key=True)
    origin_id = Column(Integer, nullable=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    mixed_description = Column(String(50))
    free_description = Column(String(50))
    condition = Column(String(50))
    spec = Column(String(50))
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float(precision=32, decimal_return_scale=None), default=0.0)
    tax = Column(Integer, nullable=False, default=0)
    ignore_spec = Column(Boolean, default=True, nullable=False)
    showing_condition = Column(String(50), nullable=True)

    def __eq__(self, other):
        return all((
            self.mixed_description == other.description,
            self.item_id == other.item_id,
            self.condition == other.condition,
            self.spec == other.spec,
            self.origin_id == other.origin_id
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (
            self.mixed_description, self.item_id, self.condition,
            self.spec, self.origin_id
        ))

        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(id={self.id}, origin_id={self.origin_id}, proforma_id={self.proforma_id}, "
        s += f"item_id={self.item_id}, mixed_description={self.mixed_description}, "
        s += f"condition={self.condition}, spec={self.spec}, quantity={self.quantity})"
        return s

    proforma = relationship(
        'SaleProforma',
        backref=backref(
            'advanced_lines',
            cascade='delete-orphan, delete, save-update',
            # lazy = 'joined'
        )
    )

    definitions = relationship('AdvancedLineDefinition', backref='line',
                               cascade='delete-orphan, save-update, delete')


class AdvancedLineDefinition(Base):
    __tablename__ = 'advanced_lines_definition'

    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey('advanced_lines.id'))
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)
    quantity = Column(Integer, default=0)

    showing_condition = Column(String(50), nullable=True)

    local_count_relevant = Column(Boolean, default=True)
    global_count_relevant = Column(Boolean, default=False)

    item = relationship('Item', uselist=False)

    def __init__(self, item_id, condition, spec, quantity, showing_condition):
        self.item_id = item_id
        self.condition = condition
        self.spec = spec
        self.quantity = quantity
        self.showing_condition = showing_condition

    def __bool__(self):
        return all((self.item_id, self.spec, self.condition))

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(item_id={self.item_id}, condition={self.condition}"
        s += f", spec={self.spec}, quantity={self.quantity})"
        return s

        return repr(self.__dict__)


class Expedition(Base):
    __tablename__ = 'expeditions'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'), nullable=False)
    created_on = Column(DateTime, default=datetime.now)
    from_sale_type = Column(Integer, nullable=False)

    def __init__(self, proforma, from_sale_type=NORMAL):
        self.proforma = proforma
        self.from_sale_type = from_sale_type

    proforma = relationship('SaleProforma', back_populates='expedition')

    __table_args__ = (
        UniqueConstraint('proforma_id', name='sale_expedition_from_onlyone_proforma'),
    )


class ExpeditionLine(Base):
    __tablename__ = 'expedition_lines'

    id = Column(Integer, primary_key=True)
    expedition_id = Column(Integer, ForeignKey('expeditions.id'))

    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)
    showing_condition = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False)

    item = relationship('Item', uselist=False)
    expedition = relationship('Expedition', backref=backref('lines'))

    # Compatible with saleProformaLINE
    # Enable set operations

    # Remember operation with sale proforma line:
    def __eq__(self, other):
        return all((
            other.item_id == self.item_id,
            other.condition == self.condition,
            other.spec == self.spec,
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (self.item_id, self.spec, self.condition, None))
        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}(item_id={self.item_id}, condition={self.condition}, spec={self.spec})"

    __table_args__ = (
        UniqueConstraint('id', 'expedition_id'),
    )


class Reception(Base):
    __tablename__ = 'receptions'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('purchase_proformas.id'),
                         nullable=False, unique=True)
    note = Column(String(50))
    created_on = Column(DateTime, default=datetime.now)

    def __init__(self, proforma, note):
        self.proforma = proforma
        self.note = note

    __table_args__ = (
        UniqueConstraint('proforma_id', name='purchase_reception_from_onlyone_proforma'),
    )


class ReceptionLine(Base):
    __tablename__ = 'reception_lines'

    id = Column(Integer, primary_key=True)
    reception_id = Column(Integer, ForeignKey('receptions.id'))

    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    description = Column(String(100), nullable=True)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)

    item = relationship('Item', uselist=False)

    reception = relationship(
        'Reception',
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update'
        )
    )

    def __eq__(self, other):
        return all((
            other.item_id == self.item_id,
            other.description == self.description,
            other.condition == self.condition,
            other.spec == self.spec
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (
            self.item_id, self.description, self.spec,
            self.condition
        ))
        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(item_id={self.item_id}, description={self.description}, condition={self.condition}"
        s += f", spec={self.spec})"
        return s

    __table_args__ = (
        UniqueConstraint('id', 'reception_id'),
    )


class ReceptionSerie(Base):
    __tablename__ = 'reception_series'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    line_id = Column(Integer, ForeignKey('reception_lines.id'), nullable=False)
    serie = Column(String(50), nullable=False)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)

    created_on = Column(DateTime, default=datetime.now)

    item = relationship('Item', uselist=False)
    line = relationship('ReceptionLine', backref=backref('series'))

    def __init__(self, item_id, line, serie, condition, spec):
        self.item_id = item_id
        self.line = line
        self.serie = serie
        self.condition = condition
        self.spec = spec

    @classmethod
    def from_excel(cls, serie, _1, description, condition, spec, _2, line):
        from utils import description_id_map
        self = cls(description_id_map[description], line, serie, condition, spec)
        return self


class ExpeditionSerie(Base):
    __tablename__ = 'expedition_series'

    id = Column(Integer, primary_key=True)
    line_id = Column(Integer, ForeignKey('expedition_lines.id'))
    serie = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.now)

    line = relationship('ExpeditionLine', backref=backref('series'))

    __table_args__ = (
        UniqueConstraint('id', 'line_id', 'serie'),
    )

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'{class_name}(id={self.id}, line_id={self.line_id}, serie={self.serie})'

        # def __eq__(self, other):
    #     return (self.id, self.line_id, self.serie) == (other.id, other.line_id, other.serie)

    # def __hash__(self):
    #     return functools.reduce(
    #         operator.xor, 
    #         (hash(x) for x in(self.id, self.line_id, self.serie)), 
    #         0 
    #     )


class Imei(Base):
    __tablename__ = 'imeis'

    imei = Column(String(50), primary_key=True, nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50))
    spec = Column(String(50))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)

    item = relationship('Item', uselist=False)
    warehouse = relationship('Warehouse', uselist=False)



class ImeiMask(Base):
    __tablename__ = 'imeis_mask'

    imei = Column(String(50), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    origin_id = Column(Integer, nullable=False)

    item = relationship('Item', uselist=False)
    warehouse = relationship('Warehouse', uselist=False)


def create_and_populate():
    import sys
    import random

    if sys.platform == 'win32':
        testpath = r'.\app\SalesInvoice_LWI003703.pdf'
    elif sys.platform == 'darwin':
        testpath = r'./app/SalesInvoice_LWI003703.pdf'
    else:
        print('I dont know in which platform I am')
        sys.exit()

    Base.metadata.create_all(engine)

    session = Session()

    spec_list = [Spec('EEUU'), Spec('JAPAN'), Spec('FRANCE'),
                 Spec('SPAIN'), Spec('Mix')]

    condition_list = [Condition('NEW'), Condition('USED'), Condition('A+'),
                      Condition('A+/A-'), Condition('B+'), Condition('Mix')]

    session.add_all(spec_list)
    session.add_all(condition_list)

    a1 = Agent()

    a1.fiscal_name = 'Andrei Enache'
    a1.fiscal_number = 'X4946057E'
    a1.email = 'andrei.officee@gmail.com'
    a1.phone = '604178304'
    a1.country = 'Spain'
    a1.active = True

    a2 = Agent()

    a2.fiscal_name = 'Raimundo Cortès'
    a2.fiscal_number = '4253234532'
    a2.email = 'raimun.cortes@bbb.com'
    a2.phone = '898949865'
    a2.country = 'France'
    a2.active = True

    a3 = Agent()
    a3.fiscal_name = 'Raimundo Lopez'
    a3.fiscal_number = 'X34234234'
    a3.active = False
    a3.country = 'Spain'
    a3.email = 'aasdasdnwe@fas.com'
    a3.phone = '7723324324'

    agent_list = [a1, a2, a3]

    partner1 = Partner()

    partner1.fiscal_name = 'Euromedia Investment Group, S.L.'
    partner1.fiscal_number = 'B98815608'
    partner1.trading_name = 'Euromedia'
    partner1.billing_country = 'Spain'
    partner1.agent = random.choice(agent_list)

    partner1.shipping_line1 = 'Shipping line1'
    partner1.shipping_line2 = 'Shipping line2'
    partner1.shipping_line3 = 'Shipping line3'

    partner1.shipping_city = 'Shipping city'
    partner1.shipping_state = 'Shipping state'
    partner1.shipping_country = 'Spain'
    partner1.shipping_postcode = 'Shipping postcode'

    partner1.billing_line1 = 'billing line1'
    partner1.billing_line2 = 'billing line2'
    partner1.billing_line3 = 'billing line3'

    partner1.billing_city = 'billing city'
    partner1.billing_state = 'billing state'
    partner1.billing_country = 'Spain'
    partner1.billing_postcode = 'billing postcode'

    contact1 = PartnerContact('Angel Mirchev', 'CEO', '673567274',
                              'angel.bn@euromediagroup.com', 'Boss of the people')

    contact2 = PartnerContact('Tihomir Damyianov', 'Sales Manager', '772342343',
                              'tihomir.dv@euromediagroup.com', 'The boss of the salesman')

    partner1.contacts.extend([contact1, contact2])

    partner1.we_pay_they_ship = True
    partner1.days_credit_limit = 30
    partner1.amount_credit_limit = 10000
    partner1.warranty = 7

    partner2 = Partner()

    partner2.fiscal_name = 'The boring company.'
    partner2.fiscal_number = '32442234235324'
    partner2.trading_name = 'The boring comany'
    partner2.billing_country = 'EEUU'
    partner2.agent = random.choice(agent_list)

    contact1 = PartnerContact('Elon Musk', 'CEO', '673567274',
                              'elon.musk@tre.com', 'Boss of the people')

    contact2 = PartnerContact('Jose Ignacio Fernanzed', 'Admin', '772342343',
                              'jose@ignacio.com', 'Un idiota')

    partner2.contacts.extend([contact1, contact2])

    partner2.shipping_line1 = 'Shipping line1'
    partner2.shipping_line2 = 'Shipping line2'
    partner2.shipping_line3 = 'Shipping line3'

    partner2.shipping_city = 'Shipping city'
    partner2.shipping_state = 'Shipping state'
    partner2.shipping_country = 'Spain'
    partner2.shipping_postcode = 'Shipping postcode'

    partner2.billing_line1 = 'billing line1'
    partner2.billing_line2 = 'billing line2'
    partner2.billing_line3 = 'billing line3'

    partner2.billing_city = 'billing city'
    partner2.billing_state = 'billing state'
    partner2.billing_country = 'Spain'
    partner2.billing_postcode = 'billing postcode'

    partner2.warranty = 9
    partner2.we_pay_they_ship = True
    partner2.days_credit_limit = 10
    partner2.amount_credit_limit = 50000

    partner_list = [partner1, partner2]

    from utils import base64Pdf

    ad1 = AgentDocument()
    ad1.name = 'NIE'
    ad1.document = base64Pdf(testpath)
    ad1.agent = random.choice(agent_list)

    ad2 = AgentDocument()
    ad2.name = 'Passport'
    ad2.document = base64Pdf(testpath)
    ad2.agent = random.choice(agent_list)

    pd = PartnerDocument()
    pd.name = 'TAF'
    pd.document = base64Pdf(testpath)
    pd.partner = random.choice(partner_list)

    session.add_all(agent_list)
    session.add_all(partner_list)

    item_list = [item1, item2, item3, item4, item5, item6, item7, item8, item9]

    session.add_all(item_list)

    warehouse_list = [Warehouse('Drebno'), Warehouse('Sale'), Warehouse('Trash')]

    session.add_all(warehouse_list)

    courier_list = [Courier('DHL'), Courier('MRV'), Courier('Fedex')]
    session.add_all(courier_list)

    session.flush()
    # for i in range(1, 4):

    proforma = PurchaseProforma()
    proforma.type = 1
    proforma.number = 1
    proforma.date = datetime(2020, 10, 11)
    from datetime import timedelta
    proforma.eta = proforma.date + timedelta(days=5)
    proforma.partner = random.choice(partner_list)
    proforma.agent = random.choice(agent_list)
    proforma.warehouse = session.query(Warehouse).where(Warehouse.description == 'Drebno').one()
    proforma.courier = random.choice(courier_list)
    proforma.eur_currency = True
    proforma.incoterm = 'FOB'
    proforma.we_pay_we_ship = True

    line = PurchaseProformaLine()
    line.proforma = proforma
    line.item = random.choice([item for item in item_list if 'ams' not in item.manufacturer])
    line.condition = random.choice([c.description for c in condition_list])
    line.spec = random.choice([s.description for s in spec_list])
    # line.quantity = random.choice([i for i in range(5, 15)])
    line.quantity = 4
    line.price = random.uniform(200.0, 400.2)

    proforma.lines.append(line)

    line = PurchaseProformaLine()
    line.proforma = proforma
    line.description = 'Apple Iphone X Mixed GB Mixed Color'
    line.condition = random.choice([c.description for c in condition_list])
    line.spec = random.choice([s.description for s in spec_list])
    # line.quantity = random.choice([i for i in range(5, 15)])
    line.quantity = 4
    line.price = random.uniform(200.0, 400.2)
    proforma.lines.append(line)

    line = PurchaseProformaLine()
    line.proforma = proforma
    line.item = random.choice(item_list)
    line.condition = random.choice([c.description for c in condition_list])
    line.spec = 'Mix'
    # line.quantity = random.choice([i for i in range(5, 15)])
    line.quantity = 4
    line.price = random.uniform(200.0, 400.2)
    proforma.lines.append(line)

    line = PurchaseProformaLine()
    line.proforma = proforma
    line.item = random.choice(item_list)
    line.condition = 'Mix'
    line.spec = random.choice([s.description for s in spec_list])
    line.quantity = 4
    line.price = random.uniform(200.0, 400.2)
    proforma.lines.append(line)

    session.add(proforma)

    pd = PurchaseDocument()
    pd.name = 'customs'
    pd.document = base64Pdf(testpath)
    pd.proforma = proforma

    session.commit()


def create_sale(type):
    proforma = SaleProforma()
    proforma.type = type
    number = session.query(func.max(SaleProforma.number)).where(SaleProforma.type == type).scalar()

    proforma.number = 1 if not number else number + 1
    proforma.date = datetime(2020, 10, 11)
    from datetime import timedelta
    proforma.eta = proforma.date + timedelta(days=5)
    proforma.partner = session.query(Partner).first()
    proforma.agent = session.query(Agent).first()
    proforma.warehouse = session.query(Warehouse).where(Warehouse.id == 1).one()
    proforma.courier = session.query(Courier).first()
    proforma.eur_currency = True
    proforma.incoterm = 'FOB'
    proforma.sent = False
    proforma.cancelled = False

    line = SaleProformaLine()

    session.add(proforma)
    session.commit()


@event.listens_for(PurchaseProformaLine, 'after_delete')
def delete_dependant_advanced_sales(mapper, connection, target):
    origin_id = target.id

    stmt = update(AdvancedLine).where(
        AdvancedLine.origin_id == origin_id
    ).values(quantity=0)

    connection.execute(stmt)


@event.listens_for(ReceptionSerie, 'after_insert')
def reception_series_after_insert(mapper, connection, target):
    # Execute always
    connection.execute(imei_insert_stmt(target))

    if any((
            target.line.description is not None,
            'Mix' in target.line.condition,
            'Mix' in target.spec
    )):
        sister_origin_id = get_sister_origin_id(target)

        if sister_origin_id is not None:

            advanced = session.query(AdvancedLine.id).join(SaleProforma). \
                where(SaleProforma.cancelled == False). \
                where(AdvancedLine.origin_id == sister_origin_id).all()

            if len(advanced) > 0:
                connection.execute(imei_mask_insert_stmt(target, sister_origin_id))


def get_sister_origin_id(reception_serie: ReceptionSerie):
    line_alias = reception_serie.line
    for line in reception_serie.line.reception.proforma.lines:
        if line == line_alias:
            return line.id


def imei_insert_stmt(target):
    return insert(Imei).values(
        imei=target.serie,
        item_id=target.item_id,
        condition=target.condition,
        spec=target.spec,
        warehouse_id=target.line.reception.proforma.warehouse_id
    )


def imei_mask_insert_stmt(target, origin_id):
    return insert(ImeiMask).values(
        imei=target.serie,
        item_id=target.item_id,
        condition=target.condition,
        spec=target.spec,
        warehouse_id=target.line.reception.proforma.warehouse_id,
        origin_id=origin_id
    )


@event.listens_for(ReceptionSerie, 'after_delete')
def reception_series_after_delete(mapper, connection, target):
    # No puede haber error humano aqui. El programa decide por eso
    # no es necesario where clause.
    connection.execute(delete(Imei).where(Imei.imei == target.serie))
    connection.execute(delete(ImeiMask).where(ImeiMask.imei == target.serie))


def get_linked_proforma_id(expedition_serie):
    origin_id = expedition_serie.line.expedition.proforma.advanced_lines[0].origin_id
    return session.query(PurchaseProforma.id).join(PurchaseProformaLine).where(
        PurchaseProformaLine.id == origin_id
    ).scalar()


def get_linked_origin_id(expedition_serie):
    return expedition_serie.line.expedition.proforma.advanced_lines[0].origin_id


def get_origin_id_from_expedition_serie(target):
    return session.query(
        AdvancedLine.origin_id
    ).join(AdvancedLineDefinition).join(SaleProforma).where(
        AdvancedLineDefinition.item_id == target.line.item_id,
        AdvancedLineDefinition.condition == target.line.condition,
        AdvancedLineDefinition.spec == target.line.spec
    ).first().origin_id


@event.listens_for(ExpeditionSerie, 'after_insert')
def expedition_series_after_insert(mapper, connection, target):
    # 1 . Search reception line
    # origin -> proforma_id -> reception_line
    # 2 . Build reception series
    # 3 . Insert reception series
    # Expedition series already inserted by session api
    condition = target.line.condition
    spec = target.line.spec
    item_id = target.line.item_id
    serie = target.serie

    if target.line.expedition.from_sale_type == FAST:
        try:
            proforma_id = get_linked_proforma_id(target)

            reception_line_id = session.query(ReceptionLine.id).join(Reception) \
                .where(
                Reception.proforma_id == proforma_id
            ).where(
                ReceptionLine.item_id == item_id,
                ReceptionLine.condition == condition,
                ReceptionLine.spec == spec
            ).scalar()

            connection.execute(
                reception_series_insert_statement(
                    serie=serie, item_id=item_id, condition=condition,
                    spec=spec, reception_line_id=reception_line_id
                )
            )

        except IndexError:
            return

    elif target.line.expedition.from_sale_type == NORMAL:

        condition = target.line.condition
        spec = target.line.spec
        item_id = target.line.item_id
        result = connection.execute(
            delete(Imei).where(
                Imei.imei == serie,
                Imei.item_id == item_id,
                Imei.condition == condition,
                Imei.spec == spec
            )
        )
        if not result.rowcount:
            from exceptions import NotExistingStockOutput
            raise NotExistingStockOutput

    elif target.line.expedition.from_sale_type == DEFINED:

        origin_id = get_origin_id_from_expedition_serie(target)

        result = connection.execute(
            delete(ImeiMask).where(
                ImeiMask.imei == serie,
                ImeiMask.item_id == item_id,
                ImeiMask.condition == condition,
                ImeiMask.spec == spec,
                ImeiMask.origin_id == origin_id
            )
        )

        if not result.rowcount:
            from exceptions import NotExistingStockInMask
            raise NotExistingStockInMask
        else:
            connection.execute(
                delete(Imei).where(
                    Imei.imei == serie,
                    Imei.item_id == item_id,
                    Imei.condition == condition,
                    Imei.spec == spec
                )
            )


def reception_series_insert_statement(item_id, serie, condition, spec, reception_line_id):
    return insert(ReceptionSerie).values(
        condition=condition,
        spec=spec,
        item_id=item_id,
        line_id=reception_line_id,
        serie=serie
    )


@event.listens_for(ExpeditionSerie, 'after_delete')
def expedition_series_after_delete(mapper, connection, target):
    if target.line.expedition.from_sale_type == FAST:
        connection.execute(
            delete(ReceptionSerie).where(ReceptionSerie.serie == target.serie)
        )

    elif target.line.expedition.from_sale_type == NORMAL:
        stmt = insert(Imei).values(
            imei=target.serie,
            item_id=target.line.item_id,
            condition=target.line.condition,
            spec=target.line.spec,
            warehouse_id=target.line.expedition.proforma.warehouse.id
        )

        connection.execute(stmt)
    elif target.line.expedition.from_sale_type == DEFINED:

        origin_id = get_origin_id_from_expedition_serie(target)

        stmt = insert(ImeiMask).values(
            imei=target.serie,
            item_id=target.line.item_id,
            condition=target.line.condition,
            spec=target.line.spec,
            warehouse_id=target.line.expedition.proforma.warehouse_id,
            origin_id=origin_id
        )

        connection.execute(stmt)

class SpecChange(Base):
    __tablename__ = 'spec_changes'

    id = Column(Integer, primary_key=True)
    sn = Column(String(50), nullable=False)
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    comment = Column(String(50), nullable=True)
    created_on = Column(DateTime, default=datetime.now)

    def __init__(self, sn, before, after, comment=None):
        self.sn = sn
        self.before = before
        self.after = after
        self.comment = comment

class WarehouseChange(Base):
    __tablename__ = 'warehouse_changes'

    id = Column(Integer, primary_key=True)
    sn = Column(String(50), nullable=False)
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    comment = Column(String(50), nullable=True)
    created_on = Column(DateTime, default=datetime.now)

    def __init__(self, sn, before, after, comment=None):
        self.sn = sn
        self.before = before
        self.after = after
        self.comment = comment



class ConditionChange(Base):
    __tablename__ = 'condition_changes'

    id = Column(Integer, primary_key=True)
    sn = Column(String(50), nullable=False)
    before = Column(String(50), nullable=False)
    after = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.now)
    comment = Column(String(50), nullable=True)

    def __init__(self, sn, before, after, comment=None):
        self.sn = sn
        self.before = before
        self.after = after
        self.comment = comment



class IncomingRma(Base):

    __tablename__ = 'incoming_rmas'

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'))
    date = Column(Date, nullable=True)

    partner = relationship('Partner', uselist=False)


class IncomingRmaLine(Base):

    __tablename__ = 'incoming_rma_lines'

    id = Column(Integer, primary_key=True)
    incoming_rma_id = Column(Integer, ForeignKey('incoming_rmas.id'))

    sn = Column(String(50), nullable=False)
    purchase_date = Column(Date, nullable=False)
    purchase_description = Column(String(100), nullable=False)
    arrival_date = Column(DateTime,  nullable=False)
    defined_as = Column(String(100), nullable=False)
    sold_as = Column(String(100), nullable=False)
    sale_date = Column(Date, nullable=False)
    warehouse_picking_datetime = Column(DateTime, nullable=False)

    incoming_rma = relationship(
        'IncomingRma',
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update'
        )
    )


def create_lines():
    line = SaleProformaLine()
    line.proforma_id = 1
    line.mix_id = 0
    line.item_id = 1
    line.spec = 'EEUU'
    line.condition = 'B+'
    line.quantity = 3
    line.price = 145.2
    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.mix_id = 0
    line.item_id = 1
    line.condition = 'NEW'
    line.spec = 'EEUU'
    line.quantity = 10
    line.price = 100
    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.mix_id = 0
    line.item_id = 1
    line.condition = 'NEW'
    line.spec = 'FRANCE'
    line.quantity = 7
    line.price = 100

    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.mix_id = 0
    line.item_id = 4
    line.condition = 'NEW'
    line.spec = 'FRANCE'
    line.quantity = 4
    line.price = 100
    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.item_id = None
    line.condition = None
    line.spec = None
    line.quantity = 10
    line.description = 'Servicios de transporte'

    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.mix_id = None
    line.item_id = 1
    line.spec = 'EEUU'
    line.condition = 'USED'
    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.item_id = 3
    line.condition = 'NEW'
    line.spec = 'EEEUU'
    line.mix_id = None
    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.item_id = None
    line.condition = None
    line.spec = None
    line.quantity = 10
    line.description = 'Servicios de transporte'

    session.add(line)

    line = SaleProformaLine()
    line.proforma_id = 1
    line.item_id = 4
    line.condition = 'USED'
    line.showing_condition = 'NEW'
    line.spec = 'SPAIN'
    line.quantity = 10

    session.add(line)

    session.commit()


def create_mask():
    mask = ImeiMask()
    mask.item_id = 1
    mask.imei = 'G'
    mask.condition = 'B+'
    mask.spec = 'EEUU'
    mask.warehouse_id = 1

    session.add(mask)
    session.commit()


def create_advanced_line():
    line = AdvancedLine()
    line.origin_id = 1
    line.quantity = 3

    session.add(line)

    session.commit()


def create_test_data():
    import sys

    if sys.platform == 'win32':
        testpath = r'.\app\SalesInvoice_LWI003703.pdf'
    elif sys.platform == 'darwin':
        testpath = r'./app/SalesInvoice_LWI003703.pdf'
    else:
        print('I dont know in which platform I am')
        sys.exit()

        # CAP=0 COL=0 SERIE=1
    import random
    # session.add_all([
    #     Item(
    #         mpn = '', 
    #         manufacturer = 'AMD', 
    #         category='Graphic Card', 
    #         model = 'x11', 
    #         color='',
    #         capacity='', 
    #         has_serie=True
    #     ), Item(
    #         mpn='', 
    #         manufacturer = 'INTEL', 
    #         category='microprocesor', 
    #         model = 'x86_64', 
    #         color='', 
    #         capacity='', 
    #         has_serie=True
    #     ), 

    #     #  CAP=0 COL=0 SERIE=0
    #     Item(
    #         mpn='MPN1231', 
    #         manufacturer='Apple', 
    #         category='cable', 
    #         model = 'coco', 
    #         color='', 
    #         capacity='', 
    #         has_serie=False
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category='Charger', 
    #         model='lol', 
    #         capacity='', 
    #         color='', 
    #         has_serie=False
    #     )
    # ])

    # # STOCK_TYPE = -1 

    # session.add_all([
    #     Item(
    #         mpn = 'MPN1', 
    #         manufacturer = 'Apple', 
    #         category='iPhone', 
    #         model = 'xs pro', 
    #         capacity='433', 
    #         color='yellow', 
    #         has_serie=True  
    #     ), 
    #     Item(
    #         mpn = 'MPN2', 
    #         manufacturer='Samsung', 
    #         category='Phone', 
    #         model = 'galaxy', 
    #         capacity='22', 
    #         color='blue', 
    #         has_serie=True
    #     )
    # ])

    # # CAP=0 COL=1 SERIE=0

    # session.add_all([
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category= 'Airpods', 
    #         model = 'model1',
    #         capacity='', 
    #         color='yellow', 
    #         has_serie=False
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category= 'Airpods', 
    #         model = 'model1',
    #         capacity='', 
    #         color='blue', 
    #         has_serie=False
    #     ),
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category= 'Airpods', 
    #         model = 'model1',
    #         capacity='', 
    #         color='orange', 
    #         has_serie=False
    #     ),
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category= 'Airpods', 
    #         model = 'model1',
    #         capacity='', 
    #         color='brown', 
    #         has_serie=False
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Samsung', 
    #         category='Headphones', 
    #         model='themodel', 
    #         capacity='', 
    #         color='purple', 
    #         has_serie=False
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Samsung', 
    #         category='Headphones', 
    #         model='themodel', 
    #         capacity='', 
    #         color='gray', 
    #         has_serie=False
    #     )
    # ])

    # # CAP = 0 COL=1 SERIE=1
    # session.add_all([
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category='iPad', 
    #         model = 'wer', 
    #         capacity='', 
    #         color='brown', 
    #         has_serie=True
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category='iPad', 
    #         model = 'wer', 
    #         capacity='', 
    #         color='yellow',
    #         has_serie=True 
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category='iPad', 
    #         model = 'wer', 
    #         capacity='', 
    #         color='gray', 
    #         has_serie=True
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Apple', 
    #         category='iPad', 
    #         model = 'wer', 
    #         capacity='', 
    #         color='purple',
    #         has_serie=True 
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Xiamoi', 
    #         category='Tv', 
    #         model = 'wgdf', 
    #         capacity='', 
    #         color='black', 
    #         has_serie=True
    #     ), 
    #     Item(
    #         mpn='', 
    #         manufacturer='Xiaomi', 
    #         category='Tv', 
    #         model = 'wgdf', 
    #         capacity='', 
    #         color='white', 
    #         has_serie=True
    #     )
    # ])

    # # CAP = 1 COL = 0 SERIE=1
    # session.add_all([
    #     Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '13', 
    #         color='', 
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '43', 
    #         color='',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '54', 
    #         color='',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '65', 
    #         color='',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Huawey', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '10', 
    #         color='',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Huawey', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '33', 
    #         color='',  
    #         has_serie=True
    #     )
    # ])

    # # CAP = 1 COL = 1 SERIE = 1

    # session.add_all([
    #     Item(
    #         mpn = '', 
    #         manufacturer='Apple', 
    #         category='iPhone',
    #         model='xs', 
    #         capacity = '10', 
    #         color='yellow', 
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Apple', 
    #         category='iPhone',
    #         model='xs', 
    #         capacity = '10', 
    #         color='blue',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Apple', 
    #         category='iPhone',
    #         model='xs', 
    #         capacity = '10', 
    #         color='green',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Apple', 
    #         category='iPhone',
    #         model='xs', 
    #         capacity = '12', 
    #         color='black',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Apple', 
    #         category='iPhone',
    #         model='xs',
    #         capacity = '14', 
    #         color='white',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Huawey', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '16', 
    #         color='black',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Huawey', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '33', 
    #         color='gray',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Huawey', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '55', 
    #         color='yellow',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Watch',
    #         model='wam', 
    #         capacity = '10', 
    #         color='nocolor',  
    #         has_serie=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Dron',
    #         model='sdr', 
    #         capacity = '130', 
    #         color='black',  
    #         has_series=True
    #     ),Item(
    #         mpn = '', 
    #         manufacturer='Samsung', 
    #         category='Drone',
    #         model='sdr', 
    #         capacity = '421', 
    #         color='red',  
    #         has_serie=True
    #     )
    # ])

    session.add_all([
        Condition('A'),
        Condition('B'),
        Condition('New'),
        Condition('Mix')
    ])

    session.add_all([
        Spec('EU'),
        Spec('Mix'),
        Spec('US')
    ])

    session.add_all([
        Warehouse('warehouse1'),
        Warehouse('Warehouse2')
    ])

    session.add_all([
        Courier('Courier1'),
        Courier('Courier2')
    ])

    a1 = Agent()

    a1.fiscal_name = 'Andrei En ache'
    a1.fiscal_number = 'X4946057E'
    a1.email = 'andrei.officee@gmail.com'
    a1.phone = '604178304'
    a1.country = 'Spain'
    a1.active = True

    a2 = Agent()

    a2.fiscal_name = 'Raimundo Cortès'
    a2.fiscal_number = '4253234532'
    a2.email = 'raimun.cortes@bbb.com'
    a2.phone = '898949865'
    a2.country = 'France'
    a2.active = True

    a3 = Agent()
    a3.fiscal_name = 'Raimundo Lopez'
    a3.fiscal_number = 'X34234234'
    a3.active = False
    a3.country = 'Spain'
    a3.email = 'aasdasdnwe@fas.com'
    a3.phone = '7723324324'

    agent_list = [a1, a2, a3]

    partner1 = Partner()

    partner1.fiscal_name = 'Euromedia Investment Group, S.L.'
    partner1.fiscal_number = 'B98815608'
    partner1.trading_name = 'Euromedia'
    partner1.billing_country = 'Spain'
    partner1.agent = random.choice(agent_list)

    partner1.shipping_line1 = 'Shipping line1'
    partner1.shipping_line2 = 'Shipping line2'
    partner1.shipping_line3 = 'Shipping line3'

    partner1.shipping_city = 'Shipping city'
    partner1.shipping_state = 'Shipping state'
    partner1.shipping_country = 'Spain'
    partner1.shipping_postcode = 'Shipping postcode'

    partner1.billing_line1 = 'billing line1'
    partner1.billing_line2 = 'billing line2'
    partner1.billing_line3 = 'billing line3'

    partner1.billing_city = 'billing city'
    partner1.billing_state = 'billing state'
    partner1.billing_country = 'Spain'
    partner1.billing_postcode = 'billing postcode'

    contact1 = PartnerContact('Angel Mirchev', 'CEO', '673567274',
                              'angel.bn@euromediagroup.com', 'Boss of the people')

    contact2 = PartnerContact('Tihomir Damyianov', 'Sales Manager', '772342343',
                              'tihomir.dv@euromediagroup.com', 'The boss of the salesman')

    partner1.contacts.extend([contact1, contact2])

    partner1.we_pay_they_ship = True
    partner1.days_credit_limit = 30
    partner1.amount_credit_limit = 10000
    partner1.warranty = 7

    partner2 = Partner()

    partner2.fiscal_name = 'The boring company.'
    partner2.fiscal_number = '32442234235324'
    partner2.trading_name = 'The boring company'
    partner2.billing_country = 'EEUU'
    partner2.agent = random.choice(agent_list)

    contact1 = PartnerContact('Elon Musk', 'CEO', '673567274',
                              'elon.musk@tre.com', 'Boss of the people')

    contact2 = PartnerContact('Jose Ignacio Fernanzed', 'Admin', '772342343',
                              'jose@ignacio.com', 'Un idiota')

    partner2.contacts.extend([contact1, contact2])

    partner2.shipping_line1 = 'Shipping line1'
    partner2.shipping_line2 = 'Shipping line2'
    partner2.shipping_line3 = 'Shipping line3'

    partner2.shipping_city = 'Shipping city'
    partner2.shipping_state = 'Shipping state'
    partner2.shipping_country = 'Spain'
    partner2.shipping_postcode = 'Shipping postcode'

    partner2.billing_line1 = 'billing line1'
    partner2.billing_line2 = 'billing line2'
    partner2.billing_line3 = 'billing line3'

    partner2.billing_city = 'billing city'
    partner2.billing_state = 'billing state'
    partner2.billing_country = 'Spain'
    partner2.billing_postcode = 'billing postcode'

    partner2.warranty = 9
    partner2.we_pay_they_ship = True
    partner2.days_credit_limit = 10
    partner2.amount_credit_limit = 50000

    partner_list = [partner1, partner2]

    from utils import base64Pdf

    ad1 = AgentDocument()
    ad1.name = 'NIE'
    ad1.document = base64Pdf(testpath)
    ad1.agent = random.choice(agent_list)

    ad2 = AgentDocument()
    ad2.name = 'Passport'
    ad2.document = base64Pdf(testpath)
    ad2.agent = random.choice(agent_list)

    pd = PartnerDocument()
    pd.name = 'TAF'
    pd.document = base64Pdf(testpath)
    pd.partner = random.choice(partner_list)

    session.add_all(agent_list)
    session.add_all(partner_list)

    session.commit()


def create_init_data():
    spec = Spec('Mix')
    condition = Condition('Mix')

    session.add(spec)
    session.add(condition)

    session.commit()


def correct_mask():

    for row in session.query(ImeiMask.origin_id).distinct():
        purchase_proforma = session.query(PurchaseProforma).join(PurchaseProformaLine).\
            where(PurchaseProformaLine.id == row.origin_id).first()
        if purchase_proforma.completed:
            if all((
                sale.completed for sale in session.query(SaleProforma).join(AdvancedLine).\
                    where(AdvancedLine.origin_id == row.origin_id)
            )):
                stmt = delete(ImeiMask).where(ImeiMask.origin_id == row.origin_id)
                session.execute(stmt)

    try:
        session.commit()
    except:
        session.rollback()
        raise


if __name__ == '__main__':
    Base.metadata.create_all(get_engine())

    create_init_data()
