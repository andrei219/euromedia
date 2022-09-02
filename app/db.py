from mysqlx import Column
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

from datetime import timedelta

from sqlalchemy.sql.operators import exists

engine = create_engine('mysql+mysqlconnector://andrei:hnq#4506@192.168.1.78:3306/appdb', echo=False)
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
    fiscal_name = Column(String(50), nullable=False, unique=True)
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

    shipping_city = Column(String(50))
    shipping_state = Column(String(50))
    shipping_country = Column(String(50))
    shipping_postcode = Column(String(50))

    billing_line1 = Column(String(50))
    billing_line2 = Column(String(50))

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


RED, GREEN, YELLOW, ORANGE = '#FF7F7F', '#90EE90', '#FFFF66', '#FFD580'


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

    invoice = relationship('PurchaseInvoice', backref=backref('proformas'))
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

    def __hash__(self):
        return functools.reduce(operator.xor, (hash(x) for x in (self.type, self.number)), 0)


    @property
    def doc_repr(self):
        return str(self.type) + '-' + str(self.number).zfill(6)

    @property
    def subtotal(self):
        return round(sum(line.price * line.quantity for line in self.lines), 2)

    @property
    def tax(self):
        return round(sum(line.price * line.quantity * line.tax / 100 for line in self.lines), 2)


    @property
    def total_debt(self):
        return round(self.subtotal + self.tax, 2)

    @property
    def total_paid(self):
        return round(sum(p.amount for p in self.payments), 2)

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
            if line.item_id is not None or line.description in utils.descriptions
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

    @property
    def device_count(self):
        try:
            return sum(len(line.series) for line in self.reception.lines)
        except AttributeError:
            return 0

    @property
    def owing(self):
        return self.total_debt - self.total_paid

    @property
    def financial_status_string(self):
        if self.not_paid:
            return 'Not Paid'
        elif self.partially_paid:
            return 'Partially Paid'
        elif self.fully_paid:
            return 'Paid'
        elif self.overpaid:
            return 'They Owe'

    @property
    def logistic_status_string(self):
        if self.empty:
            return "Empty"
        elif self.overflowed:
            return "Overflowed"
        elif self.partially_processed:
            return "Partially Received"
        elif self.completed:
            return "Completed"

    @property
    def partner_name(self):
        return self.partner.fiscal_name

    @property
    def partner_object(self):
        return self.partner


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

    @property
    def subtotal(self):
        return round(self.quantity * self.price, 2)

    @property
    def total(self):
        return round(self.quantity * self.price * ( 1 + self.tax/100), 2)

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

    @property
    def payments(self):
        return [payment for proforma in self.proformas for payment in proforma.payments]

    @property
    def doc_repr(self):
        return str(self.type) + '-' + str(self.number).zfill(6)

    @property
    def subtotal(self):
        return round(sum(p.subtotal for p in self.proformas), 2)

    @property
    def tax(self):
        return round(sum(p.tax for p in self.proformas), 2)

    @property
    def total_debt(self):
        return sum(proforma.total_debt for proforma in self.proformas)

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
    def device_count(self):
        return sum(p.device_count for p in self.proformas)

    def __init__(self, type, number):
        self.type = type
        self.number = number

    __table_args__ = (
        UniqueConstraint('type', 'number'),
    )

    @property
    def logistic_status_string(self):
        if all(p.empty for p in self.proformas):
            return 'Empty'
        elif any(p.overflowed for p in self.proformas):
            return 'Overflowed'
        elif any(p.partially_processed for p in self.proformas):
            return 'Partially received'
        elif all(p.completed for p in self.proformas):
            return 'Completed'
        elif any(p.empty for p in self.proformas) \
                and any(p.completed for p in self.proformas):
            return 'Partially received'

    @property
    def financial_status_string(self):
        if self.not_paid:
            return 'Not Paid'
        elif self.partially_paid:
            return 'Partially Paid'
        elif self.fully_paid:
            return 'Paid'
        elif self.overpaid:
            return 'They Owe'

    @property
    def partner_name(self):
        return self.proformas[0].partner_name  # Always at least one, by design

    @property
    def agent(self):
        name = self.proformas[0].agent.fiscal_name
        try:
            return name.split()[0]
        except IndexError:
            return name

    @property
    def sent(self):
        if all(p.sent for p in self.proformas):
            return 'Yes'
        elif all(not p.sent for p in self.proformas):
            return 'No'
        elif any(not p.sent for p in self.proformas):
            return 'Partially'


    @property
    def cancelled(self):
        if all(p.cancelled for p in self.proformas):
            return 'Yes'
        elif all(not p.cancelled for p in self.proformas):
            return 'No'
        elif any(not p.cancelled for p in self.proformas):
            return 'Partially'

    @property
    def currency(self):
        return ' EUR' if self.proformas[0].eur_currency else ' USD'

    @property
    def owing_string(self):
        return str(self.total_debt - self.total_paid) + self.currency

    @property
    def total(self):
        return str(self.total_debt) + self.currency

    @property
    def external(self):
        return self.helper('external')

    @property
    def warning(self):
        return self.helper('warning')

    @property
    def tracking(self):
        return self.helper('tracking')

    @property
    def note(self):
        return self.helper('note')

    def helper(self, attrname):
        values = set(getattr(p, attrname) for p in self.proformas)
        if len(values) == 1 and values != {None}:
            return values.pop()
        elif len(values) != 1:
            return ', '.join((v or '' for v in values))
        elif values == {None}:
            return ''


    @property
    def inwh(self):
        if all(p.reception is not None for p in self.proformas):
            return 'Yes'
        elif all(p.reception is None for p in self.proformas):
            return 'No'
        elif any(p.reception is None for p in self.proformas):
            return 'Partially'

    @property
    def origin_proformas(self):
        return ', '.join(p.doc_repr for p in self.proformas)


    @property
    def partner_object(self):
        return self.proformas[0].partner


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

    invoice = relationship('SaleInvoice', backref=backref('proformas'), lazy='joined')

    expedition = relationship('Expedition', uselist=False, back_populates='proforma')

    warning = Column(String(50), nullable=True)

    incoterm = Column(String(3), default='gbc')

    def __repr__(self):
        clasname = self.__class__.__name__
        return f'{clasname}(type={self.type}, number={self.number})'

    __table_args__ = (
        UniqueConstraint('type', 'number'),
    )

    def __hash__(self):
        return functools.reduce(operator.xor, (hash(x) for x in (self.type, self.number)), 0)

    @property
    def doc_repr(self):
        return str(self.type) + '-' + str(self.number).zfill(6)

    @property
    def subtotal(self):
        return round(sum(line.price * line.quantity for line in self.lines) or \
               sum(line.price * line.quantity for line in self.advanced_lines) or \
               sum(line.price * line.quantity for line in self.credit_note_lines), 2)

    @property
    def tax(self):
        return round(sum(line.price * line.quantity * line.tax / 100 for line in self.lines) or \
               sum(line.price * line.quantity * line.tax / 100 for line in self.advanced_lines) or \
               sum(line.price * line.quantity * line.tax / 100 for line in self.credit_note_lines), 2)

    @property
    def is_credit_note(self):
        return self.warehouse_id is None

    @property
    def cn_total(self):
        if self.invoice is not None:
            return self.invoice.cn_total
        return 0

    @property
    def applied(self):
        if self.invoice is not None:
            return self.invoice.applied
        return False

    # Posible fuente de error de precision en este método,
    # Es el invonveniente de usar floats
    # Deberias usar el modulo Decimal
    @property
    def total_debt(self):
        return round(self.subtotal + self.tax, 2)

    @property
    def total_paid(self):
        return round(sum(abs(p.amount) for p in self.payments), 2)

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
               sum(line.quantity for line in self.advanced_lines if line.item_id is not None or \
                   line.mixed_description is not None)

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
            return any((
                len(line.series) > line.quantity
                for line in self.expedition.lines
            ))

        except AttributeError:
            return False
        return False

    @property
    def partner_name(self):
        return self.partner.fiscal_name

    @property
    def partner_object(self):
        return self.partner

    @property
    def device_count(self):
        if self.credit_note_lines:
            return -len(self.credit_note_lines)
        try:
            return sum(len(line.series) for line in self.expedition.lines)
        except AttributeError:
            return 0



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

    parent_id = Column(Integer, ForeignKey('sale_invoices.id'))

    wh_incoming_rma = relationship('WhIncomingRma', uselist=False, back_populates='sale_invoice')

    def __repr__(self):
        clasname = self.__class__.__name__
        return f'{clasname}(type={self.type}, number={self.number})'

    def __init__(self, type, number):
        self.type = type
        self.number = number

    @property
    def payments(self):
        return [payment for proforma in self.proformas for payment in proforma.payments]

    @property
    def is_credit_note(self):
        return self.proformas[0].warehouse_id is None

    @property
    def cn_total(self):
        return round(sum(
            invoice.subtotal for invoice in session.query(SaleInvoice).
            where(SaleInvoice.parent_id == self.id)
        ), 2)

    @property
    def applied(self):
        return session.query(SaleInvoice.parent_id).\
            where(SaleInvoice.id == self.id).scalar() is not None

    @property
    def subtotal(self):
        return round(sum(p.subtotal for p in self.proformas), 2)

    @property
    def total_debt(self):
        return sum(proforma.total_debt for proforma in self.proformas)



    @property
    def tax(self):
        return round(sum(p.tax for p in self.proformas), 2)

    @property
    def total_paid(self):
        return round(sum(abs(p.amount) for p in self.payments), 2)

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
    def doc_repr(self):
        return str(self.type) + '-' + str(self.number).zfill(6)

    @property
    def cn_repr(self):
        return 'CN ' + self.doc_repr

    @property
    def device_count(self):
        return sum(p.device_count for p in self.proformas)

    @property
    def note(self):
        r = ''
        for proforma in self.proformas:
            if proforma.note:
                r += proforma.note + '/'
        return r

    @property
    def logistic_status_string(self):
        if all(p.empty for p in self.proformas):
            return 'Empty'
        elif any(p.overflowed for p in self.proformas):
            return 'Overflowed'
        elif any(p.partially_processed for p in self.proformas):
            return 'Partially Prepared'
        elif all(p.completed for p in self.proformas):
            return 'Completed'
        elif any(p.completed for p in self.proformas) and \
            any(p.empty for p in self.prformas):
                return 'Partially Prepared'

    @property
    def financial_status_string(self):

        if self.applied:
            return 'Applied'


        if self.not_paid:
            return 'Not Paid'
        elif self.partially_paid:
            return 'Partially Paid'
        elif self.fully_paid:
            return 'Paid'
        elif self.overpaid:
            return 'We Owe'

    @property
    def agent(self):
        return self.proformas[0].agent.fiscal_name.split()[0]

    @property
    def partner_name(self):
        return self.proformas[0].partner_name

    @property
    def partner_object(self):
        return self.proformas[0].partner

    @property
    def sent(self):
        if all(p.sent for p in self.proformas):
            return 'Yes'
        elif all(not p.sent for p in self.proformas):
            return 'No'
        elif any(not p.sent for p in self.proformas):
            return 'Partially'

    @property
    def cancelled(self):
        if all(p.cancelled for p in self.proformas):
            return 'Yes'
        elif all(not p.cancelled for p in self.proformas):
            return 'No'
        elif any(not p.cancelled for p in self.proformas):
            return 'Partially'

    @property
    def currency(self):
        return ' EUR' if self.proformas[0].eur_currency else ' USD'

    @property
    def owing_string(self):
        return str(self.total_debt - self.total_paid) + self.currency

    @property
    def total(self):
        return str(self.total_debt) + self.currency

    helper = PurchaseInvoice.helper
    external = PurchaseInvoice.external
    tracking = PurchaseInvoice.tracking
    warning = PurchaseInvoice.warning
    note = PurchaseInvoice.note



    @property
    def inwh(self):
        if all(p.expedition is not None for p in self.proformas):
            return 'Yes'
        elif all(p.expedition is None for p in self.proformas):
            return 'No'
        elif any(p.expedition is None for p in self.proformas):
            return 'Partially'

    @property
    def origin_proformas(self):
        return ', '.join(p.doc_repr for p in self.proformas)

    @property
    def partner_object(self):
        return self.proformas[0].partner_object

    @property
    def ready(self):
        if self.proformas[0].credit_note_lines:
            return 'No'
        elif all(p.ready for p in self.proformas):
            return 'Yes'
        elif any(p.ready for p in self.proformas):
            return 'Partially'
        elif all(not p.ready for p in self.proformas):
            return 'No'

    @property
    def partner_id(self):
        return self.proformas[0].partner.id

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
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update',
        )
    )
    # options lazyjoined to the query
    __table_args__ = (
        UniqueConstraint('id', 'proforma_id'),
    )

    @property
    def subtotal(self):
        return round(self.price * self.quantity, 2)

    @property
    def total(self):
        return round(self.quantity * self.price * (1 + self.tax / 100), 2)

    @property
    def defined(self):
        return all((
            self.item_id is not None,
            self.condition != 'Mix',
            self.spec != 'Mix'
        ))

    def __eq__(self, other):
        return all((
            other.item_id == self.item_id,
            other.condition == self.condition,
            other.spec == self.spec,
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (self.item_id, self.spec, self.condition))
        return functools.reduce(operator.xor, hashes, 0)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}(item_id={self.item_id}, condition={self.condition}, spec={self.spec},mix_id={self.mix_id}, quantity={self.quantity})"


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

    @property
    def defined(self):
        return all((
            self.item_id is not None,
            self.condition != 'Mix',
            self.spec != 'Mix'
        ))

    def __eq__(self, other):
        return all((self.item_id == other.item_id, self.condition == other.condition, self.spec == other.spec, ))

    def __hash__(self):
        hashes = (hash(x) for x in (self.item_id, self.condition,self.spec))
        return functools.reduce(operator.xor, hashes, 0)

    @property
    def subtotal(self):
        return round(self.price * self.quantity, 2)

    @property
    def total(self):
        return round(self.quantity * self.price * (1 + self.tax / 100), 2)

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


    def __eq__(self, other):
        return all((
            other.item_id == self.item_id,
            other.condition == self.condition,
            other.spec == self.spec,
        ))

    def __hash__(self):
        hashes = (hash(x) for x in (self.item_id, self.spec, self.condition))
        return functools.reduce(operator.xor, hashes, 0)


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

    @property
    def total_quantity(self):
        return self.proforma.total_quantity

    @property
    def total_processed(self):
        return self.proforma.total_processed

    @property
    def empty(self):
        return self.proforma.empty

    @property
    def overflowed(self):
        return self.proforma.overflowed

    @property
    def partially_processed(self):
        return self.proforma.partially_processed

    @property
    def completed(self):
        return self.proforma.completed

    @property
    def logistic_status_string(self):
        if self.empty:
            return 'Empty'
        elif self.overflowed:
            return 'Overflowed'
        elif self.partially_processed:
            return 'Partially Processed'
        elif self.completed:
            return 'Completed'

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
        hashes = (hash(x) for x in (self.item_id, self.spec, self.condition))
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

    auto = Column(Boolean, nullable=False, default=False)

    @property
    def total_quantity(self):
        return self.proforma.total_quantity

    @property
    def total_processed(self):
        return self.proforma.total_processed

    @property
    def empty(self):
        return self.proforma.empty

    @property
    def overflowed(self):
        return self.proforma.overflowed


    def __init__(self, proforma, note, auto=False):
        self.proforma = proforma
        self.note = note
        self.auto = auto

    @property
    def partially_processed(self):
        return self.proforma.partially_processed

    @property
    def completed(self):
        return self.proforma.completed

    @property
    def logistic_status_string(self):
        if self.empty:
            return 'Empty'
        elif self.overflowed:
            return 'Overflowed'
        elif self.partially_processed:
            return 'Partially Prepared'
        elif self.completed:
            return 'Completed'


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
        hashes = (hash(x) for x in ( self.item_id, self.description, self.spec, self.condition))
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


class WhIncomingRma(Base):

    __tablename__ = 'wh_incoming_rmas'

    id = Column(Integer, primary_key=True)

    dumped = Column(Boolean, nullable=False, default=False)

    incoming_rma_id = Column(Integer, ForeignKey('incoming_rmas.id'), nullable=False)

    sale_invoice_id = Column(Integer, ForeignKey('sale_invoices.id'))

    incoming_rma = relationship('IncomingRma', back_populates='wh_incoming_rma')

    sale_invoice = relationship('SaleInvoice', back_populates='wh_incoming_rma')


    __table_args__ = (
        UniqueConstraint('incoming_rma_id', name='wh_order_from_onlyone_rma_order'),
    )

    def __init__(self, incoming_rma):
        self.incoming_rma = incoming_rma


class WhIncomingRmaLine(Base):

    __tablename__ = 'wh_incoming_rma_lines'

    id = Column(Integer, primary_key=True)
    wh_incoming_rma_id = Column(Integer, ForeignKey('wh_incoming_rmas.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), default=1)
    item_id = Column(Integer, ForeignKey('items.id'), default=10)
    invoice_type = Column(Integer, nullable=False)
    sn = Column(String(50), nullable=False)
    accepted = Column(Boolean, nullable=False, default=False)
    problem = Column(String(100), nullable=True)
    why = Column(String(50), nullable=True, default="")
    condition = Column(String(50), nullable=False)
    public_condition = Column(String(50), nullable=True)
    spec = Column(String(50), nullable=False)
    price = Column(Float(precision=32, decimal_return_scale=None), nullable=False)

    item = relationship('Item', uselist=False)

    wh_incoming_rma = relationship(
        'WhIncomingRma',
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update'
        )
    )

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(sn={self.sn}, accepetd={self.accepted}, problem={self.problem},"
        s += f"why={self.why})"
        return s

    # def __hash__(self):
    #     return hash(self.sn)

    # def __eq__(self, other):
    #     # if self is None or other is None:
    #     #     return super().__eq__(other)
    #     #
    #     return self.sn == other.sn

    def __init__(self, incoming_rma_line):
        self.sn = incoming_rma_line.sn
        self.problem = incoming_rma_line.problem
        self.accepted = incoming_rma_line.accepted
        self.warehouse_id = 1  # General por defecto
        self.item_id = incoming_rma_line.item_id
        self.condition = incoming_rma_line.condition
        self.spec = incoming_rma_line.spec
        self.price = incoming_rma_line.price
        self.public_condition = incoming_rma_line.public

        try:
            self.invoice_type = session.query(SaleInvoice.type) \
                .join(SaleProforma) \
                .join(Expedition) \
                .join(ExpeditionLine). \
                join(ExpeditionSerie).where(ExpeditionSerie.serie == self.sn).all()[-1].type
        except IndexError:
            raise ValueError('Cant find sale invoice associated')

    @property
    def as_excel_row(self):
        # Circular import error not raised. When execution reaches this
        # code, utils and db are fully loaded.
        from utils import description_id_map, warehouse_id_map

        try:
            purchase_proforma = session.query(PurchaseProforma).\
                join(Reception).join(ReceptionLine).join(ReceptionSerie).\
                where(ReceptionSerie.serie == self.sn).all()[-1]
        except IndexError:
            doc_repr = 'Not found'
        else:
            try:
                doc_repr = purchase_proforma.invoice.doc_repr
            except AttributeError:
                doc_repr = purchase_proforma.doc_repr

        return (
            description_id_map.inverse[self.item_id],
            self.sn,
            self.problem,
            self.wh_incoming_rma.incoming_rma.lines[0].supp,
            doc_repr,
            self.wh_incoming_rma.incoming_rma.lines[0].cust,
            warehouse_id_map.inverse[self.warehouse_id]
        )



class CreditNoteLine(Base):

    __tablename__ = 'credit_note_lines'

    id = Column(Integer, primary_key=True)
    proforma_id = Column(Integer, ForeignKey('sale_proformas.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    condition = Column(String(50), nullable=False)
    public_condition = Column(String(50), nullable=True)
    spec = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float(precision=32, decimal_return_scale=None), nullable=False)
    tax = Column(Integer, nullable=False)
    sn = Column(String(100), nullable=False)

    proforma = relationship(
        'SaleProforma',
        backref=backref(
            'credit_note_lines',
            cascade='delete-orphan, delete, save-update',
        )
    )

    item = relationship('Item', uselist=False)

    def __init__(self, wh_line):
        self.item_id = wh_line.item_id
        self.condition = wh_line.condition
        self.public_condition = wh_line.public_condition
        self.spec = wh_line.spec
        self.quantity = 1
        self.tax = 0
        self.price = -wh_line.price
        self.sn = wh_line.sn

    def __repr__(self):
        return f'item_id = {self.item_id}'


class IncomingRma(Base):

    __tablename__ = 'incoming_rmas'

    id = Column(Integer, primary_key=True)

    date = Column(Date, nullable=True)

    wh_incoming_rma = relationship(

        'WhIncomingRma', uselist=False, back_populates='incoming_rma'

    )



class IncomingRmaLine(Base):

    __tablename__ = 'incoming_rma_lines'

    id = Column(Integer, primary_key=True)
    incoming_rma_id = Column(Integer, ForeignKey('incoming_rmas.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    condition = Column(String(50), nullable=False)
    spec = Column(String(50), nullable=False)

    sn = Column(String(100), nullable=False)
    supp = Column(String(100), nullable=False)
    recpt = Column(Date, nullable=True)
    wtyendsupp = Column(Date, nullable=False)
    purchas = Column(String(255), nullable=True)
    defas = Column(String(255), nullable=True)
    soldas = Column(String(255), nullable=True)
    public = Column(String(100), nullable=True)
    cust = Column(String(100), nullable=False)
    saledate = Column(Date, nullable=True)
    exped = Column(Date, nullable=True)
    wtyendcust = Column(Date, nullable=True)
    problem = Column(String(100), nullable=True)
    accepted = Column(Boolean, default=False, nullable=True)
    why = Column(String(100), nullable=True)
    price = Column(Float(precision=32, decimal_return_scale=None), nullable=False)
    cust_id = Column(Integer, nullable=False)
    agent_id = Column(Integer, nullable=False)

    incoming_rma = relationship(
        'IncomingRma',
        backref=backref(
            'lines',
            cascade='delete-orphan, delete, save-update'
        )
    )

    def __repr__(self):
        cls_name = self.__class__.__name__
        s = f"{cls_name}(sn={self.sn})"
        return s

    # This two method enables set difference
    # def __hash__(self):
    #     return hash(self.sn)
    #
    # def __eq__(self, other):
    #     return self.sn == other.sn

    @classmethod
    def from_sn(cls, sn):
        self = cls()
        self.sn = sn
        try:
            reception_serie = session.query(ReceptionSerie). \
                join(ReceptionLine).join(Reception).join(PurchaseProforma).join(Partner). \
                where(ReceptionSerie.serie == sn).all()[-1]

        except IndexError:
            raise ValueError('Serie not found in receptions')

        try:
            expedition_serie = session.query(ExpeditionSerie). \
                join(ExpeditionLine).join(Expedition).join(SaleProforma).join(Partner). \
                where(ExpeditionSerie.serie == sn).all()[-1]
        except IndexError:
            raise ValueError('Serie not found in expeditions')

        if reception_serie is not None:
            self.recpt = reception_serie.created_on.date()
            self.supp = reception_serie.line.reception.proforma.partner_name
            self.wtyendsupp = self.recpt + timedelta(reception_serie.line.reception.proforma.warranty)

            line = reception_serie.line
            self.purchas = ', '.join((
                line.description or line.item.clean_repr,
                line.condition,
                line.spec
            ))

            self.defas = ', '.join((
                reception_serie.item.clean_repr,
                reception_serie.condition,
                reception_serie.spec
            ))

            if expedition_serie is not None:
                self.item_id = expedition_serie.line.item_id
                self.condition = expedition_serie.line.condition
                self.spec = expedition_serie.line.spec

                self.soldas = ', '.join((
                    expedition_serie.line.item.clean_repr,
                    expedition_serie.line.condition,
                    expedition_serie.line.spec
                ))
                self.public = expedition_serie.line.showing_condition
                self.cust = expedition_serie.line.expedition.proforma.partner_name
                self.cust_id = expedition_serie.line.expedition.proforma.partner_object.id
                self.agent_id = expedition_serie.line.expedition.proforma.agent.id
                try:
                    self.saledate = expedition_serie.line.expedition.proforma.invoice.date
                except AttributeError:
                    self.saledate = expedition_serie.line.expedition.proforma.date
                self.exped = expedition_serie.created_on.date()
                self.wtyendcust = self.exped + timedelta(expedition_serie.line.expedition.proforma.warranty)

                self.sold_to = expedition_serie.line.expedition.proforma.partner_name

                self.problem = ''
                self.why = ''
                self.accepted = False

                for line in expedition_serie.line.expedition.proforma.lines or \
                            expedition_serie.line.expedition.proforma.advanced_lines:
                    if all((
                            line.item_id == expedition_serie.line.item_id,
                            line.condition == expedition_serie.line.condition,
                            line.spec == expedition_serie.line.spec
                    )):
                        self.price = line.price
                        break
                else:
                    self.price = -1332.0

        return self


def create_init_data():
    spec = Spec('Mix')
    condition = Condition('Mix')

    session.add(spec)
    session.add(condition)

    session.commit()


def correct_mask():
    for row in session.query(ImeiMask.origin_id).distinct():

        purchase_proforma = session.query(PurchaseProforma).join(PurchaseProformaLine). \
            where(PurchaseProformaLine.id == row.origin_id).first()
        if purchase_proforma.completed:
            if all(
                    sale.completed or sale.cancelled for sale in session.query(SaleProforma).join(AdvancedLine).\
                    where(AdvancedLine.origin_id == row.origin_id)
            ):
                stmt = delete(ImeiMask).where(ImeiMask.origin_id == row.origin_id)
                session.execute(stmt)
    try:
        session.commit()
    except Exception as ex:
        session.rollback()
        raise


def company_name():
    return 'Euromedia Investment Group'


def year():
    return '2022'
