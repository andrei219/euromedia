import typing
import math
import os

from pathlib import Path
from collections import namedtuple
from itertools import groupby, product
from operator import attrgetter
from datetime import datetime, timedelta



from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from sqlalchemy.exc import InvalidRequestError, NoResultFound
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

import utils
import db
from utils import description_id_map
from exceptions import SeriePresentError

# COLORS:
# RED FOR CANCELLED
# GREEN FOR COMPLETED
# ORANGE FOR EMPTY OR PARTIAL
# YELLOW FOR OVERFLOW
RED, GREEN, YELLOW, ORANGE = '#FF7F7F', '#90EE90', '#FFFF66', '#FFD580'


class BaseTable:

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self._headerData[section]

    def columnCount(self, index=QModelIndex()):
        return len(self._headerData)

    def rowCount(self, index=QModelIndex()):
        return len(getattr(self, self.name))


def computeCreditAvailable(partner_id):
    max_credit = db.session.query(db.Partner.amount_credit_limit). \
        where(db.Partner.id == partner_id).scalar()

    total = db.session.query(func.sum(db.PurchaseProformaLine.quantity * db.PurchaseProformaLine.price)). \
        select_from(db.Partner, db.PurchaseProforma, db.PurchaseProformaLine). \
        where(db.PurchaseProformaLine.proforma_id == db.PurchaseProforma.id). \
        where(db.PurchaseProforma.partner_id == db.Partner.id). \
        where(db.Partner.id == partner_id).scalar()

    paid = db.session.query(func.sum(db.PurchasePayment.amount)).select_from(db.Partner,
                                                                             db.PurchaseProforma,
                                                                             db.PurchasePayment).where(
        db.PurchaseProforma.partner_id == db.Partner.id). \
        where(db.PurchasePayment.proforma_id == db.PurchaseProforma.id). \
        where(db.Partner.id == partner_id).scalar()

    credit_taken = db.session.query(func.sum(db.PurchaseProforma.credit_amount)). \
        where(db.PurchaseProforma.partner_id == partner_id).scalar()

    # Protect against None results from partners with no credits.
    if max_credit is None:
        max_credit = 0
    if total is None:
        total = 0
    if paid is None:
        paid = 0
    if credit_taken is None:
        credit_taken = 0

    return max_credit + paid - total - credit_taken


# Proformas utils::


# Utils for sales:
# Payments:
def sale_total_debt(proforma):
    return sum(line.quantity * line.price for line in proforma.lines) or \
           sum(line.quantity * line.price for line in proforma.advanced_lines)


def sale_total_paid(proforma):
    return sum(payment.amount for payment in proforma.payments)


def sale_not_paid(proforma):
    return math.isclose(sale_total_paid(proforma), 0)


def sale_partially_paid(proforma):
    return 0 < sale_total_paid(proforma) < sale_total_debt(proforma)


def sale_fully_paid(proforma):
    return math.isclose(sale_total_paid(proforma), sale_total_debt(proforma))


def sale_overpaid(proforma):
    return 0 < sale_total_debt(proforma) < sale_total_paid(proforma)


# Warehouse:
def sale_total_quantity(proforma):
    return sum(line.quantity for line in proforma.lines if line.item_id) or \
           sum(line.quantity for line in proforma.advanced_lines if line.item_id)


def expedition_total_quantity(expedition):
    return sum(line.quantity for line in expedition.lines)


def sale_total_processed(proforma):
    expedition = proforma if isinstance(proforma, db.Expedition) else proforma.expedition
    try:
        return sum(1
                   for line in expedition.lines
                   for serie in line.series)
    except AttributeError:
        return 0


def sale_empty(proforma):
    return sale_total_processed(proforma) == 0


def sale_partially_processed(proforma):
    return 0 < sale_total_processed(proforma) < sale_total_quantity(proforma)


def sale_completed(proforma):
    return sale_total_processed(proforma) == sale_total_quantity(proforma)


def sale_overflowed(proforma):
    return 0 < sale_total_quantity(proforma) < sale_total_processed(proforma)


# Purchase Proforma Utils:
# Reuse method sales, simetric in payments
def purchase_total_debt(proforma):
    return sum(line.quantity * line.price for line in proforma.lines)


def purchase_total_paid(proforma):
    return sale_total_paid(proforma)


def purchase_not_paid(proforma):
    return math.isclose(purchase_total_paid(proforma), 0)


def purchase_partially_paid(proforma):
    return 0 < purchase_total_paid(proforma) < purchase_total_debt(proforma)


def purchase_fully_paid(proforma):
    return math.isclose(purchase_total_paid(proforma), purchase_total_debt(proforma))


def purchase_overpaid(proforma):
    return 0 < purchase_total_debt(proforma) < purchase_total_paid(proforma)


# Warehouse:
def purchase_total_quantity(proforma):
    return sum(
        line.quantity for line in proforma.lines
        if line.item_id or line.description in utils.descriptions
    )


def purchase_total_processed(proforma):
    # Method called with proforma object and reception object:
    # Type-check first
    reception = proforma if isinstance(proforma, db.Reception) else proforma.reception
    try:
        return sum(1
                   for line in reception.lines
                   for serie in line.series
                   )
    except AttributeError:
        return 0


def purchase_empty(proforma):
    return purchase_total_processed(proforma) == 0


def purchase_partially_processed(proforma):
    return 0 < purchase_total_processed(proforma) < purchase_total_quantity(proforma)


def purchase_completed(proforma):
    return purchase_total_processed(proforma) == purchase_total_quantity(proforma)


def reception_overflowed(reception):
    for line in reception.lines:
        try:
            if len(line.series) > line.quantity:
                return True
        except AttributeError:
            raise
    return False


def purchase_overflowed(proforma):
    return reception_overflowed(proforma.reception)


# return 0 < purchase_total_quantity(proforma) < purchase_total_processed(proforma)


def sale_completed(proforma):
    return sale_total_processed(proforma) == sale_total_quantity(proforma)


def stock_gap():
    return not all(
        sale_completed(proforma)
        for proforma in db.session.query(db.SaleProforma)
            .where(db.SaleProforma.cancelled == False)
            .order_by(db.SaleProforma.id.desc())
    )


class AgentModel(QtCore.QAbstractTableModel):
    ID, NAME, PHONE, EMAIL, COUNTRY, ACTIVE = 0, 1, 2, 3, 4, 5

    def __init__(self, search_key=None):
        super().__init__()
        self._headerData = ['Code', 'Agent', 'Phone Nº', 'E-mail', 'Country', 'Active']
        query = db.session.query(db.Agent)

        if search_key:
            query = query.filter(
                or_(
                    db.Agent.fiscal_name.contains(search_key),
                    db.Agent.fiscal_number.contains(search_key),
                    db.Agent.email.contains(search_key),
                    db.Agent.phone.contains(search_key),
                    db.Agent.country.contains(search_key)
                )
            )

        self.agents = query.all()

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or \
                not (0 <= index.row() <= len(self.agents)):
            return
        agent = self.agents[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == AgentModel.ID:
                return agent.id
            elif column == AgentModel.NAME:
                return agent.fiscal_name
            elif column == AgentModel.PHONE:
                return agent.phone
            elif column == AgentModel.EMAIL:
                return agent.email
            elif column == AgentModel.COUNTRY:
                return agent.country
            elif column == AgentModel.ACTIVE:
                return 'Yes' if agent.active else 'No'
        elif role == Qt.DecorationRole:
            if column == AgentModel.ACTIVE:
                if agent.active:
                    return QtGui.QIcon(':\greentick')
                else:
                    return QtGui.QIcon(':\cross')
        elif role == Qt.TextAlignmentRole:
            if column == AgentModel.ID:
                return Qt.AlignVCenter | Qt.AlignHCenter

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self._headerData[section]

    def rowCount(self, index=QModelIndex()):
        return len(self.agents)

    def columnCount(self, index=QModelIndex()):
        return 6

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsEditable

    def add(self, agent):
        db.session.add(agent)
        try:
            db.session.commit()
            self.agents.append(agent)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def update(self, agent):
        # for old_agent in self.agents:
        # 	if old_agent.id == agent.id:
        # 		break
        # old_agent.fiscal_name = agent.fiscal_name
        # old_agent.fiscal_number = agent.fiscal_number
        # old_agent.email = agent.email
        # old_agent.phone = agent.phone
        # old_agent.active = agent.active
        # old_agent.country = agent.country
        # old_agent.fixed_salary = agent.fixed_salary
        # old_agent.from_profit = agent.from_profit
        # old_agent.from_turnover = agent.from_turnover
        # old_agent.fixed_perpiece = agent.fixed_perpiece
        # old_agent.bank_name = agent.bank_name
        # old_agent.iban = agent.iban
        # old_agent.swift = agent.swift
        # old_agent.bank_address = agent.bank_address
        # old_agent.bank_postcode = agent.bank_postcode
        # old_agent.bank_city = agent.bank_city
        # old_agent.bank_state = agent.bank_state
        # old_agent.bank_country = agent.bank_country
        # old_agent.bank_routing = agent.bank_routing

        # try:
        # 	db.session.commit()
        # 	print('commit executed')
        # except:
        # 	db.session.rollback()
        # 	raise
        # self.dataChanged.emit(QModelIndex(), QModelIndex())

        try:
            self.layoutAboutToBeChanged.emit()
            db.session.commit()
            self.layoutChanged.emit()

        except:
            db.session.rollback()
            raise

    def delete(self, index):
        if not index.isValid():
            return
        row = index.row()
        candidate_agent = self.agents[row]
        db.session.delete(candidate_agent)
        try:
            db.session.commit()
            # Dont check ValueError, this code executes only if self.agents is populated
            self.agents.remove(candidate_agent)
            self.layoutChanged.emit()

        except IntegrityError:
            db.session.rollback()
            raise

    def sort(self, section, order):
        attr = {AgentModel.NAME: 'fiscal_name', AgentModel.EMAIL: 'email', \
                AgentModel.COUNTRY: 'country'}.get(section)
        if attr:
            self.layoutAboutToBeChanged.emit()
            self.agents = sorted(self.agents, key=operator.attrgetter(attr), \
                                 reverse=True if order == Qt.DescendingOrder else False)
            self.layoutChanged.emit()


dropbox_base = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Dropbox', 'Programa')


def move(origin, dest, copy=False):
    origin = origin.replace('/', '\\')
    dest = dest.replace('/', '\\')
    with open(origin, "rb") as od, open(dest, "wb") as dd:
        dd.write(od.read())
    if not copy:
        os.remove(origin)


class DocumentModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.document_names = list(filter(self.key, os.listdir(self.path)))

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.document_names)

    def add(self, file_path):
        name = Path(file_path).name
        filename = self.prefix + name
        new_location = os.path.join(self.path, filename)
        self.layoutAboutToBeChanged.emit()
        move(file_path, new_location)
        self.document_names.append(filename)
        self.layoutChanged.emit()

    def delete(self, row):
        file = self.document_names[row]
        path = os.path.join(self.path, file)
        try:
            os.remove(path)
            self.document_names.pop(row)
            self.layoutChanged.emit()
        except FileNotFoundError:
            pass

    def export(self, directory, row):
        filename = self.document_names[row]
        origin = os.path.join(self.path, filename)
        dest = os.path.join(directory, filename.replace(self.prefix, ''))
        move(origin, dest, copy=True)

    def key(self, filename: str):
        return filename.startswith(self.prefix)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        filename = self.document_names[index.row()]
        if role == Qt.DisplayRole:
            return filename.replace(self.prefix, '')
        elif role == Qt.DecorationRole:
            return QtGui.QIcon(':\pdf')

    def view(self, row):
        import subprocess
        filename = self.document_names[row]
        filepath = os.path.join(self.path, filename)
        subprocess.Popen((filename,), shell=True)


class AgentsDocumentModel(DocumentModel):

    def __init__(self, agent):
        self.agent = agent
        super().__init__()

    @property
    def path(self):
        path = os.path.join(dropbox_base, db.company_name(), 'Agents')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def prefix(self):
        prefix = str(self.agent.id).zfill(3) + '_'
        for word in self.agent.fiscal_name.split():
            prefix += word[0]
        prefix += '_'
        return prefix


class PartnersDocumentModel(DocumentModel):

    def __init__(self, partner):
        self.partner = partner
        super().__init__()

    @property
    def prefix(self):
        prefix = str(self.partner.id).zfill(6) + '_'
        for word in self.partner.fiscal_name.split():
            prefix += word[0]
        prefix += '_'
        return prefix

    @property
    def path(self):
        path = os.path.join(dropbox_base, db.company_name(), 'Partners')
        if not os.path.exists(path):
            os.makedirs(path)
        return path


number_month_dict = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}

end_path = {
    1: os.path.join('Interior', 'Reg. General'),
    2: os.path.join('Interior', 'ISP'),
    5: os.path.join('Interior', 'REBU'),
    3: os.path.join('Importacion'),
    4: os.path.join('Intracomunitaria', 'Regimen General'),
    6: os.path.join('Intracomunitaria', 'Marginal VAT')
}


class ProformasSalesDocumentModel(DocumentModel):

    def __init__(self, obj):
        self.proforma = obj
        super().__init__()

    @property
    def path(self):
        _type = self.proforma.type
        path = os.path.join(
            dropbox_base,
            db.company_name(),
            'Proformas Emitidas',
            db.year(),
            number_month_dict[self.proforma.date.month],
            'Exportacion' if _type == 3 else end_path[_type]
        )

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def prefix(self):
        return self.proforma.doc_repr + '_'


class ProformasPurchasesDocumentModel(DocumentModel):

    def __init__(self, obj):
        self.proforma = obj
        super().__init__()

    @property
    def path(self):
        path = os.path.join(
            dropbox_base,
            db.company_name(),
            'Proformas Recibidas',
            db.year(),
            number_month_dict[self.proforma.date.month],
            end_path[self.proforma.type]
        )

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def prefix(self):
        return self.proforma.doc_repr + '_'


class InvoicesPurchasesDocumentModel(DocumentModel):

    def __init__(self, obj):
        self.invoice = obj.invoice
        super().__init__()

    @property
    def path(self):
        path = os.path.join(
            dropbox_base,
            db.company_name(),
            'Facturas Recibidas',
            db.year(),
            number_month_dict[self.invoice.date.month],
            end_path[self.invoice.type]
        )
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def prefix(self):
        return self.invoice.doc_repr + '_'


class InvoicesSalesDocumentModel(DocumentModel):

    def __init__(self, obj):
        self.invoice = obj.invoice
        super().__init__()

        print(self.invoice.doc_repr)

    @property
    def path(self):
        _type = self.invoice.type
        path = os.path.join(
            dropbox_base,
            db.company_name(),
            'Facturas Emitidas',
            db.year(),
            number_month_dict[self.invoice.date.month],
            'Exportacion' if _type == 3 else end_path[_type]
        )

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def prefix(self):
        return self.invoice.doc_repr


class PartnerModel(QtCore.QAbstractTableModel):
    CODE, TRADING_NAME, FISCAL_NAME, FISCAL_NUMBER, COUNTRY, CONTACT, PHONE, EMAIL, ACTIVE = \
        0, 1, 2, 3, 4, 5, 6, 7, 8

    def __init__(self, search_key=None):
        super().__init__()

        self._headerData = ['Code', 'Trading Name', 'Fiscal Name', 'Fiscal Number', 'Country', 'Contact', \
                            'Phone', 'E-mail', 'Active']
        query = db.session.query(db.Partner).outerjoin(db.PartnerContact)
        if search_key:
            query = query.filter(
                or_(
                    db.Partner.fiscal_name.contains(search_key),
                    db.Partner.fiscal_number.contains(search_key),
                    db.Partner.trading_name.contains(search_key),
                    db.Partner.billing_country.contains(search_key),
                    db.Partner.shipping_country.contains(search_key),
                )
            )

        self.partners = query.all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        partner = self.partners[index.row()]
        partner: db.Partner
        column = index.column()
        if role == Qt.DisplayRole:
            return self.col_to_data_map(column, partner)
        elif role == Qt.DecorationRole:
            if column == PartnerModel.ACTIVE:
                return QtGui.QIcon(':\greentick') if partner.active else \
                    QtGui.QIcon(':\cross')

    def columnCount(self, index=QModelIndex()):
        return len(self._headerData)

    def rowCount(self, index=QModelIndex()):
        return len(self.partners)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self._headerData[section]

    def sort(self, section, order):
        attr = {
            PartnerModel.CODE: 'id',
            PartnerModel.FISCAL_NAME: 'fiscal_name',
            PartnerModel.FISCAL_NUMBER: 'fiscal_number',
            PartnerModel.TRADING_NAME: 'trading_name',
            PartnerModel.COUNTRY: 'billing_country'
        }.get(section)

        if attr:
            self.layoutAboutToBeChanged.emit()
            self.partners.sort(key=operator.attrgetter(attr), \
                               reverse=True if Qt.AscendingOrder else False)
            self.layoutChanged.emit()

    def add(self, partner):
        db.session.add(partner)
        try:
            db.session.commit()
            self.partners.append(partner)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def delete(self, index):
        if not index.isValid():
            return
        row = index.row()
        candidate_partner = self.partners[row]
        db.session.delete(candidate_partner)
        try:
            db.session.commit()
            self.partners.remove(candidate_partner)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def col_to_data_map(self, col, partner: db.Partner):
        return {
            PartnerModel.CODE: partner.id,
            PartnerModel.TRADING_NAME: partner.trading_name,
            PartnerModel.FISCAL_NAME: partner.fiscal_name,
            PartnerModel.FISCAL_NUMBER: partner.fiscal_number,
            PartnerModel.COUNTRY: partner.billing_country,
            PartnerModel.CONTACT: partner.contacts[0].name,
            PartnerModel.PHONE: partner.contacts[0].phone,
            PartnerModel.EMAIL: partner.contacts[0].email,
            PartnerModel.ACTIVE: 'YES' if partner.active else 'NO'
        }.get(col)


class PartnerContactModel(QtCore.QAbstractTableModel):
    NAME, POSITION, PHONE, EMAIL, NOTE = 0, 1, 2, 3, 4

    def __init__(self, view, contacts):
        super().__init__()
        self._headerData = ['Name', 'Position', 'Phone', 'Email', 'Note']
        self.contacts = contacts
        self.view = view

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() and 0 <= index.row() < len(self.contacts):
            return
        if role != Qt.DisplayRole:
            return
        row, col = index.row(), index.column()
        contact = self.contacts[row]
        if col == PartnerContactModel.NAME:
            return contact.name
        elif col == PartnerContactModel.POSITION:
            return contact.position
        elif col == PartnerContactModel.PHONE:
            return contact.phone
        elif col == PartnerContactModel.EMAIL:
            return contact.email
        elif col == PartnerContactModel.NOTE:
            return contact.note

    def rowCount(self, index=Qt.DisplayRole):
        return len(self.contacts)

    def columnCount(self, index=Qt.DisplayRole):
        return 5

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headerData[section]

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.contacts):
            contact = self.contacts[index.row()]
            column = index.column()
            if column == PartnerContactModel.NAME:
                contact.name = value
            elif column == PartnerContactModel.POSITION:
                contact.position = value
            elif column == PartnerContactModel.PHONE:
                contact.phone = value
            elif column == PartnerContactModel.EMAIL:
                contact.email = value
            elif column == PartnerContactModel.NOTE:
                contact.note = value
            self.dataChanged.emit(index, index)
            self.view.resizeColumnToContents(column)
            return True
        return False

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        contact = db.PartnerContact('', '', '', '', '')
        self.contacts.insert(position, contact)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.contacts.pop(position)
        self.endRemoveRows()
        return True


class SaleInvoiceModel(QtCore.QAbstractTableModel):
    TYPE_NUM, DATE, PROFORMA = 0, 1, 16

    def __init__(self, search_key=None, filters=None, last=10):
        super().__init__()
        self.parent_model = SaleProformaModel(
            filters=filters,
            search_key=search_key,
            proxy=True,
            last=last
        )

        self.parent_model._headerData.remove('Inv.')

    def rowCount(self, index=QModelIndex()):
        return self.parent_model.rowCount(index)

    def columnCount(self, index=QModelIndex()):
        return self.parent_model.columnCount(index)

    def headerCount(self, index=QModelIndex()):
        return self.parent_model.headerCount(index)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return self.parent_model.headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        proforma = self.invoices[row]
        if role == Qt.DisplayRole:
            if column == self.TYPE_NUM:
                return str(proforma.invoice.type) + '-' + \
                       str(proforma.invoice.number).zfill(6)
            elif column == self.PROFORMA:
                return str(proforma.type) + '-' + str(proforma.number).zfill(6)

            elif column == self.DATE:
                return proforma.invoice.date.strftime('%d/%m/%Y')

            else:
                return self.parent_model.data(index, role)

        return self.parent_model.data(index, role)

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == self.__class__.TYPE_NUM:
            self.layoutAboutToBeChanged.emit()
            self.invoices.sort(
                key=lambda p: (p.invoice.type, p.invoice.number),
                reverse=reverse
            )
            self.layoutChanged.emit()

        elif section == self.__class__.PROFORMA:
            self.layoutAboutToBeChanged.emit()
            self.invoices.sort(
                key=lambda p: (p.type, p.number),
                reverse=reverse
            )
            self.layoutChanged.emit()
        else:

            self.layoutAboutToBeChanged.emit()
            self.parent_model.sort(section, order)
            self.layoutChanged.emit()

    def ready(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            invoice = self[row]
            invoice.ready = True if not invoice.ready else False

        try:
            db.session.commit()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def __getattr__(self, name):
        if name == 'invoices':
            return self.parent_model.proformas
        else:
            return getattr(self, name)

    def __getitem__(self, index):
        return self.invoices[index]


class PurchaseInvoiceModel(BaseTable, QtCore.QAbstractTableModel):

    TYPENUM, DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, CANCELLED, OWING,\
    TOTAL, EXT, INWH, PROFORMA = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

    def __init__(self, filters=None, search_key=None, last=10):
        super().__init__()
        self._headerData = [
            'Type & Num', 'Date', 'ETA', 'Partner', 'Agent',
            'Financial', 'Logistic', 'Sent', 'Cancelled', 'Owing',
            'Total', 'Ext. Doc.', 'In WH', 'Proforma'
        ]

        self.name = 'invoices'

        query = db.session.query(db.PurchaseInvoice).select_from(
            db.PurchaseProforma, db.Partner, db.Agent
        ).where(
            db.PurchaseProforma.partner_id == db.Partner.id,
            db.PurchaseProforma.agent_id == db.Agent.id,
            db.PurchaseInvoice.id == db.PurchaseProforma.invoice_id,
            db.PurchaseInvoice.date > utils.get_last_date(last)
        )

        if search_key:
            predicates = []
            predicates.extend(
                [
                    db.Partner.fiscal_name.contains(search_key),
                    db.Agent.fiscal_name.conntans(search_key)
                ]
            )
            try:
                date = utils.parse_date(search_key)
            except ValueError:
                pass
            else:
                predicates.extend(
                    [
                        db.PurchaseInvoice.date == date,
                        db.PurchaseInvoice.eta == date
                    ]
                )
            try:
                n = int(search_key)
            except ValueError:
                pass
            else:
                predicates.append(db.PurchaseInvoice.number == n)

            query = query.where(or_(*predicates))

        if filters:
            self.invoices = query.all()

            if filters['types']:
                self.invoices = filter(lambda i:i.type in filters['types'], self.invoices)

            if filters['financial']:
                if 'notpaid' in filters['financial']:
                    self.invoices = filter(lambda i : i.proforma.notpaid, self.invoices)

                if 'fullypaid' in filters['financial']:
                    self.invoices = filter(lambda i:i.proforma.fully_paid, self.invoices)

                if 'partiallypaid' in filters['financial']:
                    self.invoices = filter(lambda i: i.proforma.partially_paid, self.invoices)

            if filters['logistic']:
                if 'overflowed' in filters['logistic']:
                    self.invoices = filter(lambda i: i.proforma.overflowed, self.invoices)
                if 'empty' in filters['logistic']:
                    self.invoices = filter(lambda i:i.proforma.empty, self.invoices)
                if 'partially_processed' in filters['logistic']:
                    self.invoices = filter(lambda i:i.proforma.partially_processed, self.invoices)
                if 'completed' in filters['logistic']:
                    self.invoices = filter(lambda i:i.proforma.completed, self.invoices)

            if filters['shipment']:
                if 'sent' in filters['shipment']:
                    self.invoices = filter(lambda i:i.proforma.sent, self.invoices)

                if 'notsent' in filters['shipment']:
                    self.invoices = filter(lambda i: not i.proforma.sent, self.invoices)

            if isinstance(self.invoices, filter):
                self.invoices = list(self.invoices)

        else:
            self.invoices = query.all()


    def __getitem__(self, index):
        return self.invoices[index].proforma
    
    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        invoice = self.invoices[index.row()]

        if role == Qt.DisplayRole:
            if col == self.TYPENUM:
                return invoice.doc_repr
            elif col == self.DATE:
                return invoice.date.strftime('%d/%m/%Y')
            elif col == self.ETA:
                return invoice.eta.strftime('%d/%m/%Y')
            elif col == self.PARTNER:
                return invoice.proforma.partner.fiscal_name
            elif col == self.AGENT:
                return invoice.proforma.agent.fiscal_name
            elif col == self.FINANCIAL:
                return invoice.proforma.financial_status_string
            elif col == self.LOGISTIC:
                return invoice.proforma.logistic_status_string
            elif col == self.SENT:
                return 'Yes' if invoice.proforma.sent else 'No'
            elif col == self.CANCELLED:
                return 'Yes' if invoice.proforma.cancelled else 'No'
            elif col == self.OWING:
                sign = ' -€' if invoice.proforma.eur_currency else ' $'
                return str(invoice.proforma.owing) + sign
            elif col == self.TOTAL:
                sign = ' -€' if invoice.proforma.eur_currency else ' $'
                return str(invoice.proforma.total_debt) + sign
            elif col == self.INWH:
                return 'Yes' if invoice.proforma.reception is not None else 'No'
            elif col == self.PROFORMA:
                return invoice.proforma.doc_repr
            elif col == self.EXT:
                return invoice.proforma.external

        elif role == Qt.DecorationRole:
            if col == self.FINANCIAL:
                if invoice.proforma.not_paid:
                    return QtGui.QColor(YELLOW)
                elif invoice.proforma.fully_paid:
                    return QtGui.QColor(GREEN)
                elif invoice.proforma.partially_paid:
                    return QtGui.QColor(ORANGE)
                elif invoice.proforma.overpaid:
                    return QtGui.QColor(RED)
            elif col == self.DATE or col == self.ETA:
                return QtGui.QIcon(':\calendar')
            elif col == self.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == self.AGENT:
                return QtGui.QIcon(':\\agents')

            elif col == self.LOGISTIC:
                if invoice.proforma.empty:
                    return QtGui.QColor(YELLOW)
                elif invoice.proforma.overflowed:
                    return QtGui.QColor(RED)
                elif invoice.proforma.partially_processed:
                    return QtGui.QColor(ORANGE)
                elif invoice.proforma.completed:
                    return QtGui.QColor(GREEN)

            elif col == self.CANCELLED:
                return QtGui.QColor(RED) if invoice.proforma.cancelled else QtGui.QColor(GREEN)

            elif col == PurchaseProformaModel.SENT:
                return QtGui.QColor(GREEN) if invoice.proforma.sent else QtGui.QColor(RED)



    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == self.TYPENUM:
            self.layoutAboutToBeChanged.emit()
            self.invoices.sort(key=lambda i:(i.type, i.number), reverse=reverse)
            self.layoutChanged.emit()
        else:
            attr = {
                self.DATE:'date',
                self.ETA:'eta',
                self.AGENT:'proforma.agent.fiscal_name',
                self.PARTNER:'proforma.partner.fiscal_name',
            }.get(section)

            if attr:
                self.layoutAboutToBeChanged.emit()
                self.invoices.sort(key=operator.attrgetter(attr), reverse=reverse)
                self.layoutChanged.emit()



class PurchaseInvoiceModel_old(QtCore.QAbstractTableModel):
    TYPE_NUM, PROFORMA = 0, 13

    def __init__(self, filters=None, search_key=None, last=10):
        super().__init__()
        self.parent_model = PurchaseProformaModel(
            filters=filters,
            search_key=search_key,
            proxy=True,
            last=last
        )

        self.parent_model._headerData.remove('Invoiced')

    def rowCount(self, index=QModelIndex()):
        return self.parent_model.rowCount(index)

    def columnCount(self, index=QModelIndex()):
        return self.parent_model.columnCount(index)

    def headerCount(self, index=QModelIndex()):
        return self.parent_model.headerCount(index)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return self.parent_model.headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        proforma = self.invoices[row]
        if role == Qt.DisplayRole:
            if column == self.__class__.TYPE_NUM:
                return str(proforma.invoice.type) + '-' + \
                       str(proforma.invoice.number).zfill(6)
            elif column == self.__class__.PROFORMA:
                return str(proforma.type) + '-' + str(proforma.number).zfill(6)
            else:
                return self.parent_model.data(index, role)

        return self.parent_model.data(index, role)

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == self.__class__.TYPE_NUM:
            self.layoutAboutToBeChanged.emit()
            self.invoices.sort(
                key=lambda p: (p.invoice.type, p.invoice.number),
                reverse=reverse
            )
            self.layoutChanged.emit()

        elif section == self.__class__.PROFORMA:
            self.layoutAboutToBeChanged.emit()
            self.invoices.sort(
                key=lambda p: (p.type, p.number),
                reverse=reverse
            )
            self.layoutChanged.emit()

        else:
            self.layoutAboutToBeChanged.emit()
            self.parent_model.sort(section, order)
            self.layoutChanged.emit()

    def __getattr__(self, name):
        if name == 'invoices':
            return self.parent_model.proformas
        else:
            return getattr(self, name)

    def __getitem__(self, index):
        return self.invoices[index]


def buildReceptionLine(line, reception):
    reception_line = db.ReceptionLine()

    reception_line.condition = line.condition
    reception_line.spec = line.spec
    reception_line.quantity = line.quantity

    reception_line.item_id = line.item_id
    reception_line.description = line.description

    if reception_line.item_id or reception_line.description in \
            utils.descriptions:
        reception_line.reception = reception
    # reception is attached to session, will cascade-commit the lines.

#
# class PurchaseInvoiceModel_new(BaseTable, QtCore.QAbstractTableModel):
#
#     TYPENUM, DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, CANCELLED, \
#     OWING, TOTAL, EXTERNAL, INWH, FROM = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
#
#
#     def __init__(self, filters=None, search_key=None, last=10):
#         super().__init__()
#         self._headerData = [
#             'Type & Num', 'Date', 'Eta', 'Partner', 'Agent', 'Financial',
#             'Logistic', 'Sent', 'Cancelled', 'Owing', 'Total', 'External',
#             'In WH', 'From Proforma'
#         ]
#         self.name = 'invoices'
#
#         query = db.session.query(db.PurchaseInvoice).join(db.PurchaseProforma)\
#             where(db.PurchaseInvoice.date > utils.get_last_date(last))
#
#         if search_key:
#             predicates = []
#             predicates.extend(
#
#             )


class PurchaseProformaModel(BaseTable, QtCore.QAbstractTableModel):
    TYPE_NUM, DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, CANCELLED, \
    OWING, TOTAL, EXTERNAL, INVOICED, IN_WAREHOUSE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

    def __init__(self, filters=None, search_key=None, proxy=False, last=10):
        super().__init__()
        self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', \
                            'Financial', 'Logistic', 'Sent', 'Cancelled', 'Owing', 'Total', 'External Doc.',
                            'Invoiced', 'In Warehouse']
        self.name = 'proformas'
        self.proxy = proxy

        query = db.session.query(db.PurchaseProforma).select_from(db.Agent, db.Partner). \
            where(
            db.Agent.id == db.PurchaseProforma.agent_id,
            db.Partner.id == db.PurchaseProforma.partner_id
        )

        if proxy:
            self._headerData.append('From proforma')

            query = db.session.query(db.PurchaseProforma).\
                join(db.PurchaseInvoice, db.PurchaseProforma.invoice_id == db.PurchaseInvoice.id, isouter=True).\
                join(db.Partner, db.Partner.id == db.PurchaseProforma.partner_id).\
                join(db.Agent, db.Agent.id == db.PurchaseProforma.agent_id)

            query = query.where(db.PurchaseProforma.invoice_id != None)
            query = query.where(db.PurchaseInvoice.date > utils.get_last_date(last))
        else:
            query = query.where(db.PurchaseProforma.date > utils.get_last_date(last))

        if search_key:
            predicates = []
            predicates.extend(
                [
                    db.Agent.fiscal_name.contains(search_key),
                    db.Partner.fiscal_name.contains(search_key)
                ]
            )

            try:
                date = utils.parse_date(search_key)
            except ValueError:
                pass
            else:
                predicates.extend(
                    [
                        db.PurchaseProforma.eta == date,
                        db.PurchaseProforma.date == date
                    ]
                )
            try:
                n = int(search_key)
            except ValueError:
                pass
            else:
                predicates.append(db.PurchaseProforma.number == n)

            query = query.where(or_(*predicates))

        if filters:
            self.proformas = query.all()

            if filters['types']:
                self.proformas = filter(lambda p: p.type in filters['types'], self.proformas)

            if filters['financial']:
                if 'notpaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.not_paid, self.proformas)
                if 'fullypaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.fully_paid, self.proformas)
                if 'partiallypaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.partially_paid, self.proformas)

            if filters['logistic']:
                if 'overflowed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.overflowed, self.proformas)
                if 'empty' in filters['logistic']:
                    self.proformas = filter(lambda p: p.empty, self.proformas)
                if 'partially_processed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.partially_processed, self.proformas)
                if 'completed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.completed, self.proformas)

            if filters['shipment']:
                if 'sent' in filters['shipment']:
                    self.proformas = filter(lambda p: p.sent, self.proformas)
                if 'notsent' in filters['shipment']:
                    self.proformas = filter(lambda p: not p.sent, self.proformas)

            if filters['cancelled']:
                if 'cancelled' in filters['cancelled']:
                    self.proformas = filter(lambda p: p.cancelled, self.proformas)
                if 'notcancelled' in filters['cancelled']:
                    self.proformas = filter(lambda p: not p.cancelled, self.proformas)

            if isinstance(self.proformas, filter):
                self.proformas = list(self.proformas)
        else:
            self.proformas = query.all()


    def __getitem__(self, index):
        return self.proformas[index]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        proforma = self.proformas[row]

        if role == Qt.DisplayRole:
            if col == PurchaseProformaModel.TYPE_NUM:
                s = str(proforma.type) + '-' + str(proforma.number).zfill(6)
                return s
            elif col == PurchaseProformaModel.DATE:
                if self.proxy:
                    return proforma.invoice.date.strftime('%d/%m/%Y')
                else:
                    return proforma.date.strftime('%d/%m/%Y')
            elif col == PurchaseProformaModel.ETA:
                if self.proxy:
                    return proforma.invoice.eta.strftime('%d/%m/%Y')
                else:
                    return proforma.eta.strftime('%d/%m/%Y')

            elif col == self.INVOICED:
                return 'Yes' if proforma.invoice is not None else 'No'

            elif col == self.IN_WAREHOUSE:
                return 'Yes' if proforma.reception is not None else 'No'

            elif col == PurchaseProformaModel.PARTNER:
                return proforma.partner.fiscal_name
            elif col == PurchaseProformaModel.AGENT:
                return proforma.agent.fiscal_name
            elif col == PurchaseProformaModel.FINANCIAL:
                return proforma.financial_status_string

            elif col == PurchaseProformaModel.LOGISTIC:
                return proforma.logistic_status_string

            elif col == PurchaseProformaModel.SENT:
                return "Yes" if proforma.sent else "No"

            elif col == PurchaseProformaModel.CANCELLED:
                return 'Yes' if proforma.cancelled else 'No'

            elif col == PurchaseProformaModel.OWING:
                sign = ' -€' if proforma.eur_currency else ' $'
                owing = purchase_total_debt(proforma) - purchase_total_paid(proforma)
                return str(owing) + sign

            elif col == PurchaseProformaModel.TOTAL:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(proforma.total_debt) + sign

            elif col == self.EXTERNAL:
                return str(proforma.external)

        elif role == Qt.DecorationRole:
            if col == PurchaseProformaModel.FINANCIAL:
                if proforma.not_paid:
                    return QtGui.QColor(YELLOW)
                elif proforma.fully_paid:
                    return QtGui.QColor(GREEN)
                elif proforma.partially_paid:
                    return QtGui.QColor(ORANGE)
                elif proforma.overpaid:
                    return QtGui.QColor(RED)

            elif col == PurchaseProformaModel.DATE or col == PurchaseProformaModel.ETA:
                return QtGui.QIcon(':\calendar')
            elif col == PurchaseProformaModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == PurchaseProformaModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif col == PurchaseProformaModel.LOGISTIC:
                if purchase_empty(proforma):
                    return QtGui.QColor(YELLOW)
                elif purchase_overflowed(proforma):
                    return QtGui.QColor(RED)
                elif purchase_partially_processed(proforma):
                    return QtGui.QColor(ORANGE)
                elif purchase_completed(proforma):
                    return QtGui.QColor(GREEN)
            elif col == PurchaseProformaModel.CANCELLED:
                return QtGui.QColor(RED) if proforma.cancelled else \
                    QtGui.QColor(GREEN)
            elif col == PurchaseProformaModel.SENT:
                return QtGui.QColor(GREEN) if proforma.sent else \
                    QtGui.QColor(RED)

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == PurchaseProformaModel.TYPE_NUM:
            self.layoutAboutToBeChanged.emit()
            self.proformas.sort(key=lambda p: (p.type, p.number), reverse=reverse)
            self.layoutChanged.emit()

        else:
            attr = {
                PurchaseProformaModel.DATE: 'date',
                PurchaseProformaModel.PARTNER: 'partner.trading_name',
                PurchaseProformaModel.AGENT: 'agent.fiscal_name',
                PurchaseProformaModel.SENT: 'sent',
                PurchaseProformaModel.ETA: 'eta'
            }.get(section)

            if attr:
                self.layoutAboutToBeChanged.emit()
                self.proformas.sort(key=operator.attrgetter(attr), reverse=reverse)
                self.layoutChanged.emit()

    def add(self, proforma):
        proforma.number = self.nextNumberOfType(proforma.type)
        db.session.add(proforma)
        try:
            db.session.commit()
            self.layoutAboutToBeChanged.emit()
            self.proformas.append(proforma)
            self.layoutChanged.emit()
        except IntegrityError:
            db.session.rollback()
            try:
                proforma.number = self.nextNumberOfType(proforma.type)
                db.session.add(proforma)
                db.session.commit()
                self.layoutAboutToBeChanged.emit()
                self.proformas.append(proforma)
                self.layoutChanged.emit()

            except:
                db.session.rollback()
                raise

    def nextNumberOfType(self, type):
        Session = db.sessionmaker(bind=db.get_engine())
        with Session.begin() as session:
            current_num = db.session.query(func.max(db.PurchaseProforma.number)). \
                where(db.PurchaseProforma.type == type).scalar()
            return 1 if current_num is None else current_num + 1

    def cancel(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            p = self.proformas[row]
            if not p.cancelled:
                p.cancelled = True
        try:
            # Update advanced lines depending on this purchase
            ids = [line.id for line in p.lines]
            db.session.query(db.AdvancedLine). \
                where(db.AdvancedLine.origin_id.in_(ids)). \
                update({db.AdvancedLine.quantity: 0})

            db.session.commit()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def associateInvoice(self, proforma):
        current_num = db.session.query(func.max(db.PurchaseInvoice.number)). \
            where(db.PurchaseInvoice.type == proforma.type).scalar()
        if current_num:
            next_num = current_num + 1
        else:
            next_num = 1
        proforma.invoice = db.PurchaseInvoice(proforma.type, next_num)
        try:
            db.session.commit()
            return proforma.invoice
        except:
            db.session.rollback()
            raise

    def ship(self, proforma, tracking=None):
        if tracking:
            proforma.tracking = tracking

        proforma.sent = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def toWarehouse(self, proforma, note):
        reception = db.Reception(proforma, note)
        db.session.add(reception)

        for line in proforma.lines:
            buildReceptionLine(line, reception)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def updateWarehouse(self, proforma):

        if proforma.reception is None:
            return False

        warehouse_lines = set(proforma.reception.lines)
        proforma_lines = set(proforma.lines)

        for line in warehouse_lines.difference(proforma_lines):
            line.quantity = 0
            if len(line.series) == 0:
                db.session.delete(line)

        for line in proforma_lines.difference(warehouse_lines):
            if line.item_id or line.description in utils.descriptions:
                buildReceptionLine(line, proforma.reception)

        for proforma_line in proforma_lines:
            for reception_line in proforma.reception.lines:
                if reception_line == proforma_line:
                    reception_line.quantity = proforma_line.quantity
        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise


def export_expedition(expediton, file_path):
    pass


def item_key(line):
    return line.item_id in utils.description_id_map.inverse


def line_with_stock_key(line):
    if line.item_id:
        return True
    else:
        if isinstance(line, db.AdvancedLine):
            if line.free_description:
                return False
            else:
                return True
    return False


def build_associated_reception(sale_proforma):
    try:
        origin_id = line = sale_proforma.advanced_lines[0].origin_id
    except IndexError:
        return
    else:
        proforma = db.session.query(
            db.PurchaseProforma
        ).join(db.PurchaseProformaLine).where(
            db.PurchaseProformaLine.id == origin_id
        ).first()

    reception = db.Reception(proforma, note='Created automatically')
    db.session.add(reception)

    for line in proforma.lines:
        buildReceptionLine(line, reception)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


class SaleProformaModel(BaseTable, QtCore.QAbstractTableModel):
    TYPE_NUM, DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, \
    CANCELLED, OWING, TOTAL, ADVANCED, DEFINED, READY, EXTERNAL, IN_WAREHOUSE, \
    WARNING, INVOICED = \
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16

    def __init__(self, search_key=None, filters=None, proxy=False, last=10):
        super().__init__()
        self._headerData = ['Type & Num', 'Date', 'Partner', 'Agent', \
                            'Financial', 'Logistic', 'Sent', 'Cancelled',
                            'Owes', 'Total', 'Presale', 'Defined', 'Ready To Go',
                            'External Doc.', 'In WH', 'Warning', 'Inv.'
                            ]

        self.proformas = []
        self.name = 'proformas'
        # query = db.session.query(db.SaleProforma). \
        #     select_from(db.Agent, db.Partner). \
        #     where(
        #     db.Agent.id == db.SaleProforma.agent_id,
        #     db.Partner.id == db.SaleProforma.partner_id,
        #     db.Warehouse.id == db.SaleProforma.warehouse_id
        # )

        query = db.session.query(db.SaleProforma).join(db.Agent).join(db.Partner).\
            join(db.SaleInvoice, isouter=True)

        if proxy:
            self._headerData.append('From proforma')
            query = query.where(db.SaleProforma.invoice != None)
            query = query.where(db.SaleInvoice.date >= utils.get_last_date(last))
        else:

            query = query.where(db.SaleProforma.date >= utils.get_last_date(last))

        if search_key:
            predicates = []
            predicates.extend(
                [
                    db.Agent.fiscal_name.contains(search_key),
                    db.Partner.fiscal_name.contains(search_key),
                    db.Warehouse.description.contains(search_key)
                ]
            )

            try:
                date = utils.parse_date(search_key)
            except ValueError:
                pass
            else:
                predicates.append(db.SaleProforma.date == date)

            try:
                n = int(search_key)
            except:
                pass
            else:
                predicates.append(db.SaleProforma.number == n)

            query = query.where(or_(*predicates))

        if filters:
            self.proformas = query.all()

            if filters['types']:
                self.proformas = filter(lambda p: p.type in filters['types'], self.proformas)

            if filters['financial']:
                if 'notpaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.not_paid, self.proformas)
                if 'fullypaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.fully_paid, self.proformas)
                if 'partiallypaid' in filters['financial']:
                    self.proformas = filter(lambda p: p.partially_paid, self.proformas)

            if filters['logistic']:
                if 'overflowed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.overflowed, self.proformas)
                if 'empty' in filters['logistic']:
                    self.proformas = filter(lambda p: p.empty, self.proformas)
                if 'partially_processed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.partially_processed, self.proformas)
                if 'completed' in filters['logistic']:
                    self.proformas = filter(lambda p: p.completed, self.proformas)

            if filters['shipment']:
                if 'sent' in filters['shipment']:
                    self.proformas = filter(lambda p: p.sent, self.proformas)
                if 'notsent' in filters['shipment']:
                    self.proformas = filter(lambda p: not p.sent, self.proformas)

            if filters['cancelled']:
                if 'cancelled' in filters['cancelled']:
                    self.proformas = filter(lambda p: p.cancelled, self.proformas)
                if 'notcancelled' in filters['cancelled']:
                    self.proformas = filter(lambda p: not p.cancelled, self.proformas)

            if isinstance(self.proformas, filter):
                self.proformas = list(self.proformas)

        else:
            self.proformas = query.all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        proforma = self.proformas[row]

        if role == Qt.DisplayRole:
            if col == self.TYPE_NUM:
                s = str(proforma.type) + '-' + str(proforma.number).zfill(6)
                return s
            elif col == self.DATE:
                return proforma.date.strftime('%d/%m/%Y')
            elif col == self.PARTNER:
                return proforma.partner.fiscal_name
            elif col == self.AGENT:
                return proforma.agent.fiscal_name.split()[0]

            elif col == self.WARNING:
                return proforma.warning

            elif col == self.INVOICED:
                return 'Yes' if proforma.invoice is not None else 'No'

            elif col == self.IN_WAREHOUSE:
                return 'Yes' if proforma.expedition is not None else 'No'

            elif col == self.FINANCIAL:

                if proforma.warehouse_id is None and proforma.applied:
                    return 'Applied'

                if proforma.not_paid:
                    return 'Not Paid'
                elif proforma.fully_paid:
                    return 'Paid'
                elif proforma.partially_paid:
                    return 'Partially Paid'
                elif proforma.overpaid:
                    return 'We Owe'

            elif col == self.LOGISTIC:
                if proforma.empty:
                    return 'Empty'
                elif proforma.overflowed:
                    return 'Overflowed'
                elif proforma.partially_processed:
                    return 'Partially Prepared'
                elif proforma.completed:
                    return 'Completed'

            elif col == self.SENT:
                return 'Yes' if proforma.sent else 'No'
            elif col == self.CANCELLED:
                return 'Yes' if proforma.cancelled else 'No'
            elif col == self.OWING:
                sign = ' -€' if proforma.eur_currency else ' $'
                owes = proforma.total_debt - proforma.total_paid
                return str(owes) + sign
            elif col == self.TOTAL:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(proforma.total_debt) + sign

            elif col == self.ADVANCED:
                return 'Yes' if proforma.advanced_lines else 'No'

            elif col == self.DEFINED:
                line_iter = filter(line_with_stock_key, iter(proforma.lines or proforma.advanced_lines))
                return 'Yes' if all([line.defined for line in line_iter]) else 'No'


            elif col == self.READY:
                return 'Yes' if proforma.ready else 'No'
            elif col == self.EXTERNAL:
                return proforma.external or 'Unknown'

        elif role == Qt.DecorationRole:
            if col == self.FINANCIAL:
                if proforma.warehouse_id is None and proforma.applied:
                    return QtGui.QColor(GREEN)

                if proforma.not_paid:
                    return QtGui.QColor(YELLOW)
                elif proforma.fully_paid:
                    return QtGui.QColor(GREEN)
                elif proforma.partially_paid:
                    return QtGui.QColor(ORANGE)
                elif proforma.overpaid:
                    return QtGui.QColor(YELLOW)

            elif col == self.DATE:
                return QtGui.QIcon(':\calendar')
            elif col == self.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == self.AGENT:
                return QtGui.QIcon(':\\agents')
            elif col == self.LOGISTIC:
                if sale_empty(proforma):
                    return QtGui.QColor(YELLOW)
                elif sale_overflowed(proforma):
                    return QtGui.QColor(RED)
                elif sale_partially_processed(proforma):
                    return QtGui.QColor(ORANGE)
                elif sale_completed(proforma):
                    return QtGui.QColor(GREEN)
            elif col == self.SENT:
                return QtGui.QColor(GREEN if proforma.sent else YELLOW)
            elif col == self.CANCELLED:
                return QtGui.QColor(RED if proforma.cancelled else GREEN)
            elif col == self.READY:
                return QtGui.QColor(GREEN if proforma.ready else YELLOW)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == self.WARNING:
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return
        proforma = self.proformas[index.row()]
        proforma.warning = value
        return True

    def __getitem__(self, index):
        return self.proformas[index]

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == self.TYPE_NUM:
            self.layoutAboutToBeChanged.emit()
            self.proformas.sort(key=lambda p: (p.type, p.number), reverse=reverse)
            self.layoutChanged.emit()

        else:
            attr = {
                self.DATE: 'date',
                self.PARTNER: 'partner.trading_name',
                self.AGENT: 'agent.fiscal_name',
                self.SENT: 'sent',
                self.READY: 'ready'
            }.get(section)

            if attr:
                self.layoutAboutToBeChanged.emit()
                self.proformas.sort(key=operator.attrgetter(attr), reverse=reverse)
                self.layoutChanged.emit()

    def add(self, proforma):
        proforma.number = self.nextNumberOfType(proforma.type)
        db.session.add(proforma)
        try:
            db.session.commit()
            self.layoutAboutToBeChanged.emit()
            self.proformas.append(proforma)
            self.layoutChanged.emit()
        except IntegrityError:
            db.session.rollback()
            try:
                proforma.number = self.nextNumberOfType(proforma.type)
                db.session.add(proforma)
                db.session.commit()
                self.layoutAboutToBeChanged.emit()
                self.proformas.append(proforma)
                self.layoutChanged.emit()
            except:
                db.session.rollback()
                raise

    def nextNumberOfType(self, type):
        Session = db.sessionmaker(bind=db.get_engine())
        with Session.begin() as session:
            current_num = db.session.query(func.max(db.SaleProforma.number)). \
                where(db.SaleProforma.type == type).scalar()
            return 1 if current_num is None else current_num + 1

    def cancel(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            p = self.proformas[row]
            if not p.cancelled:
                p.cancelled = True
        try:
            db.session.commit()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def associateInvoice(self, proforma):
        current_num = db.session.query(func.max(db.SaleInvoice.number)). \
            where(db.SaleInvoice.type == proforma.type).scalar()
        if current_num:
            next_num = current_num + 1
        else:
            next_num = 1
        proforma.invoice = db.SaleInvoice(proforma.type, next_num)
        try:
            db.session.commit()
            return proforma.invoice
        except:
            db.session.rollback()
            raise

    def ready(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            p = self.proformas[row]
            p.ready = True if not p.ready else False
        try:
            db.session.commit()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def ship(self, proforma, tracking):
        proforma.tracking = tracking
        proforma.sent = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def toWarehouse(self, proforma, note):

        fast = True
        expedition = db.Expedition(proforma)
        proforma.warning = note

        if proforma.advanced_lines:
            for line in proforma.advanced_lines:
                if any((
                        line.mixed_description,
                        line.spec == 'Mix',
                        line.condition == 'Mix'
                )) and not line.definitions:
                    raise ValueError("You have to define the presale first")

            # Defined
            else:
                lines = []
                for line in proforma.advanced_lines:
                    if line.definitions:
                        lines.extend(list(definition for definition in line.definitions))
                        if fast:
                            fast = False

                    else:
                        lines.append(line)

            if fast:
                expedition.from_sale_type = db.FAST
                build_associated_reception(proforma)

            else:
                expedition.from_sale_type = db.DEFINED

        else:
            expedition.from_sale_type = db.NORMAL
            lines = proforma.lines

        if not lines:
            return

        db.session.add(expedition)

        for line in lines:
            exp_line = db.ExpeditionLine()
            exp_line.item_id = line.item_id
            exp_line.condition = line.condition
            exp_line.spec = line.spec
            exp_line.quantity = line.quantity
            try:
                exp_line.showing_condition = line.showing_condition
            except AttributeError:
                # Arreglar definition showing condition
                exp_line.showing_condition = ''

            if line.item_id:
                exp_line.expedition = expedition
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def stock_available(self, wh_id, lines):
        query = db.session.query(
            func.count(db.Imei.imei).label('quantity'),
            db.Imei.item_id, db.Imei.condition,
            db.Imei.spec
        ).join(db.Warehouse).where(
            db.Warehouse.id == wh_id
        ).group_by(
            db.Imei.item_id, db.Imei.spec, db.Imei.condition
        )
        return any((
            line.quantity > stock.quantity and line == stock
            for line in lines
            for stock in query
        ))

    def build_expedition_line(self, line, expedition):
        print('build expedition line call')
        print('\tline=', line)
        print('\expedition=', expedition)

        exp_line = db.ExpeditionLine()
        exp_line.condition = line.condition
        exp_line.spec = line.spec
        exp_line.item_id = line.item_id
        exp_line.quantity = line.quantity

        exp_line.expedition = expedition

    def updateWarehouse(self, proforma):
        if proforma.expedition is None:
            return

        added_lines = self.difference(proforma)
        for line in added_lines:
            self.build_expedition_line(line, proforma.expedition)

        deleted_lines = self.difference(proforma, direction='expedition_proforma')

        for line in deleted_lines:
            line.quantity = 0
            if len(line.series) == 0:
                # Corner case:
                # Solo hay 1
                # Borras la serie en el almacen
                # y se queda a 0
                # borras la linea en la factura
                # entonces queda
                try:
                    db.session.delete(line)
                except InvalidRequestError:
                    raise

        # for line in added_lines:
        #     self.build_expedition_line(line, proforma.expedition)

        # Update quantity
        # Update showing condition
        for pline in filter(item_key, proforma.lines):
            for eline in proforma.expedition.lines:
                if self.pline_eline_equal(pline, eline):
                    eline.quantity = pline.quantity
                    eline.showing_condition = pline.showing_condition
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def pline_eline_equal(self, pline, eline):
        return all((
            pline.item_id == eline.item_id,
            pline.condition == eline.condition,
            pline.spec == eline.spec
        ))

    def difference(self, proforma, direction='proforma_expedition'):

        if direction == 'proforma_expedition':
            iter_a = filter(item_key, proforma.advanced_lines or proforma.lines)
            iter_b = iter(proforma.expedition.lines)

        elif direction == 'expedition_proforma':
            iter_a = iter(proforma.expedition.lines)
            iter_b = filter(item_key, proforma.advanced_lines or proforma.lines)

        for pline in iter_a:
            for eline in iter_b:
                if self.pline_eline_equal(pline, eline):
                    break
            else:
                yield pline

from collections.abc import Iterable

class OrganizedLines:

    def __init__(self, lines):
        self.instrumented_lines = lines
        self.organized_lines = self.organize_lines(lines)

    @property
    def lines(self):
        return self.instrumented_lines

    @staticmethod
    def get_next_mix():
        import uuid
        return str(uuid.uuid4())

    def delete(self, i, j=None):
        update_stock_view = True
        if j is None:
            lines = self.organized_lines.pop(i)
            for line in lines:
                if line.item_id is None:  # exploit the run
                    update_stock_view = False
                self.instrumented_lines.remove(line)
        else:
            line = self.organized_lines[i].pop(j)
            self.instrumented_lines.remove(line)

        self.organized_lines = [e for e in self.organized_lines if e]

        db.session.flush()

        return update_stock_view

    def delete_all(self):
        for i in range(len(self.organized_lines)):
            try:
                self.delete(i)
            except IndexError:
                continue

    def append(self, price, ignore_spec, tax, showing, *stocks, row=None):
        if len(stocks) == 0:
            raise ValueError("Provide stocks")
        # Update quantity
        hit = False
        for stock in stocks:
            for line in self.lines:
                if stock == line:
                    line.quantity += stock.quantity
                    hit = True
                    break
        if hit:
            db.session.flush()
            return

        # Check if stocks are compatible for mixing between them:
        for a, b in product(stocks, stocks):
            if not utils.mixing_compatible(a, b):
                raise ValueError('Incompatible Mixing One to One.')

        # Adding
        if row is None:
            new_lines = self.build_lines_from_stocks(
                price, ignore_spec, tax,
                showing, *stocks
            )

            mix_id = self.get_next_mix()
            for line in new_lines:
                line.mix_id = mix_id

            self.organized_lines.append(new_lines)
        # Updating:
        else:
            if self.backward_compatible(stocks, row):
                new_lines = self.update_organized_lines(
                    price, ignore_spec,
                    tax, showing, *stocks,
                    row=row)
            else:
                raise ValueError(f"Incompatible mixing with line {row + 1}")

        self.instrumented_lines.extend(new_lines)

        db.session.flush()

    def build_lines_from_stocks(self, price, ignore_spec, tax, showing, *stocks, mix_id=None):
        return [
            self.build_line(price, ignore_spec, tax, showing, stock, mix_id=mix_id) for stock in stocks
        ]

    def update_organized_lines(self, price, ignore_spec, tax, showing, *stocks, row=-1):
        previous_lines = self.organized_lines[row]
        previous_mix_id = previous_lines[0].mix_id

        new_lines = self.build_lines_from_stocks(price, ignore_spec, tax, showing, *stocks, mix_id=previous_mix_id)
        previous_lines.extend(new_lines)

        return new_lines

    def backward_compatible(self, stocks, row):
        previous_lines = self.organized_lines[row]
        try:
            result = all((
                utils.mixing_compatible(stock, line)
                for stock, line in product(previous_lines, stocks)

            ))
            return result

        except TypeError:
            line = previous_lines
            result = all((
                utils.mixing_compatible(stock, line)
                for stock in stocks
            ))
            return result

    def insert_free(self, description, quantity, price, tax):

        line = db.SaleProformaLine()
        line.description = description
        line.quantity = quantity
        line.price = price
        line.tax = tax
        line.mix_id = self.get_next_mix()

        lines = [line, ]  # Homogeneo

        self.organized_lines.append(lines)

        self.instrumented_lines.extend(lines)

    @staticmethod
    def organize_lines(lines):
        mix_ids = list(dict.fromkeys([line.mix_id for line in lines]))
        matrix = []
        for mix_id in mix_ids:
            aux = []
            for line in lines:
                if line.mix_id == mix_id:
                    aux.append(line)
            matrix.append(aux)
        return matrix

    def repr(self, row, col):
        lines = self.organized_lines[row]

        diff_items = {line.item_id for line in lines}

        # For free lines, ugly, but works and uses preious code hahah
        if diff_items == {None}:
            line = lines[0]
            return self.simple_line_repr(line, col)
            return

        diff_conditions = {line.condition for line in lines}
        diff_specs = {line.spec for line in lines}

        if len(diff_items) == 1:
            description = utils.description_id_map.inverse[diff_items.pop()]
        else:
            description = utils.build_description(lines)

        if len(diff_conditions) == 1:
            condition = diff_conditions.pop()
        else:
            condition = 'Mix'
        showing_condition = lines[0].showing_condition

        if len(diff_specs) == 1:
            spec = diff_specs.pop()
        else:
            spec = 'Mix'

        ignore = 'Yes' if lines[0].ignore_spec else 'No'
        price = lines[0].price
        quantity = sum([line.quantity for line in lines])
        subtotal = price * quantity
        tax = lines[0].tax
        total = subtotal * (1 + tax / 100)
        return {
            SaleProformaLineModel.DESCRIPTION: description,
            SaleProformaLineModel.CONDITION: condition,
            SaleProformaLineModel.SHOWING_CONDITION: showing_condition,
            SaleProformaLineModel.SPEC: spec,
            SaleProformaLineModel.IGNORING_SPEC: ignore,
            SaleProformaLineModel.SUBTOTAL: str(subtotal),
            SaleProformaLineModel.PRICE: str(price),
            SaleProformaLineModel.QUANTITY: str(quantity),
            SaleProformaLineModel.TAX: str(tax),
            SaleProformaLineModel.TOTAL: str(total)
        }.get(col)

    @staticmethod
    def simple_line_repr(line, col):
        total = line.quantity * line.price * (1 + line.tax / 100)
        subtotal = line.quantity * line.price
        ignore_spec = 'Yes' if line.ignore_spec else 'No'
        showing_condition = line.showing_condition or line.condition
        return {
            SaleProformaLineModel.DESCRIPTION: line.description \
                                               or utils.description_id_map.inverse[line.item_id],
            SaleProformaLineModel.CONDITION: line.condition,
            SaleProformaLineModel.SHOWING_CONDITION: showing_condition,
            SaleProformaLineModel.SPEC: line.spec,
            SaleProformaLineModel.IGNORING_SPEC: ignore_spec,
            SaleProformaLineModel.SUBTOTAL: str(subtotal),
            SaleProformaLineModel.PRICE: str(line.price),
            SaleProformaLineModel.QUANTITY: str(line.quantity),
            SaleProformaLineModel.TAX: str(line.tax),
            SaleProformaLineModel.TOTAL: str(total)
        }.get(col)

    @staticmethod
    def build_line(price, ignore, tax, showing, stock, mix_id=None):
        line = db.SaleProformaLine()
        line.item_id = stock.item_id
        line.condition = stock.condition
        line.spec = stock.spec
        line.ignore_spec = ignore
        line.showing_condition = showing
        line.quantity = stock.request
        line.price = price
        line.tax = tax
        line.mix_id = mix_id
        return line

    def update_condition(self, row, condition):
        lines = self.organized_lines[row]
        if isinstance(lines, Iterable):
            for line in lines:
                line.showing_condition = condition
        else:
            lines.showing_condition = condition
        return True

    # Segun la nueva ultima actualizcion
    # todas son iterables, el check sobra
    # pero no vamos a testear eso ahora
    # asi que lo dejamos asi .
    def update_spec(self, row, spec):
        spec = spec.lower()
        flag = spec != 'no'
        lines = self.organized_lines[row]
        if isinstance(lines, Iterable):
            for line in lines:
                line.ignore_spec = flag
        else:
            lines.ignore_spec = flag
        return True

    def update_price(self, row, price):
        lines = self.organized_lines[row]
        if isinstance(lines, Iterable):
            for line in lines:
                line.price = price
        else:
            lines.price = price
        return True

    def update_tax(self, row, tax):
        lines = self.organized_lines[row]
        if isinstance(lines, Iterable):
            for line in lines:
                line.tax = tax
        else:
            lines.tax = tax
        return True

    def __getitem__(self, index):
        try:
            return self.organized_lines[index]
        except IndexError:
            return None

    def __len__(self):
        return len(self.organized_lines)

    def __bool__(self):
        return bool(self.instrumented_lines)


class SaleProformaLineModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SHOWING_CONDITION, SPEC, IGNORING_SPEC, \
    QUANTITY, PRICE, SUBTOTAL, TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

    def __init__(self, proforma, form):
        super().__init__()
        self.form = form
        self._headerData = ['Description', 'Condition', 'Public Condt.(Editable)', 'Spec', \
                            'Ignoring Spec?(Editable)', 'Qty.', 'Price(Editable)', 'Subtotal', 'Tax(Editable)', 'Total']
        self.organized_lines = OrganizedLines(proforma.lines)
        self.name = 'organized_lines'

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            return self.organized_lines.repr(row, column)

    def __iter__(self):
        return iter(self.organized_lines.lines)

    def delete_all(self):
        self.layoutAboutToBeChanged.emit()
        self.organized_lines.delete_all()
        self.layoutChanged.emit()

    @property
    def quantity(self):
        return sum(line.quantity for line in self.lines)

    @property
    def lines(self):
        return self.organized_lines.lines

    @property
    def tax(self):
        return sum(line.quantity * line.price * line.tax / 100 for line in self.lines)

    @property
    def subtotal(self):
        return sum(line.quantity * line.price for line in self.lines)

    @property
    def total(self):
        return self.tax + self.subtotal

    def add(self, price, ignore_spec, tax, showing, *stocks, row=None):
        self.organized_lines.append(
            price,
            ignore_spec,
            tax, showing,
            *stocks,
            row=row
        )
        self.layoutChanged.emit()

    def insert_free(self, description, quantity, price, tax):
        self.organized_lines.insert_free(
            description,
            quantity,
            price,
            tax
        )
        self.layoutChanged.emit()

    def delete(self, i, j=None):
        self.organized_lines.delete(i, j)
        self.layoutChanged.emit()

    def actual_lines_from_mixed(self, row):
        try:
            lines = self.organized_lines[row]
            if lines[0].item_id:
                return lines
        except TypeError:
            pass

        # Implicit return None,solves the free line

    def __bool__(self):
        return bool(self.organized_lines)

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self.organized_lines = OrganizedLines([])
        self.layoutChanged.emit()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        row, column = index.row(), index.column()
        if not self.editable_column(column):
            return False
        updated = False
        if role == Qt.EditRole:
            if column == self.__class__.SHOWING_CONDITION:
                return self.organized_lines.update_condition(row, value)
            elif column == self.__class__.IGNORING_SPEC:
                if value.lower() not in ('yes', 'no'):
                    return False
                else:
                    updated = self.organized_lines.update_spec(row, value)
            elif column == self.__class__.TAX:
                try:
                    tax = int(value)
                    if tax not in (0, 4, 10, 21):
                        return False
                except ValueError:
                    return False
                else:
                    updated = self.organized_lines.update_tax(row, tax)
            elif column == self.__class__.PRICE:
                try:
                    price = float(value)
                    if price < 0:
                        raise ValueError
                except ValueError:
                    return False
                else:
                    updated = self.organized_lines.update_price(row, price)

            if updated:
                self.form.update_totals()
                return True
            return False
        return False

    def editable_column(self, column):
        return column in (
            self.SHOWING_CONDITION,
            self.IGNORING_SPEC,
            self.PRICE,
            self.TAX
        )

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.editable_column(index.column()):
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)


def change_layout_and_flush(func):
    wraps(func)

    def wrapper(self, *args, **kwargs):
        self.layoutAboutToBeChanged.emit()
        r = func(self, *args, **kwargs)
        db.session.flush()
        self.layoutChanged.emit()
        return r

    return wrapper


class ActualLinesFromMixedModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SPEC, REQUEST = 0, 1, 2, 3

    def __init__(self, lines=None):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'spec', 'Requested Quantity']
        self.name = 'lines'
        self.lines = lines or []

    def sort(self, section, order):
        attr = {
            self.DESCRIPTION: 'item_id',
            self.CONDITION: 'condition',
            self.SPEC: 'spec',
        }.get(section)

        if attr:
            reverse = True if order == Qt.AscendingOrder else False
            self.layoutAboutToBeChanged.emit()
            self.lines.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        line = self.lines[row]
        if role == Qt.DisplayRole:
            if column == self.DESCRIPTION:
                return utils.description_id_map.inverse[line.item_id]
            elif column == self.CONDITION:
                return line.condition
            elif column == self.SPEC:
                return line.spec
            elif column == self.REQUEST:
                return str(line.quantity)

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self.lines = []
        self.layoutChanged.emit()


class ProductModel(BaseTable, QtCore.QAbstractTableModel):
    MPN, MANUFACTURER, CATEGORY, MODEL, CAPACITY, COLOR, HAS_SERIE = \
        0, 1, 2, 3, 4, 5, 6

    def __init__(self):

        super().__init__()
        self._headerData = ['MPN', 'Manufacturer', 'Category', 'Model',
                            'Capacity', 'Color', 'Has Serie']
        self.name = 'items'
        self.items = db.session.query(db.Item).all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        item = self.items[index.row()]
        col = index.column()
        if role != Qt.DisplayRole:
            return
        else:
            return {
                self.__class__.MPN: item.mpn,
                self.__class__.MANUFACTURER: item.manufacturer,
                self.__class__.CATEGORY: item.category,
                self.__class__.MODEL: item.model,
                self.__class__.CAPACITY: item.capacity,
                self.__class__.COLOR: item.color,
                self.__class__.HAS_SERIE: 'Yes' if item.has_serie else 'No'
            }.get(col)

    def addItem(self, mpn, manufacturer, category, model, capacity, color, has_serie):
        item = db.Item(mpn, manufacturer, category, model, capacity, color, has_serie)
        db.session.add(item)
        try:
            db.session.commit()
            self.items.append(item)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def removeItem(self, index):
        if not index.isValid():
            return
        row = index.row()
        candidate = self.items[row]
        db.session.delete(candidate)
        try:
            db.session.commit()
            del self.items[row]
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if '|' in value or '?' in value or 'Mix' in value:
            return False
        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            item = self.items[row]
            if column == self.__class__.MPN:
                item.mpn = value
            elif column == self.__class__.MANUFACTURER:
                if not value.strip():
                    return False  # These specific fields cannot be empty
                item.manufacturer = value
            elif column == self.__class__.CATEGORY:
                if not value.strip():
                    return False
                item.category = value
            elif column == self.__class__.MODEL:
                if not value.strip():
                    return False
                item.model = value
            elif column == self.__class__.CAPACITY:
                item.capacity = value
            elif column == self.__class__.COLOR:
                item.color = value
            elif column == self.__class__.HAS_SERIE:
                if value.lower() not in ('yes', 'no'):
                    return False
                item.has_serie = True if value.lower() == 'yes' else False
            try:
                db.session.commit()
            except IntegrityError:  # UNIQUE VIOLATION
                db.session.rollback()
                return False
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)

    def sort(self, section, order):
        attr = {
            self.__class__.MPN: 'mpn',
            self.__class__.MANUFACTURER: 'manufacturer',
            self.__class__.CATEGORY: 'category',
            self.__class__.MODEL: 'model',
            self.__class__.CAPACITY: 'capacity',
            self.__class__.COLOR: 'color',
            self.__class__.HAS_SERIE: 'has_serie'
        }.get(section)
        if attr:
            self.layoutAboutToBeChanged.emit()
            self.items = sorted(
                self.items,
                key=operator.attrgetter(attr),
                reverse=True if order == Qt.DescendingOrder else False
            )
            self.layoutChanged.emit()

    def __iter__(self):
        return iter(self.items)


def update_advanced_line_after_purchase_line_update(newquantity, origin_id):
    # Not yet purchase line persisted and given an id
    # remember make a flush not commit
    # if the changes will be rolled back or committed

    if not origin_id: return

    lines = db.session.query(db.AdvancedLine). \
        where(db.AdvancedLine.origin_id == origin_id). \
        order_by(db.AdvancedLine.id).all()

    total, first = 0, True
    for i, line in enumerate(lines):
        if total <= newquantity:
            total += line.quantity
            if total > newquantity:
                lines[i].quantity = line.quantity + newquantity - total
                continue
        if total > newquantity:
            lines[i].quantity = 0

    db.session.flush()


class PurchaseProformaLineModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SPEC, QUANTITY, PRICE, SUBTOTAL, \
    TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7

    def __init__(self, lines=None, form=None):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'Spec', 'Qty.(Editable)', \
                            'Price (Editable)', 'Subtotal', 'Tax (Editable)', 'Total']
        self.name = 'lines'
        self.lines = lines
        self.form = form

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row = index.row()
        try:
            self.lines[row]
        except IndexError:
            return
        line = self.lines[row]
        col = index.column()
        if role == Qt.DisplayRole:
            total = line.quantity * line.price * (1 + line.tax / 100)
            subtotal = line.quantity * line.price
            # Allowing mixed and precised lines:
            if col == 0:
                if line.description is not None:
                    return line.description
                else:
                    return utils.description_id_map.inverse[line.item_id]
            return {
                self.__class__.CONDITION: line.condition,
                self.__class__.SPEC: line.spec,
                self.__class__.QUANTITY: str(line.quantity),
                self.__class__.PRICE: str(line.price),
                self.__class__.SUBTOTAL: str(subtotal),
                self.__class__.TAX: str(line.tax),
                self.__class__.TOTAL: str(total)
            }.get(col)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        row, column = index.row(), index.column()
        if not self.editable_column(column):
            return False
        try:
            line = self.lines[row]
        except IndexError:
            return False
        if role == Qt.EditRole:
            if column == self.__class__.PRICE:
                try:
                    value = float(value)
                except:
                    return False
                else:
                    line.price = value
                    self.form._updateTotals()
                    return True
            elif column == self.__class__.QUANTITY:
                try:
                    value = int(value)
                except:
                    return False
                else:

                    if line.quantity > value:
                        update_advanced_line_after_purchase_line_update(value, line.id)

                    line.quantity = value
                    self.form._updateTotals()
                    return True
            elif column == self.__class__.TAX:
                try:
                    value = int(value)
                    if value not in (0, 4, 10, 21):
                        return False
                except:
                    return False
                else:
                    line.tax = value
                    self.form._updateTotals()
                    return True
            else:
                return False

    def editable_column(self, col):
        return col in (
            self.__class__.PRICE,
            self.__class__.QUANTITY,
            self.__class__.TAX
        )

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.editable_column(index.column()):
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def is_stock_relevant(self, line):
        return line.item_id or line.description in utils.descriptions

    @property
    def tax(self):
        return sum(line.quantity * line.price * line.tax / 100 for line in self.lines)

    @property
    def subtotal(self):
        return sum(line.quantity * line.price for line in self.lines)

    @property
    def total(self):
        return self.tax + self.subtotal

    @property
    def quantity(self):
        return sum(line.quantity for line in self.lines)

    def add(self, description, condition, spec, quantity, price, tax):
        line = db.PurchaseProformaLine()
        try:
            line.item_id = utils.description_id_map[description]
        except KeyError:
            line.description = description
        line.condition = condition or None
        line.spec = spec or None
        line.quantity = quantity
        line.tax = tax
        line.price = price

        # Dont apply mean for non stock relevant lines:
        if line.item_id is None:
            self.lines.append(line)
            self.layoutChanged.emit()
        else:
            updated = self.update_if_pre_exists(line)
            if not updated:
                self.lines.append(line)
            self.layoutChanged.emit()

    def update_if_pre_exists(self, new_line):

        # PQn = p1*q1 + p2*q2 + ··· + pn*qn Recursively
        # Qn = q1 + q2 + ··· + qn
        # pn = PQn / Qn
        # Can be determined recursively, no need to rememeber terms
        # PQn = pn-1 * qn-1 + qn*pn
        # Qn = qn-1 + qn

        for line in self.lines:
            if all((
                    new_line.condition == line.condition,
                    new_line.item_id == line.item_id,
                    new_line.description == line.description,
                    new_line.spec == line.spec
            )):
                new_quantity = line.quantity + new_line.quantity
                new_price = (line.quantity * line.price + new_line.quantity * new_line.price) \
                            / new_quantity
                line.quantity = new_quantity
                line.price = new_price
                return True

        return False

    def delete(self, indexes):
        rows = {index.row() for index in indexes}
        for row in sorted(rows, reverse=True):
            try:
                del self.lines[row]
            except:
                pass
        self.layoutChanged.emit()

    def delete_if_not_stock_relevant(self, rows):
        deleted = False
        for row in sorted(rows, reverse=True):
            line = self.lines[row]
            if self.is_stock_relevant(line):
                continue
            else:
                del self.lines[row]  # Should not rise Index Error
                deleted = True
        if deleted:
            self.layoutChanged.emit()

    def save(self, proforma):
        if not self.lines: return
        for line in self.lines:
            line.proforma = proforma
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def __bool__(self):
        return bool(len(self.lines))


class PaymentModel(BaseTable, QtCore.QAbstractTableModel):
    DATE, AMOUNT, RATE, NOTE = 0, 1, 2, 3

    def __init__(self, proforma, sale, form):
        super().__init__()
        self.proforma = proforma
        self._headerData = ['Date', 'Amount', 'Rate', 'Info']
        self.name = 'payments'
        self.form = form
        if sale:
            self.Payment = db.SalePayment
        else:
            self.Payment = db.PurchasePayment

        self.payments = db.session.query(self.Payment). \
            where(self.Payment.proforma.has(id=proforma.id)).all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        payment = self.payments[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == self.DATE:
                return payment.date.strftime('%d/%m/%Y')
            elif column == self.AMOUNT:
                return str(payment.amount)
            elif column == self.NOTE:
                return payment.note

            elif column == self.RATE:
                return payment.rate

        elif role == Qt.DecorationRole:
            if column == self.__class__.DATE:
                return QtGui.QIcon(':\calendar')

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False
        row, column = index.row(), index.column()
        payment = self.payments[row]
        if role == Qt.EditRole:
            if column == self.DATE:
                try:
                    d = utils.parse_date(value)
                    payment.date = d
                    return True
                except ValueError:
                    return False
            elif column == self.AMOUNT:
                try:
                    v = float(value.replace(',', '.'))
                    payment.amount = v
                    self.form.updateOwing()
                    return True
                except ValueError:
                    return False
            elif column == self.NOTE:
                payment.note = value[0:255]
                return True
            elif column == self.RATE:
                try:
                    v = float(value.replace(',', '.'))
                    payment.rate = v
                    self.form.updateOwing()
                    return True
                except ValueError:
                    return False
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)

    def add(self, date, amount, rate, note):
        payment = self.Payment(date, amount, rate, note, self.proforma)
        db.session.add(payment)
        try:
            db.session.commit()
            self.payments.append(payment)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def delete(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            payment = self.payments[row]
            if payment.note.startswith('CN'):
                raise ValueError("You can't delete this Payment. Remove from applied credit notes")
            db.session.delete(payment)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        else:
            for row in sorted(rows, reverse=True):
                del self.payments[row]
            self.layoutChanged.emit()

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        attr = {
            self.__class__.DATE: 'date',
            self.__class__.AMOUNT: 'amount',
            self.__class__.NOTE: 'note'
        }.get(section)
        if attr:
            self.layoutAboutToBeChanged.emit()
            self.payments.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    @property
    def paid(self):
        return sum([p.amount for p in self.payments])


class ExpenseModel(BaseTable, QtCore.QAbstractTableModel):
    DATE, AMOUNT, NOTE = 0, 1, 2

    def __init__(self, proforma, sale):
        super().__init__()
        self.proforma = proforma
        self._headerData = ['Date', 'Amount', 'Info']
        self.name = 'expenses'
        if sale:
            self.Expense = db.SaleExpense
        else:
            self.Expense = db.PurchaseExpense

        self.expenses = db.session.query(self.Expense). \
            where(self.Expense.proforma.has(id=proforma.id)).all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        expense = self.expenses[index.row()]
        colum = index.column()
        if role == Qt.DisplayRole:
            if colum == 0:
                return expense.date.strftime('%d/%m/%Y')
            elif colum == 1:
                return str(expense.amount)
            elif colum == 2:
                return expense.note
        elif role == Qt.DecorationRole:
            if colum == 0:
                return QtGui.QIcon(':\calendar')

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False
        row, column = index.row(), index.column()
        expense = self.expenses[row]
        if role == Qt.EditRole:
            if column == self.__class__.DATE:
                try:
                    d = utils.parse_date(value)
                    expense.date = d
                    return True
                except ValueError:
                    return False
            elif column == self.__class__.AMOUNT:
                try:
                    v = float(value.replace(',', '.'))
                    expense.amount = v
                    self.form.updateOwing()
                    return True
                except ValueError:
                    return False
            elif column == self.__class__.NOTE:
                expense.note = value[0:255]
                return True
        return False

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        attr = {
            self.__class__.DATE: 'date',
            self.__class__.AMOUNT: 'amount',
            self.__class__.NOTE: 'note'
        }.get(section)
        if attr:
            self.layoutAboutToBeChanged.emit()
            self.expenses.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    def add(self, date, amount, info):
        expense = self.Expense(date, amount, info, self.proforma)
        db.session.add(expense)
        try:
            db.session.commit()
            self.expenses.append(expense)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def delete(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            expense = self.expenses[row]
            db.session.delete(expense)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        else:
            for row in sorted(rows, reverse=True):
                del self.expenses[row]
            self.layoutChanged.emit()

    @property
    def spent(self):
        return sum([expense.amount for expense in self.expenses])


from functools import wraps


def change_layout_and_commit(func):
    wraps(func)

    def wrapper(self, *args, **kwargs):
        self.layoutAboutToBeChanged.emit()
        r = func(self, *args, **kwargs)
        self.commit()
        self.layoutChanged.emit()
        return r

    return wrapper


class SerieModel(QtCore.QAbstractListModel):

    def __init__(self, line, expedition):
        super().__init__()
        self.expedition = expedition
        self.line = line

        if not utils.has_serie(line):
            self.series = []
        else:
            self.series = db.session.query(db.ExpeditionSerie).join(db.ExpeditionLine). \
                where(db.ExpeditionSerie.line_id == line.id).all()

            self.series_at_expedition_level = self.get_series_at_expedition_level()

    def get_series_at_expedition_level(self):
        return {
            r[0] for r in db.session.query(db.ExpeditionSerie.serie).
                join(db.ExpeditionLine).join(db.Expedition).
                where(db.Expedition.id == self.expedition.id)
        }

    def add(self, line, _serie):
        if _serie in self:
            raise SeriePresentError

        serie = db.ExpeditionSerie()
        serie.serie = _serie
        serie.line = line
        db.session.add(serie)
        try:
            db.session.commit()
            self.series.append(serie)
            self.series_at_expedition_level = self.get_series_at_expedition_level()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def delete_all(self):
        for expedition_serie in self.series:
            db.session.delete(expedition_serie)
        try:
            db.session.commit()
            self.series = []
            self.series_at_expedition_level = self.get_series_at_expedition_level()
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def select_invented_from_imeis(self, limit=0):

        query = db.session.query(db.Imei.imei).where(
            db.Imei.warehouse_id == self.expedition.proforma.warehouse_id,
            db.Imei.spec == self.line.spec,
            db.Imei.condition == self.line.condition,
            db.Imei.item_id == self.line.item_id
        ).limit(limit)

        return [r.imei for r in query]

    def select_from_expedition_series(self, *, limit=0):
        query = db.session.query(db.ExpeditionSerie).where(
            db.ExpeditionSerie.line_id == self.line.id
        ).limit(limit)

        return [e for e in query]

    def handle_invented(self, difference):
        if difference == 0:
            return

        elif difference < 0:  # user wants to correct, invent new series
            difference = abs(difference)
            for expedition_serie in self.select_from_expedition_series(limit=difference):
                db.session.delete(expedition_serie)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        elif difference > 0:  # User wants to process, select and

            ficticious_series = []
            for invented in self.select_invented_from_imeis(limit=difference):
                serie = db.ExpeditionSerie()
                serie.serie = invented
                serie.line = self.line
                ficticious_series.append(serie)

            db.session.add_all(ficticious_series)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

    def delete(self, series):
        for serie in series:
            db.session.delete(serie)
        try:
            db.session.commit()
            for serie in series:
                self.series.remove(serie)
            self.layoutChanged.emit()
            self.series_at_expedition_level = self.get_series_at_expedition_level()
        except:
            db.session.rollback()
            raise

    def rowCount(self, index):
        return len(self.series)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self.series[index.row()].serie

    def __contains__(self, serie):
        return serie in self.series_at_expedition_level

    def index_of(self, key):
        for index, serie in enumerate(self.series):
            if key == serie.serie:
                return index


class ExpeditionModel(BaseTable, QtCore.QAbstractTableModel):
    ID, WAREHOUSE, DATE, TOTAL, PROCESSED, LOGISTIC, CANCELLED, PARTNER, \
    AGENT, WARNING, FROM_PROFORMA, READY, EXTERNAL, PRESALE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13

    def __init__(self, search_key=None, filters=None, last=10):
        super().__init__()
        self._headerData = ['Expedition ID', 'Warehouse', 'Date', 'Total', 'Processed',
                            'Logistic', 'Cancelled', 'Partner', 'Agent', 'Warning', 'From Proforma', 'Ready To Go',
                            'External Doc.', 'Presale']
        self.name = 'expeditions'


        query = db.session.query(db.Expedition). \
            select_from(
            db.SaleProforma,
            db.Partner, db.Agent,
            db.Warehouse). \
            where(
            db.Agent.id == db.SaleProforma.agent_id,
            db.Partner.id == db.SaleProforma.partner_id,
            db.Expedition.proforma_id == db.SaleProforma.id,
            db.Warehouse.id == db.SaleProforma.warehouse_id
        )


        query = query.where(db.SaleProforma.date > utils.get_last_date(last))

        if search_key:
            clause = or_(
                db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
                db.Warehouse.description.contains(search_key))
            query = query.where(clause)

        if filters:
            self.expeditions = query.all()

            if filters['logistic']:
                if 'empty' in filters['logistic']:
                    self.expeditions = filter(lambda e: sale_empty(e), self.expeditions)
                if 'overflowed' in filters['logistic']:
                    self.expeditions = filter(lambda e: sale_overflowed(e), self.expeditions)
                if 'partially_processed' in filters['logistic']:
                    self.expeditions = filter(lambda e: sale_partially_processed(e), self.expeditions)
                if 'completed' in filters['logistic']:
                    self.expeditions = filter(lambda e: sale_completed(e), self.expeditions)
            if filters['cancelled']:
                if 'cancelled' in filters['cancelled']:
                    self.expeditions = filter(lambda e: e.proforma.cancelled, self.expeditions)
                if 'notcancelled' in filters['cancelled']:
                    self.expeditions = filter(lambda e: not e.proforma.cancelled, self.expeditions)

            if isinstance(self.expeditions, filter):
                self.expeditions = list(self.expeditions)
        else:
            self.expeditions = query.all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        expedition = self.expeditions[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == self.ID:
                return str(expedition.id).zfill(6)
            elif column == self.WAREHOUSE:
                return expedition.proforma.warehouse.description
            elif column == self.TOTAL:
                return str(expedition_total_quantity(expedition))
            elif column == self.PARTNER:
                return expedition.proforma.partner.fiscal_name
            elif column == self.PROCESSED:
                return str(sale_total_processed(expedition))
            elif column == self.LOGISTIC:
                if sale_empty(expedition):
                    return 'Empty'
                elif sale_overflowed(expedition):
                    return 'Overflowed'
                elif sale_partially_processed(expedition):
                    return 'Partially Prepared'
                elif sale_completed(expedition):
                    return 'Completed'

            elif column == self.PRESALE:
                return 'Yes' if expedition.proforma.advanced_lines else 'No'

            elif column == self.DATE:
                return expedition.proforma.date.strftime('%d/%m/%Y')

            elif column == self.CANCELLED:
                return 'Yes' if expedition.proforma.cancelled else 'No'
            elif column == self.AGENT:
                return expedition.proforma.agent.fiscal_name
            elif column == self.WARNING:
                return expedition.proforma.warning
            elif column == self.FROM_PROFORMA:
                return str(expedition.proforma.type) + '-' + str(expedition.proforma.number).zfill(6)
            elif column == self.READY:
                return 'Yes' if expedition.proforma.ready else 'No'
            elif column == self.EXTERNAL:
                return expedition.proforma.external or 'Unknown'

        elif role == Qt.DecorationRole:

            if column == self.AGENT:
                return QtGui.QIcon(':\\agents')

            elif column == self.DATE:
                return QtGui.QIcon(':\calendar')

            elif column == self.PARTNER:
                return QtGui.QIcon(':\partners')
            elif column == self.LOGISTIC:
                if sale_empty(expedition):
                    return QtGui.QColor(YELLOW)
                elif sale_overflowed(expedition):
                    return QtGui.QColor(RED)
                elif sale_partially_processed(expedition):
                    return QtGui.QColor(ORANGE)
                elif sale_completed(expedition):
                    return QtGui.QColor(GREEN)
            elif column == self.CANCELLED:
                return QtGui.QColor(RED if expedition.proforma.cancelled else GREEN)

            elif column == self.READY:
                return QtGui.QColor(GREEN if expedition.proforma.ready else RED)

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == self.FROM_PROFORMA:
            self.layoutAboutToBeChanged.emit()
            self.expeditions = sorted(
                self.expeditions, key=lambda r: (r.proforma.type, r.proforma.number),
                reverse=reverse
            )
            self.layoutChanged.emit()
        else:
            attr = {
                self.ID: 'id',
                self.WAREHOUSE: 'proforma.warehouse_id',
                self.CANCELLED: 'proforma.cancelled',
                self.PARTNER: 'proforma.partner.fiscal_name',
                self.AGENT: 'proforma.agent.fiscal_name',
                self.READY: 'proforma.ready',
                self.DATE: 'proforma.date'
            }.get(section)

            if attr:
                self.layoutAboutToBeChanged.emit()
                self.expeditions = sorted(self.expeditions, key=operator.attrgetter(attr), \
                                          reverse=True if order == Qt.DescendingOrder else False)
                self.layoutChanged.emit()


class ReceptionModel(BaseTable, QtCore.QAbstractTableModel):
    ID, WAREHOUSE, TOTAL, PROCESSED, LOGISTIC, CANCELLED, PARTNER, \
    AGENT, WARNING, FROM_PROFORMA, EXTERNAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

    def __init__(self, search_key=None, filters=None, last=10):
        super().__init__()
        self._headerData = ['Reception ID', 'Warehouse', 'Total', 'Processed', 'Logistic', 'Cancelled',
                            'Partner', 'Agent', 'Warning', 'From Proforma', 'External Doc.']
        self.name = 'receptions'

        query = db.session.query(db.Reception). \
            select_from(
            db.PurchaseProforma,
            db.Partner, db.Agent,
            db.Warehouse). \
            where(
                db.Agent.id == db.PurchaseProforma.agent_id,
                db.Partner.id == db.PurchaseProforma.partner_id,
                db.Reception.proforma_id == db.PurchaseProforma.id,
                db.Warehouse.id == db.PurchaseProforma.warehouse_id
            )

        query = query.where(db.PurchaseProforma.date > utils.get_last_date(last))


        if search_key:
            clause = or_(
                db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
                db.Warehouse.description.contains(search_key))
            query = query.where(clause)

        if filters:
            self.receptions = query.all()
            if filters['logistic']:
                if 'empty' in filters['logistic']:
                    self.receptions = filter(lambda r: purchase_empty(r), self.receptions)
                if 'overflowed' in filters['logistic']:
                    self.receptions = filter(lambda r: reception_overflowed(r), self.receptions)
                if 'partially_processed' in filters['logistic']:
                    self.receptions = filter(lambda r: purchase_partially_processed(r), self.receptions)
                if "completed" in filters['logistic']:
                    self.receptions = filter(lambda r: purchase_completed(r), self.receptions)

            if filters['cancelled']:
                if 'cancelled' in filters['cancelled']:
                    self.receptions = filter(lambda r: r.proforma.cancelled, self.receptions)
                if 'notcancelled' in filters['cancelled']:
                    self.receptions = filter(lambda r: not r.proforma.cancelled, self.receptions)

            if isinstance(self.receptions, filter):
                self.receptions = list(self.receptions)
        else:
            self.receptions = query.all()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        reception = self.receptions[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == ReceptionModel.ID:
                return str(reception.id).zfill(6)
            elif column == ReceptionModel.WAREHOUSE:
                return reception.proforma.warehouse.description
            elif column == ReceptionModel.TOTAL:
                return str(purchase_total_quantity(reception))
            elif column == ReceptionModel.PARTNER:
                return reception.proforma.partner.fiscal_name
            elif column == ReceptionModel.PROCESSED:
                return str(purchase_total_processed(reception))
            elif column == ReceptionModel.LOGISTIC:
                if purchase_empty(reception):
                    return "Empty"
                elif reception_overflowed(reception):
                    return 'Overflowed'
                elif purchase_partially_processed(reception):
                    return 'Partially Received'
                elif purchase_completed(reception):
                    return "Completed"
            elif column == ReceptionModel.CANCELLED:
                return "Yes" if reception.proforma.cancelled else "No"
            elif column == ReceptionModel.AGENT:
                return reception.proforma.agent.fiscal_name
            elif column == ReceptionModel.WARNING:
                return reception.note
            elif column == ReceptionModel.FROM_PROFORMA:
                return str(reception.proforma.type) + '-' + str(reception.proforma.number).zfill(6)
            elif column == self.EXTERNAL:
                return reception.proforma.external or 'Unknown'

        elif role == Qt.DecorationRole:
            if column == ReceptionModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif column == ReceptionModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif column == ReceptionModel.LOGISTIC:
                if purchase_empty(reception):
                    return QtGui.QColor(YELLOW)
                elif reception_overflowed(reception):
                    return QtGui.QColor(RED)
                elif purchase_partially_processed(reception):
                    return QtGui.QColor(ORANGE)
                elif purchase_completed(reception):
                    return QtGui.QColor(GREEN)
            elif column == ReceptionModel.CANCELLED:
                return QtGui.QColor(RED) if reception.proforma.cancelled \
                    else QtGui.QColor(GREEN)

    def sort(self, section, order):
        reverse = True if order == Qt.AscendingOrder else False
        if section == ReceptionModel.FROM_PROFORMA:
            self.layoutAboutToBeChanged.emit()
            self.receptions = sorted(
                self.receptions, key=lambda r: (r.proforma.type, r.proforma.number),
                reverse=reverse
            )
            self.layoutChanged.emit()
        else:
            attr = {
                ReceptionModel.ID: 'id',
                ReceptionModel.WAREHOUSE: 'proforma.warehouse_id',
                ReceptionModel.CANCELLED: 'proforma.cancelled',
                ReceptionModel.PARTNER: 'proforma.partner.fiscal_name',
                ReceptionModel.AGENT: 'proforma.agent.fiscal_name',
            }.get(section)

            if attr:
                self.layoutAboutToBeChanged.emit()
                self.receptions = sorted(self.receptions, key=operator.attrgetter(attr), \
                                         reverse=True if order == Qt.DescendingOrder else False)
                self.layoutChanged.emit()

    def generate_template(self, file_path, row):
        reception = self.receptions[row]
        try:
            from openpyxl import Workbook
            book = Workbook()
            sheet = book.active

            header = ['Imei/SN', 'Line Nº', 'Description', 'Condition', 'Spec']

            sheet.append([
                'Reception Id = ' + str(reception.id),
                'Partner = ' + reception.proforma.partner.fiscal_name,
                'Agent = ' + reception.proforma.agent.fiscal_name,
                'Date = ' + str(reception.proforma.date)
            ])

            sheet.append(header)

            sheet.append([])

            for row in self.generate_excel_rows(reception):
                sheet.append(row)

            book.save(file_path)

        except Exception as ex:
            raise ValueError(str(ex))

    def import_excel(self, file_path, row):
        reception = self.receptions[row]

        # First check that template was not altered
        from openpyxl import load_workbook
        book = load_workbook(file_path)
        sheet = book.active

        if sheet['A1'].value != 'Reception Id = ' + str(reception.id):
            raise ValueError("Reception doesn't match with Template")

        excel_rows = list(sheet.iter_rows(min_row=4, min_col=0, max_col=6, values_only=True))

        for excel_row, rec_row in zip(
                excel_rows,
                list(self.generate_excel_rows(reception))
        ):
            if excel_row[1:] != rec_row[1:]:
                raise ValueError("Reception doesn't match with Template")

        from db import ReceptionSerie
        for row in excel_rows:
            # No me queda otra, pa no tocar todas las ocurrencias
            # de Reception serie. Debi haber dado flexibilidad a ese
            # Constructor antes. Ahora tenemos prisa jajaja
            line = self.get_line_from_line_id(reception, row[-1])
            rs = ReceptionSerie.from_excel(*row, line)
            db.session.add(rs)

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            # raise ValueError(str(ex))
            raise

    def export(self, file_path, row):
        reception = self.receptions[row]

        try:
            from openpyxl import Workbook
            book = Workbook()
            sheet = book.active

            for row in self.generate_export_rows(reception):
                sheet.append(row)

            book.save(file_path)
        except Exception as ex:
            raise ValueError(str(ex))

    def get_line_from_line_id(self, reception, line_id):
        for line in reception.lines:
            if line.id == line_id:
                return line

    def generate_export_rows(self, reception):
        for line in reception.lines:
            for serie in line.series:
                yield (serie.serie, serie.item.clean_repr)

    def generate_excel_rows(self, reception):
        for line_no, line in enumerate(reception.lines, start=1):
            if all((
                    line.item_id,
                    line.condition != 'Mix',
                    line.spec != 'Mix',
                    utils.has_serie(line)
            )):
                for i in range(line.quantity):
                    yield (None, line_no, line.item.clean_repr, \
                           line.condition, line.spec, line.id)


import operator, functools


class StockEntry:

    def __init__(self, item_id, condition, spec, quantity):
        self._item_id = item_id
        self._spec = spec
        self._condition = condition
        self._quantity = int(quantity)
        self._request = 0
        # Make self.__eq__ with saleproformaline.__eq__ compatible
        self.description = None

    @property
    def excel_row(self):
        from utils import description_id_map
        return description_id_map.inverse.get(self.item_id), self.condition, self.spec, self.quantity

    @classmethod
    def fake(cls, item_id):
        return cls(item_id, '', '', 10)

    @property
    def item_id(self):
        return self._item_id

    @property
    def spec(self):
        return self._spec

    @property
    def condition(self):
        return self._condition

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, request):
        try:
            request = int(request)
        except ValueError:
            raise
        if self.quantity < request:
            raise ValueError('self.quantity < request')
        self._request = request

    def __iter__(self):
        return (i for i in (self.item_id, self.condition, \
                            self.spec, self.quantity, self.request))

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}({!r}, {!r}, {!r}, {!r}, {!r})'.format(class_name, *self)

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        return all((
            self.item_id == other.item_id,
            self.spec == other.spec,
            self.condition == other.condition
        ))

    def __iadd__(self, other):
        # if self != other:
        # 	raise ValueError('Unsuported add for non-eqivalent vectors')
        self.quantity += other.quantity
        return self

    def __isub__(self, other):
        self.quantity -= other.quantity

    def __hash__(self):
        # None at the end of the list in able to make this hash
        # compatible with that of SaleProformaLine and enable
        # set operations. This is shit. But it works.
        hashes = (hash(x) for x in (self._item_id, self._spec, self._condition, self.description))
        return functools.reduce(operator.xor, hashes, 0)


class StockModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SPEC, QUANTITY, REQUEST = \
        0, 1, 2, 3, 4

    def __init__(self, warehouse_id, description, condition, spec, check=False):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'Spec', 'Quantity avail. ', 'Requested quant.']

        if check:  # For checking only
            self._headerData.remove('Requested quant.')

        self.name = 'stocks'

        self.warehouse_id = warehouse_id

        self.stocks = self.computeStock(
            warehouse_id,
            description,
            condition,
            spec
        )

    @classmethod
    def stocks(cls, warehouse_id, description=None, condition=None, spec=None):

        return cls(warehouse_id, description=description, condition=condition, \
                   spec=spec).stocks

    def computeStock(self, warehouse_id, description, condition, spec, session=db.session):

        # session = session
        item_id = utils.description_id_map.get(description)

        query = session.query(
            db.Imei.item_id, db.Imei.condition,
            db.Imei.spec, func.count(db.Imei.imei).label('quantity')
        ).where(
            db.Imei.warehouse_id == warehouse_id
        ).group_by(
            db.Imei.item_id, db.Imei.condition, db.Imei.spec
        )

        if item_id:
            query = query.where(db.Imei.item_id == item_id)
        else:
            item_ids = utils.get_itemids_from_mixed_description(description)
            if item_ids:
                query = query.where(db.Imei.item_id.in_(item_ids))

        if condition:
            query = query.where(
                db.Imei.condition == condition
            )

        if spec:
            query = query.where(
                db.Imei.spec == spec
            )

        imeis = {
            StockEntry(r.item_id, r.condition, r.spec, r.quantity)
            for r in query
        }

        query = session.query(
            db.ImeiMask.item_id, db.ImeiMask.condition,
            db.ImeiMask.spec, func.count(db.ImeiMask.imei).label('quantity')
        ).where(
            db.Warehouse.id == warehouse_id,
            db.Warehouse.id == db.ImeiMask.warehouse_id,
        ).group_by(
            db.ImeiMask.item_id, db.ImeiMask.condition, db.ImeiMask.spec
        )

        if condition:
            query = query.where(
                db.ImeiMask.condition == condition
            )

        if spec:
            query = query.where(
                db.ImeiMask.spec == spec
            )

        imeis_mask = {
            StockEntry(r.item_id, r.condition, r.spec, r.quantity)
            for r in query
        }

        query = session.query(
            db.SaleProformaLine.item_id,
            db.SaleProformaLine.condition,
            db.SaleProformaLine.spec,
            func.sum(db.SaleProformaLine.quantity).label('quantity')
        ).join(
            db.SaleProforma
        ).group_by(
            db.SaleProformaLine.item_id,
            db.SaleProformaLine.condition,
            db.SaleProformaLine.spec
        ).where(
            db.SaleProforma.warehouse_id == warehouse_id,
            db.SaleProforma.cancelled == False
        )

        sales = {StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query}

        query = session.query(
            db.AdvancedLine.item_id,
            db.AdvancedLine.condition,
            db.AdvancedLine.spec,
            func.sum(db.AdvancedLine.quantity).label('quantity')
        ).join(
            db.SaleProforma
        ).group_by(
            db.AdvancedLine.item_id,
            db.AdvancedLine.condition,
            db.AdvancedLine.spec
        ).where(
            db.SaleProforma.warehouse_id == warehouse_id,
            db.SaleProforma.cancelled == False,
            db.AdvancedLine.item_id != None
        )

        advanced_sales = {StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query}

        query = session.query(
            db.ExpeditionLine.item_id,
            db.ExpeditionLine.condition,
            db.ExpeditionLine.spec,
            func.count(db.ExpeditionSerie.serie).label('quantity')
        ).select_from(
            db.ExpeditionLine, db.ExpeditionSerie,
            db.SaleProforma, db.Warehouse, db.Expedition,
        ).where(
            db.ExpeditionLine.id == db.ExpeditionSerie.line_id,
            db.ExpeditionLine.expedition_id == db.Expedition.id,
            db.SaleProforma.warehouse_id == db.Warehouse.id,
            db.Expedition.proforma_id == db.SaleProforma.id,
            db.Warehouse.id == warehouse_id,
        ).group_by(
            db.ExpeditionLine.item_id,
            db.ExpeditionLine.condition,
            db.ExpeditionLine.spec
        )

        if item_id:
            query = query.where(db.ExpeditionLine.item_id == item_id)

        if condition:
            query = query.where(
                db.ExpeditionLine.condition == condition
            )
        if spec:
            query = query.where(
                db.ExpeditionLine.spec == spec
            )

        outputs = {StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query}

        query = session.query(
            db.AdvancedLineDefinition.item_id,
            db.AdvancedLineDefinition.condition,
            db.AdvancedLineDefinition.spec,
            func.sum(db.AdvancedLineDefinition.quantity).label('quantity')
        ).join(
            db.AdvancedLine
        ).join(
            db.SaleProforma
        ).where(
            db.SaleProforma.warehouse_id == warehouse_id,
            db.SaleProforma.cancelled == False
        ).group_by(
            db.AdvancedLineDefinition.item_id,
            db.AdvancedLineDefinition.condition,
            db.AdvancedLineDefinition.spec,
        )

        defined_sales = {
            StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query
        }

        # combine sales and definitions:
        r = sales.symmetric_difference(defined_sales)
        for sale in sales:
            for defined_sale in defined_sales:
                if sale == defined_sale:
                    sale += defined_sale
                    r.add(sale)
        sales = r

        # Combine sales and advanced sales:
        r = sales.symmetric_difference(advanced_sales)
        for sale in sales:
            for advanced_sale in advanced_sales:
                if sale == advanced_sale:
                    sale += advanced_sale
                    r.add(sale)
        sales = r

        stocks = self.resolve(imeis, imeis_mask, sales, outputs)

        return list(filter(lambda stock: stock.quantity != 0, stocks))

    def lines_against_stock(self, warehouse_id, lines):
        # Session = db.sessionmaker(bind=db.dev_engine)
        # session = db.Session()

        Session = db.sessionmaker(bind=db.get_engine())
        with Session.begin() as session:

            lines = set([line for line in lines if line.item_id is not None])
            stocks = set(self.computeStock(warehouse_id, None, None, None, session=session))

            if lines.difference(stocks):
                return True

            if any((
                    line == stock and line.quantity > stock.quantity
                    for line in lines
                    for stock in stocks
            )):
                return True
            return False

    def resolve(self, imeis, imeis_mask, sales, outputs):

        for imei_mask in imeis_mask:
            for imei in imeis:
                if imei == imei_mask:
                    imei -= imei_mask

        for output in outputs:
            for sale in sales:
                if sale == output:
                    sale -= output

        for sale in sales:
            for imei in imeis:
                if sale == imei:
                    imei -= sale

        return imeis

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        stock = self.stocks[row]

        if role == Qt.DisplayRole:
            if column == self.__class__.DESCRIPTION:
                return utils.description_id_map.inverse[stock.item_id]
            elif column == self.__class__.CONDITION:
                return stock.condition
            elif column == self.__class__.SPEC:
                return stock.spec
            elif column == self.__class__.QUANTITY:
                return str(stock.quantity) + ' pcs'
            elif column == self.__class__.REQUEST:
                return str(stock.request)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return
        stock = self.stocks[index.row()]
        try:
            stock.request = value
        except ValueError as ex:
            return False

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 4:
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self.stocks = []
        self.layoutChanged.emit()

    def sort(self, section, order):
        attr = {
            self.DESCRIPTION: 'item_id',
            self.CONDITION: 'condition',
            self.SPEC: 'spec',
            self.QUANTITY: 'quantity'
        }.get(section)

        if attr:
            reverse = True if order == Qt.AscendingOrder else False
            self.layoutAboutToBeChanged.emit()
            self.stocks.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    @property
    def requested_stocks(self):
        return list(filter(lambda s: s.request > 0, self.stocks))

    def excel_export(self, file_path):

        if not file_path:
            return
        from utils import warehouse_id_map
        from utils import description_id_map
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        header = ['WH', 'Description', 'Condition', 'Spec', 'Quantity']
        ws.append(header)
        warehouse = warehouse_id_map.inverse.get(self.warehouse_id)
        for stock in self.stocks:
            ws.append((warehouse,) + stock.excel_row)

        wb.save(file_path)

    def whatsapp_export(self, file_path):
        print('whatsapp_export')


class IncomingVector:

    def __init__(self, line, session=db.session):

        self.origin_id = line.id
        self.origin = line
        self.type = line.proforma.type
        self.number = line.proforma.number
        self.eta = line.proforma.eta.strftime('%d/%m/%Y')
        self.item_id = line.item_id
        self.spec = line.spec
        self.condition = line.condition
        self.description = line.description

        quantity = line.quantity

        asked = sum(
            line.quantity for line in session.query(db.AdvancedLine.quantity).
                join(db.SaleProforma).where(db.SaleProforma.cancelled == False).
                where(db.AdvancedLine.origin_id == line.id)
        )

        processed = self.compute_processed(line)

        if quantity == processed:
            self.available = 0
        else:
            self.available = quantity - asked

    @property
    def excel_row(self):
        description = self.description or utils.description_id_map.inverse.get(self.item_id)
        return self.document, self.eta, description, self.condition, self.spec, self.available

    @property
    def document(self):
        return str(self.type) + '-' + str(self.number).zfill(6)

    @staticmethod
    def compute_processed(line):
        line_alias = line
        try:
            for line in line.proforma.reception.lines:
                if line_alias == line:
                    return len(line.series)
            else:  # Reaches end, does not find it's brother in warehouse
                return 0

        except AttributeError as ex:
            return 0

    def __iter__(self):
        return iter(self.__dict__.values())

    def __repr__(self):
        clsname = self.__class__.__name__
        s = f"{clsname}(origin_id={self.origin_id}, description={self.description}, "
        s += f"item_id={self.item_id}, condition={self.condition}, spec={self.spec}, "
        s += f"available={self.available})"
        return s


class IncomingStockModel(BaseTable, QtCore.QAbstractTableModel):
    DOCUMENT, ETA, DESC, CONDITION, SPEC, AVAILABLE = 0, 1, 2, 3, 4, 5

    # check arg , make compatible with stock model init call
    def __init__(self, warehouse_id, *, description, condition, spec, type=None, number=None, check=False):
        super().__init__()
        self._headerData = ['Document', 'ETA', 'Description', 'Condition', 'Spec', 'Available']
        self.name = 'stocks'
        self.warehouse_id = warehouse_id
        self.stocks = self.computeIncomingStock(
            warehouse_id,
            description=description,
            condition=condition,
            spec=spec,
            type=type,
            number=number
        )

    def computeIncomingStock(self, warehouse_id, *, description, condition, spec,
                             type=None, number=None, session=db.session):

        query = session.query(db.PurchaseProformaLine). \
            join(db.PurchaseProforma).join(db.Partner).outerjoin(db.Reception). \
            join(db.Warehouse).where(db.Warehouse.id == warehouse_id). \
            where(db.PurchaseProforma.cancelled == False)

        item_id = utils.description_id_map.get(description)

        if type:
            query = query.where(db.PurchaseProforma.type == type)

        if number:
            query = query.where(db.PurchaseProforma.number == number)

        if item_id:
            query = query.where(db.PurchaseProformaLine.item_id == item_id)
        else:
            item_ids = utils.get_itemids_from_mixed_description(description)
            if item_ids:
                predicates = (
                    db.PurchaseProformaLine.item_id.in_(item_ids),
                    db.PurchaseProformaLine.description == description  # ??
                )
                query = query.where(or_(*predicates))

        if condition:
            query = query.where(db.PurchaseProformaLine.condition == condition)

        if spec:
            query = query.where(db.PurchaseProformaLine.spec == spec)

        stocks = [
            IncomingVector(line, session=session) for line in query
            if self.line_contains_stock(line)
        ]

        r = list(filter(lambda s: s.available != 0, stocks))

        return r

    @staticmethod
    def line_contains_stock(line):
        return line.description in utils.descriptions or line.item_id in utils.description_id_map.inverse

    def lines_against_stock(self, warehouse_id, lines):

        Session = db.sessionmaker(bind=db.get_engine())
        session = Session()

        print('Lines:')
        for line in lines:
            print('\t', line)

        print('Stocks:')

        for stock in self.computeIncomingStock(
                warehouse_id, description=None,
                condition=None, spec=None, session=session
        ):
            for line in lines:
                if line == stock and line.quantity > stock.available:
                    return True
        return False

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            vector = self.stocks[row]
            if col == self.__class__.DOCUMENT:
                return vector.document
            elif col == self.__class__.ETA:
                return vector.eta
            elif col == self.__class__.DESC:
                return vector.description or \
                       utils.description_id_map.inverse.get(vector.item_id)
                return vector.description
            elif col == self.__class__.CONDITION:
                return vector.condition
            elif col == self.__class__.SPEC:
                return vector.spec
            elif col == self.__class__.AVAILABLE:
                return str(vector.available)

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self.stocks = []
        self.layoutChanged.emit()

    def __getitem__(self, index):
        return self.stocks[index]

    def whatsapp_export(self):
        print('whatsapp export')

    def excel_export(self, file_path):

        header = ['WH', 'Document', 'ETA', 'Description', 'Condition', 'Spec', 'Available']
        from openpyxl import Workbook
        from utils import warehouse_id_map

        warehouse = warehouse_id_map.inverse.get(self.warehouse_id)

        wb = Workbook()
        ws = wb.active

        ws.append(header)

        for vector in self.stocks:
            ws.append((warehouse,) + vector.excel_row)

        wb.save(file_path)


class AdvancedLinesModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SHOWING_CONDITION, SPEC, IGNORING_SPEC, \
    QUANTITY, PRICE, SUBTOTAL, TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

    def __init__(self, proforma, form=None, show_free=True):
        super().__init__()
        self.form = form
        self._headerData = ['Description', 'Condition', 'Public Condt.(Editable)', 'Spec',
                            'Ignoring Spec?(Editable)', 'Qty.', 'Price(Editable)', 'Subtotal',
                            'Tax (Editable)', 'Total']
        self.name = 'lines'
        self._lines = proforma.advanced_lines
        if not show_free:
            self._lines = [line for line in self._lines if not line.free_description]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            line = self._lines[row]
            if col == self.DESCRIPTION:
                return line.free_description or line.mixed_description \
                       or utils.description_id_map.inverse.get(line.item_id)

            elif col == self.CONDITION:
                try:
                    return line.condition
                except AttributeError:
                    return ''
            elif col == self.SHOWING_CONDITION:
                return line.showing_condition or ''
            elif col == self.SPEC:
                try:
                    return line.spec
                except AttributeError:
                    return ''
            elif col == self.IGNORING_SPEC:
                return 'Yes' if line.ignore_spec else 'No'
            elif col == self.QUANTITY:
                return str(line.quantity)
            elif col == self.PRICE:
                return str(line.price)
            elif col == self.TAX:
                return str(line.tax)
            elif col == self.SUBTOTAL:
                return str(line.price * line.quantity)
            elif col == self.TOTAL:
                total = line.quantity * line.price * (1 + line.tax / 100)
                return str(total)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return False
        row, column = index.row(), index.column()
        if not self.editable_column(column):
            return False
        updated = False
        line = self.lines[row]
        if column == self.SHOWING_CONDITION:
            line.showing_condition = value
            updated = True
        elif column == self.PRICE:
            try:
                v = float(value)
            except ValueError:
                pass
            else:
                line.price = v
                updated = True
        elif column == self.IGNORING_SPEC:
            value_lower = value.lower()
            if value_lower in ('yes', 'no'):
                line.ignore_spec = True if value_lower == 'yes' else False
                updated = True
        elif column == self.TAX:
            try:
                tax = int(value)
                if tax not in (0, 4, 10, 21):
                    raise ValueError
            except ValueError:
                pass
            else:
                line.tax = tax
                updated = True

        if updated:
            if self.form is not None:  # In definition form is not necessary

                self.form.update_totals()

        return updated

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.editable_column(index.column()):
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def editable_column(self, column):
        return column in (
            self.PRICE, self.IGNORING_SPEC, self.SHOWING_CONDITION, self.PRICE,
            self.TAX
        )

    def add(self, quantity, price, ignore, tax, showing, vector):

        line = db.AdvancedLine()
        line.origin_id = vector.origin_id
        line.quantity = quantity
        line.price = price
        line.ignore = ignore
        line.tax = tax
        line.showing_condition = showing
        line.condition = vector.condition
        line.spec = vector.spec
        line.item_id = vector.item_id
        line.mixed_description = vector.description

        if not self.update_if_preexists(vector, quantity):
            self._lines.append(line)

        db.session.flush()
        self.layoutChanged.emit()

    def delete(self, row):
        del self._lines[row]
        db.session.flush()
        self.layoutChanged.emit()

    def update_if_preexists(self, vector: IncomingVector, quantity):
        for line in self.lines:
            if all((
                    vector.item_id == line.item_id,
                    vector.description == line.mixed_description,
                    vector.condition == line.condition,
                    vector.spec == line.spec
            )):
                line.quantity += quantity
                return True
        return False

    def insert_free(self, description, quantity, price, tax):

        line = db.AdvancedLine()
        line.free_description = description
        line.quantity = quantity
        line.price = price
        line.tax = tax

        self._lines.append(line)
        self.layoutChanged.emit()

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self._lines = []
        self.layoutChanged.emit()

    @property
    def quantity(self):
        return sum(line.quantity for line in self._lines)

    @property
    def lines(self):
        return self._lines

    @property
    def tax(self):
        return sum(
            line.quantity * line.price * line.tax / 100
            for line in self._lines
        )

    @property
    def total(self):
        return self.subtotal + self.tax

    @property
    def subtotal(self):
        return sum(
            line.quantity * line.price for line in self._lines
        )

    def update_count_relevant(self):
        for line in self._lines:
            for line_def in line.definitions:
                line_def.local_count_relevant = False
                line_def.global_count_relevant = True

    def __getitem__(self, index):
        return self._lines[index]

    def __bool__(self):
        return bool(self._lines)


InventoryEntry = namedtuple('InventoryEntry', 'serie description condition spec warehouse quantity')


class InventoryModel(BaseTable, QtCore.QAbstractTableModel):
    SERIE, DESCRIPTION, CONDITION, SPEC, WAREHOUSE, QUANTITY = 0, 1, 2, 3, 4, 5,

    def __init__(self, description=None, condition=None, spec=None, warehouse=None):
        super().__init__()
        self._headerData = ['Serie', 'Description', 'Condition', 'Spec', 'Warehouse', 'Quantity']
        self.name = 'series'
        query = db.session.query(db.Imei).join(db.Item).join(db.Warehouse)

        if description:
            ids = utils.get_items_ids_by_keyword(description.lower())
            if ids:
                query = query.where(db.Imei.item_id.in_(ids))
            else:
                query = query.where(db.Imei.imei.contains(description))

        if condition:
            query = query.where(db.Imei.condition.contains(condition))

        if spec:
            query = query.where(db.Imei.spec.contains(spec))

        if warehouse:
            query = query.where(db.Warehouse.description.contains(warehouse))

        series = query.all()

        has_not_serie = lambda object: utils.valid_uuid(object.imei)
        has_serie = lambda object: not utils.valid_uuid(object.imei)

        uuid_group = list(filter(has_not_serie, series))
        sn_group = list(filter(has_serie, series))

        key = operator.attrgetter('item_id', 'condition', 'spec', 'warehouse_id')
        uuid_group = sorted(uuid_group, key=key)

        self.series = []

        # InventoryModel actua como punto comun para los dos tipos de stock
        for entry in sn_group:
            self.series.append(
                InventoryEntry(
                    entry.imei,
                    entry.item.clean_repr,
                    entry.condition,
                    entry.spec,
                    entry.warehouse.description,
                    1
                )
            )

        for key, group in groupby(iterable=uuid_group, key=key):
            item_id, condition, spec, warehouse_id = key
            self.series.append(
                InventoryEntry(
                    '',
                    utils.description_id_map.inverse[item_id],
                    condition,
                    spec,
                    utils.warehouse_id_map.inverse[warehouse_id],
                    len(list(group))
                )
            )

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        entry = self.series[row]
        if role == Qt.DisplayRole:
            if column == self.SERIE:
                return entry.serie
            elif column == self.DESCRIPTION:
                return entry.description
            elif column == self.CONDITION:
                return entry.condition
            elif column == self.SPEC:
                return entry.spec
            elif column == self.WAREHOUSE:
                return entry.warehouse
            elif column == self.QUANTITY:
                return entry.quantity

    def excel_export(self, path):
        from openpyxl import Workbook
        book = Workbook()
        sheet = book.active

        for entry in self.series:
            sheet.append((
                entry.serie,
                entry.description,
                entry.condition,
                entry.spec,
                entry.warehouse,
                entry.quantity
            ))

        book.save(path)


class WarehouseListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.warehouses = [w for w in db.session.query(db.Warehouse)]

    def rowCount(self, index):
        return len(self.warehouses)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self.warehouses[index.row()].description

    def delete(self, row):
        try:
            warehouse = self.warehouses[row]
        except IndexError:
            return
        else:
            db.session.delete(warehouse)
            try:
                db.session.commit()
                del self.warehouses[row]
                self.layoutChanged.emit()
            except:
                db.session.rollback()
                raise

    def add(self, warehouse_name):
        if warehouse_name in self.warehouses:
            raise ValueError

        warehouse = db.Warehouse(warehouse_name)
        db.session.add(warehouse)
        try:
            db.session.commit()
            self.warehouses.append(warehouse)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise


class ConditionListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.conditions = [c for c in db.session.query(db.Condition)]

    def rowCount(self, index=QModelIndex()):
        return len(self.conditions)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self.conditions[index.row()].description

    def delete(self, row):
        try:
            condition = self.conditions[row]
        except:
            return
        else:
            if condition == 'Mix': return
            db.session.delete(condition)
            try:
                db.session.commit()
                del self.conditions[row]
                self.layoutChanged.emit()
            except:
                db.session.rollback()
                raise

    def add(self, condition_name):
        if condition_name in self.conditions:
            raise ValueError
        condition = db.Condition(condition_name)
        db.session.add(condition)
        try:
            db.session.commit()
            self.conditions.append(condition)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise


class CourierListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.couriers = db.session.query(db.Courier).all()

    def rowCount(self, index=QModelIndex()):
        return len(self.couriers)

    def data(self, index, role=QModelIndex()):
        if not index.isValid(): return
        if role == Qt.DisplayRole:
            return self.couriers[index.row()].description

    def delete(self, row):
        try:
            courier = self.couriers[row]
        except IndexError:
            return
        else:
            db.session.delete(courier)
            try:
                db.session.commit()
                del self.couriers[row]
                self.layoutChanged.emit()
            except:
                db.session.rollback()
                raise

    def add(self, name):

        if name in self:
            raise ValueError

        courier = db.Courier(name)
        db.session.add(courier)
        try:
            db.session.commit()
            self.couriers.append(courier)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise

    def __contains__(self, name):
        for e in self.couriers:
            if name == e.description:
                return True
        return False


class SpecListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.specs = [s for s in db.session.query(db.Spec)]

    def rowCount(self, index=QModelIndex()):
        return len(self.specs)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return
        if role == Qt.DisplayRole:
            return self.specs[index.row()].description

    def delete(self, row):
        try:
            spec = self.specs[row]
        except IndexError:
            return
        else:
            if spec == 'Mix': return
            db.session.delete(spec)
            try:
                db.session.commit()
                del self.specs[row]
                self.layoutChanged.emit()
            except:
                db.session.rollback()
                raise

    def add(self, spec_name):
        if spec_name in self.specs:
            raise ValueError

        spec = db.Spec(spec_name)
        db.session.add(spec)
        try:
            db.session.commit()
            self.specs.append(spec)
            self.layoutChanged.emit()
        except:
            db.session.rollback()
            raise


class ReceptionSeriesModel:

    def __init__(self, reception):
        self.reception = reception
        self.reception_series = db.session.query(db.ReceptionSerie). \
            join(db.ReceptionLine).join(db.Reception). \
            where(db.Reception.id == reception.id).all()

    def add(self, line, serie, description, condition, spec):
        if serie.lower() in [o.serie.lower() for o in self.reception_series]:
            raise ValueError('Serie already processed in this reception order')

        if any((
                description not in utils.description_id_map.keys(),
                condition not in utils.conditions.difference({'Mix'}),
                spec not in utils.specs.difference({'Mix'})
        )): raise ValueError('Invalid description, condition or spec')

        reception_serie = db.ReceptionSerie(
            utils.description_id_map[description],
            line, serie, condition, spec
        )
        db.session.add(reception_serie)
        try:
            db.session.commit()
            self.reception_series.append(reception_serie)
        except:
            db.session.rollback()
            raise

    def add_invented(self, line, qnt, description, condition, spec):

        import uuid
        reception_series = []
        if qnt > 0:
            for i in range(qnt):
                reception_series.append(
                    db.ReceptionSerie(
                        utils.description_id_map[description],
                        line, str(uuid.uuid4()), condition, spec
                    )
                )
            db.session.add_all(reception_series)
            try:
                db.session.commit()
                self.reception_series.extend(reception_series)
            except:
                db.session.rollback()
                raise

        elif qnt < 0:
            # No podemos hacer LIMIT en sqlalchemy, damos este rodeo
            qnt = abs(qnt)
            counter, targets = 0, []
            for serie in self.reception_series:
                if all((
                        serie.item_id == utils.description_id_map[description],
                        serie.line_id == line.id,
                        serie.condition == condition,
                        serie.spec == spec
                )):
                    counter += 1
                    targets.append(serie)
                    if counter == qnt:
                        break

            for target in targets:
                db.session.delete(target)

            try:
                db.session.commit()
                for t in targets:
                    self.reception_series.remove(t)
            except:
                db.session.rollback()
                raise

    def delete(self, series):
        delete_targets = [r for r in self.reception_series \
                          if r.serie in series]

        for t in delete_targets:
            db.session.delete(t)
        try:
            db.session.commit()
            for t in delete_targets:
                self.reception_series.remove(t)
        except:
            db.session.rollack()
            raise

    def processed_in(self, line):
        return sum(1 for o in self.reception_series if o.line_id == line.id)

    def __len__(self):
        return len(self.reception_series)


class DefinedSeriesModel(QtCore.QAbstractListModel):

    def __init__(self, rs_model, \
                 line, description, condition, spec):
        super().__init__()
        self.rs_model = rs_model

        self.series = [r.serie for r in rs_model.reception_series \
                       if all((
                r.line_id == line.id,
                r.item_id == utils.description_id_map[description],
                r.condition == condition,
                r.spec == spec
            ))]

    def clear(self):
        self.layoutAboutToBeChanged.emit()
        self.series = []
        self.layoutChanged.emit()

    def rowCount(self, index):
        return len(self.series)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return
        if role == Qt.DisplayRole:
            return self.series[index.row()]

    def index_of(self, key):
        for index, serie in enumerate(self.series):
            if key in serie:
                return index

    def __contains__(self, key):
        for serie in self.series:
            if key in serie:
                return True
        return False


Group = namedtuple('Group', 'description condition spec quantity')


class GroupModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SPEC, QUANTITY = 0, 1, 2, 3

    def __init__(self, rs_model, line):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'Spec', 'Quantity']
        self.name = 'groups'
        key = attrgetter('item_id', 'condition', 'spec')

        series = rs_model.reception_series
        _filter = lambda o: o.line_id == line.id
        series = list(filter(_filter, series))
        series = sorted(series, key=key)

        self.groups = []
        for key, group in groupby(iterable=series, key=key):
            item_id, condition, spec = key
            self.groups.append(
                Group(utils.description_id_map.inverse[item_id],
                      condition, spec, len(list(group)))
            )

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return
        row, col = index.row(), index.column()
        group = self.groups[row]
        if role == Qt.DisplayRole:
            return {
                self.__class__.DESCRIPTION: group.description,
                self.__class__.CONDITION: group.condition,
                self.__class__.SPEC: group.spec,
                self.__class__.QUANTITY: group.quantity
            }.get(col)

    def sort(self, section, order):
        attr = {
            self.DESCRIPTION: 'description',
            self.CONDITION: 'condition',
            self.SPEC: 'spec',
            self.QUANTITY: 'quantity'
        }.get(section)

        if attr:
            reverse = True if order == Qt.AscendingOrder else False
            self.layoutAboutToBeChanged.emit()
            self.groups.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    def group_exists(self, description, condition, spec):
        pass
        for group in self.groups:
            if all((
                    group.description == description,
                    group.condition == condition,
                    group.spec == spec
            )):
                return True
        return False

    def __len__(self):
        return len(self.groups)


class EditableGroupModel(GroupModel):

    def __init__(self, rs_model, line, form):
        self.line = line
        self.rs_model = rs_model
        self.form = form
        super().__init__(rs_model, line)

    def flags(self, index):
        if not index.isValid(): return Qt.ItemIsEnabled
        if index.column() == self.__class__.QUANTITY:
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False
        try:
            v = int(value)
            if v < 0:
                raise ValueError
        except ValueError:
            return False

        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            if index.column() == self.__class__.QUANTITY:
                try:
                    new_processed = int(value)
                    if new_processed < 0:
                        raise ValueError
                except ValueError:
                    return False
                try:
                    group = self.groups[row]
                    old_processed = self.groups[row].quantity
                    actual_item = group.description
                    condition = group.condition
                    spec = group.spec
                    self.rs_model.add_invented(self.line,
                                               new_processed - old_processed,
                                               actual_item, condition, spec
                                               )
                    self.form.populate_body()
                    return True

                except:
                    raise  # debug
                    return False
        return True


class AdvancedStockModel(StockModel):
    DESCRIPTION, CONDITION, SPEC, QUANTITY, REQUEST = 0, 1, 2, 3, 4

    def __init__(self, warehouse_id=None, line=None):
        super(QtCore.QAbstractTableModel, self).__init__()

        self._headerData = ['Description', 'Condition', 'Spec',
                            'Quantity avail. ', 'Requested quant.']
        self.name = 'stocks'

        if line is None or warehouse_id is None:
            self.stocks = []
        else:
            self.stocks = self.computeStock(warehouse_id, line)

    @property
    def requested_stocks(self):
        return list(filter(lambda s: s.request > 0, self.stocks))

    def computeStock(self, warehouse_id, line):

        query = db.session.query(
            db.ImeiMask.item_id, db.ImeiMask.condition,
            db.ImeiMask.spec, func.count(db.ImeiMask.imei).label('quantity')
        ).where(
            db.ImeiMask.origin_id == line.origin_id,
            db.ImeiMask.warehouse_id == warehouse_id,
        ).group_by(
            db.ImeiMask.item_id, db.ImeiMask.condition, db.ImeiMask.spec
        )

        if line.condition != 'Mix':
            query = query.where(db.ImeiMask.condition == line.condition)

        if line.spec != 'Mix':
            query = query.where(db.ImeiMask.spec == line.spec)

        if line.item_id:
            query = query.where(db.ImeiMask.item_id == line.item_id)

        elif line.mixed_description:
            item_ids = utils.get_itemids_from_mixed_description(line.mixed_description)
            query = query.where(db.ImeiMask.item_id.in_(item_ids))

        imeis = {
            StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query
        }

        query = db.session.query(
            db.AdvancedLineDefinition.item_id,
            db.AdvancedLineDefinition.condition,
            db.AdvancedLineDefinition.spec,
            func.sum(db.AdvancedLineDefinition.quantity).label('quantity')
        ).where(
            db.AdvancedLineDefinition.local_count_relevant == True
        ).group_by(
            db.AdvancedLineDefinition.item_id,
            db.AdvancedLineDefinition.condition,
            db.AdvancedLineDefinition.spec
        )

        defined = {
            StockEntry(r.item_id, r.condition, r.spec, r.quantity)
            for r in query
        }

        for d in defined:
            for imei in imeis:
                if imei == d:
                    imei -= d

        return list(filter(lambda s: s.quantity > 0, imeis))


class DefinedStockModel(BaseTable, QtCore.QAbstractTableModel):
    DESCRIPTION, CONDITION, SPEC, REQUESTED = 0, 1, 2, 3

    def __init__(self, line):
        super().__init__()
        self.line = line
        self._headerData = ['Description', 'Condition', 'Spec', 'Requested']
        self.name = 'definitions'
        self.definitions = line.definitions

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            definition = self.definitions[row]

            if col == self.DESCRIPTION:
                return definition.item.clean_repr
            elif col == self.CONDITION:
                return definition.condition
            elif col == self.SPEC:
                return definition.spec
            elif col == self.REQUESTED:
                return definition.quantity

    def add(self, *requested_stocks,
            showing_condition=None):
        for stock in requested_stocks:
            self.line.definitions.append(
                db.AdvancedLineDefinition(
                    item_id=stock.item_id,
                    condition=stock.condition,
                    spec=stock.spec,
                    quantity=stock.request,
                    showing_condition=showing_condition
                )
            )

        db.session.flush()

    def reset(self):
        self.layoutAboutToBeChanged.emit()
        self.line.definitions.clear()
        self.definitions = self.line.definitions
        db.session.flush()
        self.layoutChanged.emit()


class BankAccountModel(BaseTable, QtCore.QAbstractTableModel):
    NAME, IBAN, SWIFT, ADDRESS, POSTCODE, CITY, STATE, COUNTRY, ROUTING, CURRENCY = \
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9

    def __init__(self, partner):
        super().__init__()
        self.accounts = partner.accounts
        self.name = 'accounts'
        self._headerData = ['Name', 'Iban', 'Swift', 'Address', \
                            'Post code', 'City', 'State', 'Country', 'Routing', 'Currency']

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            account = self.accounts[row]
            return {
                self.__class__.NAME: account.bank_name,
                self.__class__.IBAN: account.iban,
                self.__class__.SWIFT: account.swift,
                self.__class__.ADDRESS: account.bank_address,
                self.__class__.POSTCODE: account.bank_postcode,
                self.__class__.CITY: account.bank_city,
                self.__class__.STATE: account.bank_state,
                self.__class__.COUNTRY: account.bank_country,
                self.__class__.ROUTING: account.bank_routing,
                self.__class__.CURRENCY: account.currency
            }.get(col)

    def add(self, name, iban, swift, address, postcode, city, state, country, \
            routing, currency):
        self.layoutAboutToBeChanged.emit()
        account = db.PartnerAccount(name, iban, swift, address, postcode, \
                                    city, state, country, routing, currency)
        self.accounts.append(account)
        self.layoutChanged.emit()

    def delete(self, row):

        self.layoutAboutToBeChanged.emit()

        del self.accounts[row]

        self.layoutChanged.emit()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False
        row, col = index.row(), index.column()
        account = self.accounts[row]
        if role == Qt.EditRole:
            if col == self.__class__.NAME:
                account.bank_name = value
            elif col == self.__class__.IBAN:
                account.iban = value
            elif col == self.__class__.ADDRESS:
                account.bank_address = value
            elif col == self.__class__.SWIFT:
                account.swift = value
            elif col == self.__class__.POSTCODE:
                account.bank_postcode = value
            elif col == self.__class__.CITY:
                account.bank_city = value
            elif col == self.__class__.STATE:
                account.bank_state = value
            elif col == self.__class__.COUNTRY:
                account.bank_country = value
            elif col == self.__class__.ROUTING:
                account.bank_routing = value
            elif col == self.__class__.CURRENCY:
                account.currency = value
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)


from db import Spec, Condition, Warehouse


class ChangeModel(BaseTable, QtCore.QAbstractTableModel):
    SN, DESCRIPTION, HINT = 0, 1, 2

    def __init__(self, hint=None):

        from importlib import reload
        global utils
        utils = reload(utils)

        super().__init__()
        self.hint = hint
        self._headerData = ['IMEI/SN', 'Description', hint.capitalize()]

        self.sns = []
        self.name = 'sns'
        self.hint = hint

        self.set_things()

    def set_things(self):
        if self.hint == 'warehouse':
            self.attrname = 'warehouse.description'
            self.orm_class = Warehouse
            self.orm_change_class = db.WarehouseChange
        elif self.hint == 'spec':
            self.attrname = 'spec'
            self.orm_class = Spec
            self.orm_change_class = db.SpecChange
        elif self.hint == 'condition':
            self.attrname = 'condition'
            self.orm_class = Condition
            self.orm_change_class = db.ConditionChange

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            imei_object = self.sns[row]
            if column == self.SN:
                return imei_object.imei
            elif column == self.DESCRIPTION:
                return imei_object.item.clean_repr
            elif column == self.HINT:
                if self.hint == 'warehouse':
                    return imei_object.warehouse.description
                return getattr(imei_object, self.attrname)

    def search(self, sn):
        if sn in self:
            return

        imei_objects = db.session.query(db.Imei).where(db.Imei.imei == sn).all()
        self.sns.extend(imei_objects)
        self.layoutChanged.emit()

    def apply(self, name, comment):

        if self.hint == 'warehouse':

            for imei_object in self.sns:
                before = imei_object.warehouse.description
                after = name
                db.session.add(db.WarehouseChange(imei_object.imei, before, after, comment))
                imei_object.warehouse_id = utils.warehouse_id_map.get(name)
        else:

            for imei_object in self.sns:
                before = getattr(imei_object, self.attrname)
                after = name
                db.session.add(self.orm_change_class(imei_object.imei, before, after, comment))
                setattr(imei_object, self.attrname, name)

        try:
            db.session.commit()
            self.layoutChanged.emit()
        except:
            raise

    def __contains__(self, sn):
        sn = sn.lower()
        for e in self.sns:
            if e.imei.lower() == sn:
                return True
        else:
            return False


def export_sale_excel(proforma, file_path):
    from openpyxl import Workbook
    from utils import build_description

    book = Workbook()
    sheet = book.active

    header = ['Imei/SN', 'Description', 'Condition', 'Spec']

    # Document Date
    # Customer
    # Supplpier
    # Agente primera parte

    try:
        # type_num = str(proforma.invoice.type) + '-' + str(proforma.invoice.number).zfill(6)

        type_num = 'FR ' + proforma.invoice.doc_repr
        document_date = str(proforma.invoice.date)

    except AttributeError:
        type_num = 'PR' + proforma.doc_repr
        document_date = ''

    sheet.append([
        'Document Date = ' + document_date,
        'Document Number = ' + type_num,
        'Customer = ' + proforma.partner.trading_name,
        'Supplier = ' + 'Euromedia Investment Group S.L. ',
        'Agent = ' + proforma.agent.fiscal_name.split()[0]
    ])

    sheet.append([])

    sheet.append(header)

    for row in generate_excel_rows(proforma):
        sheet.append(list(row))

    book.save(file_path)


def generate_excel_rows(proforma):
    for eline in proforma.expedition.lines:
        condition = eline.showing_condition or eline.condition
        spec = get_spec(eline)
        description = eline.item.clean_repr
        for serie in eline.series:
            yield serie.serie, description, condition, spec


def get_spec(eline: db.ExpeditionLine):
    for pline in eline.expedition.proforma.lines:
        if all((
                eline.item_id == pline.item_id,
                eline.condition == eline.condition,
                eline.spec == eline.spec
        )):
            if pline.ignore_spec:
                return ''
            else:
                return pline.spec


class WhRmaIncomingModel(BaseTable, QtCore.QAbstractTableModel):
    ID, PARTNER, DATE, QUANTITY, STATUS, INVOICED = 0, 1, 2, 3, 4, 5

    def __init__(self, search_key=None, filters=None, last=10):
        super().__init__()
        self._headerData = ['ID', 'Partner', 'Date', 'Quantity', 'Status', 'Invoiced']
        self.name = 'orders'

        query = db.session.query(db.WhIncomingRma).join(db.IncomingRma)
        query = query.where(db.IncomingRma.date > utils.get_last_date(last))
        self.orders = query.all()


    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        order = self.orders[row]

        if role == Qt.DisplayRole:
            if column == self.ID:
                return str(order.id).zfill(6)
            elif column == self.PARTNER:
                return order.incoming_rma.lines[0].cust
            elif column == self.DATE:
                return order.incoming_rma.date.strftime('%d/%m/%Y')
            elif column == self.STATUS:
                if all((line.accepted for line in order.lines)):
                    return 'Accepted'
                elif all((not line.accepted for line in order.lines)):
                    return 'Rejected'
                elif len({line.accepted for line in order.lines}) == 2:
                    return 'Partially accepted'
            elif column == self.INVOICED:
                return 'Yes' if order.sale_invoice is not None else 'No'

            elif column == self.QUANTITY:
                return str(len(order.lines)) + ' pcs '

        elif role == Qt.DecorationRole:
            if column == self.STATUS:
                if all((line.accepted for line in order.lines)):
                    return QtGui.QColor(GREEN)
                elif all((not line.accepted for line in order.lines)):
                    return QtGui.QColor(RED)
                elif len({line.accepted for line in order.lines}) == 2:
                    return QtGui.QColor(ORANGE)
            elif column == self.DATE:
                return QtGui.QIcon(':\calendar')


from utils import warehouse_id_map


class CreditNoteLineModel(BaseTable, QtCore.QAbstractTableModel):
    ITEM, CONDITION, SPEC, QUANTITY, PRICE, TAX = 0, 1, 2, 3, 4, 5

    def __init__(self, lines):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'Spec', 'Quantity', 'Price', 'Tax']
        self.name = 'lines'
        self.lines = lines

    @property
    def subtotal(self):
        return sum(line.price * line.quantity for line in self.lines)

    @property
    def tax(self):
        return sum(line.quantity * line.price * line.tax / 100 for line in self.lines)

    @property
    def total(self):
        return self.subtotal + self.tax

    @property
    def quantity(self):
        return sum(line.quantity for line in self.lines)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            line = self.lines[row]
            if column == self.ITEM:
                return description_id_map.inverse[line.item_id]
            elif column == self.CONDITION:
                return line.condition
            elif column == self.SPEC:
                return line.spec
            elif column == self.QUANTITY:
                return str(line.quantity)
            elif column == self.PRICE:
                return str(line.price)
            elif column == self.TAX:
                return str(line.tax)


class WhRmaIncomingLineModel(BaseTable, QtCore.QAbstractTableModel):
    SN, DESCRIPTION, CONDITION, SPEC, PROBLEM, ACCEPTED, WHY, WAREHOUSE = 0, 1, 2, 3, 4, 5, 6, 7

    def __init__(self, lines):
        super().__init__()
        self._headerData = ['SN/IMEI', 'Description', 'Condt.', 'Spec',
                            'Problem', 'Accepted', 'Why', 'Target WH']
        self.name = 'lines'
        self.lines = lines

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            line = self.lines[row]
            if column == self.SN:
                return line.sn
            elif column == self.PROBLEM:
                return line.problem
            elif column == self.WHY:
                return line.why
            elif column == self.ACCEPTED:
                return 'y' if line.accepted else 'n'
            elif column == self.WAREHOUSE:
                return warehouse_id_map.inverse[line.warehouse_id]
            elif column == self.DESCRIPTION:
                return line.item.clean_repr
            elif column == self.CONDITION:
                return line.condition
            elif column == self.SPEC:
                return line.spec

    def flags(self, index):
        # return Qt.ItemIsEditable

        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() in (self.WHY, self.ACCEPTED, self.WAREHOUSE):
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.EditRole:
            line = self.lines[row]
            if column == self.WHY:
                line.why = value
                return True
            elif column == self.ACCEPTED:
                value = value.lower()
                if value in ('y', 'n'):
                    line.accepted = value == 'y'
                    return True
            elif column == self.WAREHOUSE:
                try:
                    line.warehouse_id = warehouse_id_map[value]
                    return True
                except KeyError:
                    return False
            return False
        return False


class RmaIncomingModel(BaseTable, QtCore.QAbstractTableModel):
    ID, PARTNER, DATE, QNT, STATUS, INWH = 0, 1, 2, 3, 4, 5

    def __init__(self, search_key=None, filters=None, last=10):
        super().__init__()
        self.name = 'orders'
        self._headerData = ['ID', 'Partner', 'Date', 'Quantity', 'Status', 'In WH']

        query = db.session.query(db.IncomingRma).where(db.IncomingRma.date > utils.get_last_date(last))

        self.orders = query.all()



    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        if not index.isValid():
            return

        row, column = index.row(), index.column()
        rma_order = self.orders[row]
        if role == Qt.DisplayRole:
            if column == self.ID:
                return str(rma_order.id).zfill(6)
            elif column == self.DATE:
                return rma_order.date.strftime('%d/%m/%Y')
            elif column == self.PARTNER:
                try:
                    return rma_order.lines[0].cust
                except IndexError:
                    return 'Unknown'

            elif column == self.STATUS:
                if all((line.accepted for line in rma_order.lines)):
                    return 'Accepted'
                elif all((not line.accepted for line in rma_order.lines)):
                    return 'Rejected'
                elif len({line.accepted for line in rma_order.lines}) == 2:  # We found both
                    return 'Partially Accepted'
            elif column == self.INWH:
                return 'Yes' if rma_order.wh_incoming_rma is not None else 'No'
            elif column == self.QNT:
                return str(len(rma_order.lines)) + ' pcs'

        elif role == Qt.DecorationRole:
            if column == self.DATE:
                return QtGui.QIcon(':\calendar')
            elif column == self.STATUS:
                if all((line.accepted for line in rma_order.lines)):
                    return QtGui.QColor(GREEN)
                elif all((not line.accepted for line in rma_order.lines)):
                    return QtGui.QColor(RED)
                elif len({line.accepted for line in rma_order.lines}) == 2:  # We found both
                    return QtGui.QColor(ORANGE)

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        reverse = True if order == Qt.AscendingOrder else False
        attr = {
            self.ID: 'id',
            self.DATE: 'date'
        }.get(column)
        if attr:
            self.layoutAboutToBeChanged.emit()
            self.orders.sort(key=operator.attrgetter(attr), reverse=reverse)
            self.layoutChanged.emit()

    def to_warehouse(self, row):
        rma_order: db.IncomingRma = self.orders[row]
        wh_rma_order = db.WhIncomingRma(rma_order)

        if all((not line.accepted for line in rma_order.lines)):
            raise ValueError('Rma not accepted. I will not send to WH')

        # Raises value error if invoice type not found
        for line in rma_order.lines:
            if line.accepted:
                wh_rma_order.lines.append(db.WhIncomingRmaLine(line))
        try:
            db.session.commit()
        except IntegrityError as ex:
            db.session.rollback()
            raise ValueError('Wh order already exists')

    def __getitem__(self, item):
        return self.orders[item]


class RmaIncomingLineModel(BaseTable, QtCore.QAbstractTableModel):
    IMEI, SUPP, RCPT, WTYENDSUPP, PURCHAS, DEFAS, SOLD_AS, PUBLIC, CUST, SALE_DATE, \
    EXPED, WTYENDC, PROBLEM, ACCEPTED, WHY = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14

    def __init__(self, lines):
        super().__init__()
        self._headerData = [
            'Imei/SN', 'Supp.', 'Rcpt.', 'Wty. End(S)', 'Pur. as', 'Def. as', 'Sold as', 'Public condt.', 'Cust.',
            'Sale Date', 'Exped.', 'Wty End(C)', 'Problem', 'Accepted (y/n)', 'Why'
        ]
        self.name = 'lines'
        self.lines = lines

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        line: db.IncomingRmaLine = self.lines[row]
        if role == Qt.DisplayRole:
            if column == self.IMEI:
                return line.sn
            elif column == self.SUPP:
                return line.supp
            elif column == self.RCPT:
                return line.recpt.strftime('%d-%m-%Y')
            elif column == self.WTYENDSUPP:
                return str(line.wtyendsupp)
            elif column == self.PURCHAS:
                return line.purchas
            elif column == self.DEFAS:
                return line.defas
            elif column == self.SOLD_AS:
                return line.soldas
            elif column == self.PUBLIC:
                return line.public
            elif column == self.CUST:
                return line.cust
            elif column == self.SALE_DATE:
                return str(line.saledate)
            elif column == self.EXPED:
                return line.exped.strftime('%d-%m-%Y')
            elif column == self.WTYENDC:
                return str(line.wtyendcust)
            elif column == self.PROBLEM:
                return line.problem
            elif column == self.ACCEPTED:
                return 'y' if line.accepted else 'n'
            elif column == self.WHY:
                return line.why

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() in (self.PROBLEM, self.ACCEPTED, self.WHY):
            return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
        else:
            return Qt.ItemFlags(~Qt.ItemIsEditable)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        if role == Qt.EditRole:
            line = self.lines[row]
            if col == self.WHY:
                line.why = value
            elif col == self.PROBLEM:
                line.problem = value
            elif col == self.ACCEPTED:
                value = value.lower()
                if value in ('y', 'n'):
                    line.accepted = value == 'y'
            return True
        return False

    def serie_processed(self, sn):
        for line in self.lines:
            if line.sn == sn:
                return True
        else:
            return False

    def add(self, sn):
        if self.serie_processed(sn):
            raise ValueError('Imei/Sn already processed')
        try:
            self.layoutAboutToBeChanged.emit()
            self.lines.append(db.IncomingRmaLine.from_sn(sn))
            self.layoutChanged.emit()
            db.session.flush()
        except ValueError:
            raise

    def update_warehouse(self):
        # Not necessary to check index error
        wh_order = self.lines[0].incoming_rma.wh_incoming_rma

        if wh_order is not None:

            wh_lines = wh_order.lines
            rma_lines = self.lines

            for line in self.rma_warehouse_difference(rma_lines, wh_lines):
                if line.accepted:
                    wh_order.lines.append(db.WhIncomingRmaLine(line))

            db.session.commit()

            for line in self.warehouse_rma_difference(wh_lines, rma_lines):
                db.session.delete(line)

            db.session.commit()

    @staticmethod
    def warehouse_rma_difference(wh_lines, rma_lines):
        aux = []
        for wh_line in wh_lines:
            for rma_line in rma_lines:
                if wh_line.sn == rma_line.sn:
                    break
            else:
                aux.append(wh_line)
        return aux

    @staticmethod
    def rma_warehouse_difference(rma_lines, wh_lines):
        aux = []
        for rma_line in rma_lines:
            for wh_line in wh_lines:
                if rma_line.sn == wh_line.sn:
                    break
            else:
                aux.append(rma_line)
        return aux

    def delete(self, row):
        self.layoutAboutToBeChanged.emit()
        self.lines.pop(row)
        db.session.flush()
        self.layoutChanged.emit()

    def __iter__(self):
        return iter(self.lines)

    def __bool__(self):
        return bool(self.lines)


class ChangeModelTrace(BaseTable, QtCore.QAbstractTableModel):
    FROM, TO, WHEN, COMMENT = 0, 1, 2, 3

    def __init__(self, Sqlalchemy_cls, imei):
        super().__init__()
        self._headerData = ['FROM', 'TO', 'WHEN', 'COMMENT']
        self.registers = db.session.query(Sqlalchemy_cls). \
            where(Sqlalchemy_cls.sn == imei).all()
        self.name = 'registers'

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        r = self.registers[row]

        if role == Qt.DisplayRole:
            if col == self.FROM:
                return r.before
            elif col == self.TO:
                return r.after
            elif col == self.WHEN:
                return str(r.created_on)
            elif col == self.COMMENT:
                return str(r.comment)


class TraceEntry:

    def __str__(self):
        return str(self.__dict__)


class OperationModel(BaseTable, QtCore.QAbstractTableModel):
    OPERATION, DOC, DATE, PARTNER, PICKING = 0, 1, 2, 3, 4

    def __init__(self, imei):
        super().__init__()
        self._headerData = ['Operation', 'Doc', 'Date', 'Partner', 'Picking']
        self.name = 'entries'
        self.entries = []

        query = db.session.query(db.ReceptionSerie). \
            join(db.ReceptionLine).join(db.Reception). \
            join(db.PurchaseProforma). \
            where(db.ReceptionSerie.serie == imei)

        for r in query:
            te = TraceEntry()
            te.operation = 'Purchase'
            # Get doc
            try:
                te.doc = 'FR ' + r.line.reception.proforma.invoice.doc_repr
            except AttributeError:
                te.doc = 'PR ' + r.line.reception.proforma.doc_repr

            # Get date:
            try:
                te.date = r.line.reception.proforma.invoice.date
            except AttributeError:
                te.date = r.line.reception.proforma.date

            te.partner = r.line.reception.proforma.partner.fiscal_name
            te.picking = r.created_on

            self.entries.append(te)

        query = db.session.query(db.ExpeditionSerie).join(db.ExpeditionLine). \
            join(db.Expedition).join(db.SaleProforma).where(db.ExpeditionSerie.serie == imei)

        for r in query:
            te = TraceEntry()
            te.operation = 'Sale'
            try:
                te.doc = 'FR ' + r.line.expedition.proforma.invoice.doc_repr
            except AttributeError:
                te.doc = 'PR ' + r.line.expedition.proforma.doc_repr

            try:
                te.date = r.line.expedition.proforma.invoice.date
            except AttributeError:
                te.date = r.line.expedition.proforma.date

            te.partner = r.line.expedition.proforma.partner.fiscal_name
            te.picking = r.created_on

            self.entries.append(te)

        query = db.session.query(db.WhIncomingRmaLine).join(db.WhIncomingRma).join(db.SaleInvoice)\
            .where(db.WhIncomingRmaLine.sn == imei)

        for r in query:
            te = TraceEntry()
            te.operation = 'Incoming Rma'
            te.doc = 'FR ' + r.wh_incoming_rma.sale_invoice.doc_repr
            te.date = r.wh_incoming_rma.sale_invoice.date
            te.partner = r.wh_incoming_rma.incoming_rma.lines[0].cust
            te.picking = 'Not Registered'

            self.entries.append(te)


        self.entries.sort(key=lambda te: te.date)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        if not index.isValid():
            return
        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            te = self.entries[row]
            if col == self.OPERATION:
                return te.operation
            elif col == self.DOC:
                return te.doc
            elif col == self.DATE:
                return str(te.date)
            elif col == self.PARTNER:
                return te.partner
            elif col == self.PICKING:
                return str(te.picking)


def find_last_description(sn):
    try:
        obj = db.session.query(db.Imei).where(db.Imei.imei == sn).one()
        obj: db.Imei
    except NoResultFound:
        obj = None

    if obj:
        return ', '.join((obj.item.clean_repr, obj.condition + ' Condt.',
                          obj.spec + ' Spec'))
    else:
        exp_series = db.session.query(db.ExpeditionSerie). \
            join(db.ExpeditionLine).where(db.ExpeditionSerie.serie == sn).all()

        try:
            exp_serie = exp_series[-1]
        except IndexError:
            return "Not found neither in stock nor in sales."
        else:
            line = exp_serie.line
            return ', '.join(
                (
                    line.item.clean_repr,
                    line.condition + ' Condt.',
                    line.spec + ' Spec'
                )
            )


def build_credit_note_and_commit(partner_id, agent_id, order):
    # print('type=', type, 'wh=', warehouse_id, 'partn=', partner_id, 'lines=', wh_rma_lines)
    from datetime import datetime

    proforma = db.SaleProforma()
    proforma.type = order.lines[0].invoice_type
    number = db.session.query(db.func.max(db.SaleProforma.number).label('number')).scalar()

    proforma.number = number + 1
    proforma.partner_id = partner_id
    proforma.warehouse_id = None
    proforma.date = datetime.now().date()
    proforma.cancelled = False
    proforma.agent_id = agent_id
    proforma.courier_id = 1

    for wh_line in order.lines:
        proforma.credit_note_lines.append(db.CreditNoteLine(wh_line))

    db.session.add(proforma)

    db.session.commit()

    return proforma


class AvailableNoteModel(BaseTable, QtCore.QAbstractTableModel):
    DOCUMENT, SUBTOTAL = 0, 1

    def __init__(self, invoice):
        super().__init__()
        self.parent_invoice = invoice

        self._headerData = ['Document', 'Subtotal']

        self.name = 'invoices'
        self.invoices = db.session.query(db.SaleInvoice).join(db.SaleProforma).join(db.Partner). \
            where(db.Partner.id == invoice.proforma.partner.id). \
            where(db.SaleProforma.warehouse_id == None). \
            where(db.SaleInvoice.parent_id == None).all()

    def add(self, rows):
        # Set relationship and add payment
        for row in rows:
            invoice = self.invoices[row]
            invoice.parent_id = self.parent_invoice.id
            self.parent_invoice.proforma.payments.append(
                db.SalePayment(
                    date=invoice.date,
                    amount=invoice.subtotal,
                    rate=1.0,
                    note=invoice.cn_repr,
                    proforma=self.parent_invoice.proforma
                )
            )

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise
            # raise ValueError

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            invoice = self.invoices[row]
            if column == self.DOCUMENT:
                return invoice.doc_repr
            elif column == self.SUBTOTAL:
                return invoice.subtotal


class AppliedNoteModel(BaseTable, QtCore.QAbstractTableModel):
    DOCUMENT, SUBTOTAL = 0, 1

    def __init__(self, invoice):
        super().__init__()
        self._headerData = ['Document', 'Subtotal']
        self.name = 'invoices'
        self.parent_invoice = invoice

        self.invoices = db.session.query(db.SaleInvoice). \
            where(db.SaleInvoice.parent_id == self.parent_invoice.id).all()

    def delete(self, rows):
        from db import delete
        for row in rows:
            invoice = self.invoices[row]
            invoice.parent_id = None
            stmt = delete(db.SalePayment).where(db.SalePayment.note == invoice.cn_repr)
            db.session.execute(stmt)
            try:
                db.session.commit()
            except Exception as ex:
                raise ValueError(str(ex))

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return
        row, column = index.row(), index.column()
        if role == Qt.DisplayRole:
            invoice = self.invoices[row]
            if column == self.DOCUMENT:
                return invoice.doc_repr
            elif column == self.SUBTOTAL:
                return invoice.subtotal

    @property
    def credit_notes_subtotal(self):
        return abs(sum(i.subtotal for i in self.invoices))


class SIIInvoice:

    def __init__(self, invoice):
        self.invoice_number = invoice.doc_repr
        self.partner_name = invoice.proforma.partner.fiscal_name
        self.partner_ident = invoice.proforma.partner.fiscal_number
        self.country_code = utils.get_country_code(invoice.proforma.partner.billing_country)
        self.invoice_date = invoice.date.strftime('%d-%m-%Y')

        self.lines = []

        lines = invoice.proforma.lines or \
            invoice.proforma.advanced_lines or \
            invoice.proforma.credit_note_lines

        for line in lines:
            self.lines.append(SIILine(line))

        self.ambos_tax = len({line.tax for line in self.lines}) == 2

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.invoice_number}, {self.partner_name}, \"" \
               f"{self.partner_ident}, {self.country_code})"


class SIILine:

    def __init__(self, line):
        self.quantity = line.quantity
        self.price = line.price
        self.tax = line.tax
        self.is_stock = False
        if isinstance(line, db.SaleProformaLine):
            if line.item_id is not None:
                self.is_stock = True
        elif isinstance(line, db.AdvancedLine):
            if line.item_id is not None or line.mixed_description is not None:
                self.is_stock = True
        elif isinstance(line, db.CreditNoteLine):
            self.is_stock = True
        self.line_type = self.resolve_line_type()

    def resolve_line_type(self):
        booleans = (self.is_stock, self.tax != 0, self.price > 0)
        return int(''.join(str(int(b)) for b in booleans), base=2)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.quantity}, {self.price}, {self.tax}, {self.is_stock}) "


def do_sii(_from=None, to=None, series=None):
    import os
    jsonfeed = os.path.abspath(r'.\data.json')
    jsonresponse = os.path.abspath(r'.\response.json')

    from db import (
        session,
        SaleInvoice,
        SaleProforma,
        Partner
    )

    siiinovices: list[SIIInvoice] = []
    for invoice in session.query(SaleInvoice).join(SaleProforma).join(Partner). \
            where(SaleInvoice.date >= _from). \
            where(SaleInvoice.date <= to). \
            where(SaleInvoice.type.in_(series)):

        siiinovices.append(SIIInvoice(invoice))

    import json
    import subprocess
    import os

    with open(jsonfeed, 'w') as fp:
        json.dump(siiinovices, default=lambda o: o.__dict__, fp=fp, indent=4)

    completed_subprocess = subprocess.run(['sii', jsonfeed, jsonresponse], shell=True)

    with open(jsonresponse, 'r') as fp:
        return json.load(fp)


class SIILogModel(BaseTable, QtCore.QAbstractTableModel):

    NUMBER, DATE, STATUS, MESSAGE = 0, 1, 2, 3

    def __init__(self, registers):
        super().__init__()
        self._headerData = ['Invoice Number', 'Date', 'Status', 'Message']
        self.registers = registers
        self.name = 'registers'

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        if not index.isValid():
            return

        if role == Qt.DisplayRole:
            row, column = index.row(), index.column()
            reg = self.registers[row]
            if column == self.NUMBER:
                return reg['invoice_number']
            elif column == self.DATE:
                return reg['invoice_date']
            elif column == self.STATUS:
                return reg['invoice_status']
            elif column == self.MESSAGE:
                return reg['message']

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        item = {
            self.NUMBER: 'invoice_number',
            self.STATUS: 'invoice_status',
            self.DATE: 'invoice_date',
            self.MESSAGE: 'message'
        }.get(column)

        if item:
            self.layoutAboutToBeChanged.emit()
            self.registers = sorted(self.registers, key=operator.itemgetter(item),
                                    reverse=True if order == Qt.DescendingOrder else False)
            self.layoutChanged.emit()


if __name__ == '__main__':
    do_sii()
