

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5 import QtGui

from sqlalchemy import inspect, or_ 
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select, func

import db 
import operator

from utils import build_description


from exceptions import DuplicateLine, SeriePresentError, LineCompletedError

class BaseTable:

    def headerData(self, section, orientation, role = Qt.DisplayRole):
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



class AgentModel(QtCore.QAbstractTableModel):

    ID, NAME, PHONE, EMAIL, COUNTRY, ACTIVE = 0, 1, 2, 3, 4, 5

    def __init__(self, search_key=None):
        super().__init__()
        self._headerData = ['Code', 'Agent', 'Phone Nº', 'E-mail', 'Country', 'Active'] 
        self.session = db.Session() 
        query = self.session.query(db.Agent)
        
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
                if agent.active :
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
        self.session.add(agent)
        try:
            self.session.commit() 
            self.agents.append(agent) 
            self.layoutChanged.emit() 
        except:
            self.session.rollback()
            raise 

    def update(self, agent):
        for old_agent in self.agents:
            if old_agent.id == agent.id:
                break
        old_agent.fiscal_name = agent.fiscal_name
        old_agent.fiscal_number = agent.fiscal_number 
        old_agent.email = agent.email 
        old_agent.phone = agent.phone 
        old_agent.active = agent.active
        old_agent.country = agent.country
        old_agent.fixed_salary = agent.fixed_salary
        old_agent.from_profit = agent.from_profit
        old_agent.from_turnover = agent.from_turnover
        old_agent.fixed_perpiece = agent.fixed_perpiece
        old_agent.bank_name = agent.bank_name
        old_agent.iban = agent.iban
        old_agent.swift = agent.swift
        old_agent.bank_address = agent.bank_address
        old_agent.bank_postcode = agent.bank_postcode 
        old_agent.bank_city = agent.bank_city
        old_agent.bank_state = agent.bank_state
        old_agent.bank_country = agent.bank_country
        old_agent.bank_routing = agent.bank_routing

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def delete(self, index):
        if not index.isValid():
            return
        row = index.row() 
        candidate_agent = self.agents[row]
        self.session.delete(candidate_agent)
        try:
            self.session.commit() 
            # Dont check ValueError, this code executes only if self.agents is populated
            self.agents.remove(candidate_agent)
            self.layoutChanged.emit() 

        except IntegrityError:
            self.session.rollback() 
            raise 

    def sort(self, section, order):
        attr = {AgentModel.NAME:'fiscal_name', AgentModel.EMAIL:'email', \
            AgentModel.COUNTRY:'country'}.get(section)
        if attr:
            self.layoutAboutToBeChanged.emit() 
            self.agents = sorted(self.agents, key=operator.attrgetter(attr), \
                reverse = True if order == Qt.DescendingOrder else False)    
            self.layoutChanged.emit() 

# Example key = 'agent_id' , value=2 
# Neccesary as arguments for setattr and getattr to build general XDocuemnt SqlAlchemy Objects
class DocumentModel(QtCore.QAbstractListModel):

    EDITABLE_MODE, NEW_MODE = 0, 1 

    def __init__(self, key, value, sqlAlchemyChildClass, sqlAlchemyParentClass):
        super().__init__()
        self.session = db.Session() 
        self.key = key
        self.value = value  
        self.sqlAlchemyChildClass = sqlAlchemyChildClass
        self.sqlAlchemyParentClass = sqlAlchemyParentClass
        self.documents = self.session.query(sqlAlchemyChildClass). \
            join(sqlAlchemyParentClass).where(getattr(sqlAlchemyChildClass, key) == value).all() 

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and 0 <= index.row() < len(self.documents):
            if role == Qt.DecorationRole:
                return QtGui.QIcon(':\pdf')
            if role == Qt.DisplayRole:
                return self.documents[index.row()].name 

    def rowCount(self, index):
        return len(self.documents) 

    def delete(self, index):
        document = self.documents[index.row()]
        self.session.delete(document)
        try:
            self.session.commit()
            del self.documents[index.row()]
            self.layoutChanged.emit()
        except:
            self.session.rollback()
            raise 


    def add(self, filename, base64Pdf):
        document = self.sqlAlchemyChildClass(name=filename, document=base64Pdf)
        setattr(document, self.key, self.value)
        self.session.add(document)        
        try:
            self.session.commit()
            self.documents.append(document)
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 

class PartnerModel(QtCore.QAbstractTableModel):

    CODE, TRADING_NAME, FISCAL_NAME, FISCAL_NUMBER, COUNTRY, CONTACT, PHONE, EMAIL, ACTIVE = \
        0, 1, 2, 3, 4, 5, 6, 7, 8

    def __init__(self, search_key=None):
        super().__init__()

        self._headerData = ['Code', 'Trading Name', 'Fiscal Name', 'Fiscal Number', 'Country', 'Contact', \
            'Phone', 'E-mail', 'Active']
        self.session = db.Session() 
        query = self.session.query(db.Partner).outerjoin(db.PartnerContact)
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
        partner:db.Partner
        column = index.column() 
        if role == Qt.DisplayRole:
            return self.col_to_data_map(column, partner)
        elif role == Qt.DecorationRole:
            if column == PartnerModel.ACTIVE:
                return QtGui.QIcon(':\greentick') if partner.active else \
                    QtGui.QIcon(':\cross')
        
    def columnCount(self, index=QModelIndex()):
        return len(self._headerData)

    def rowCount(self, index = QModelIndex()):
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
            PartnerModel.CODE:'id', 
            PartnerModel.FISCAL_NAME:'fiscal_name', 
            PartnerModel.FISCAL_NUMBER:'fiscal_number', 
            PartnerModel.TRADING_NAME:'trading_name', 
            PartnerModel.COUNTRY:'billing_country'
        }.get(section)

        if attr:
            self.layoutAboutToBeChanged.emit()
            self.partners.sort(key=operator.attrgetter(attr), \
                reverse = True if Qt.AscendingOrder else False)
            self.layoutChanged.emit() 
    
    def add(self, partner):
        self.session.add(partner)
        try:
            self.session.commit()
            self.partners.append(partner)
            self.layoutChanged.emit()
        except:
            self.session.rollback()
            raise 
    
    def delete(self, index):
        if not index.isValid():
            return
        row = index.row()
        candidate_partner = self.partners[row]
        self.session.delete(candidate_partner)
        try:
            self.session.commit()
            self.partners.remove(candidate_partner)
            self.layoutChanged.emit()
        except:
            self.session.rollback()
            raise 

    def col_to_data_map(self, col, partner:db.Partner):
        return {
            PartnerModel.CODE: partner.id, 
            PartnerModel.TRADING_NAME:partner.trading_name, 
            PartnerModel.FISCAL_NAME:partner.fiscal_name, 
            PartnerModel.FISCAL_NUMBER:partner.fiscal_number, 
            PartnerModel.COUNTRY:partner.billing_country, 
            PartnerModel.CONTACT:partner.contacts[0].name, 
            PartnerModel.PHONE:partner.contacts[0].phone, 
            PartnerModel.EMAIL:partner.contacts[0].email, 
            PartnerModel.ACTIVE:'YES' if partner.active else 'NO'
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
        self.beginRemoveRows(QModelIndex(), position,  position + rows - 1)
        self.contacts.pop(position)
        self.endRemoveRows()
        return True 


class InvoiceModel(BaseTable, QtCore.QAbstractTableModel):
     
    TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    
    def __init__(self, sale=False, search_key=None, filters=None):
        super().__init__() 
        self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', 'Financial', \
            'Logistic', 'Shipment', 'Owing', 'Total']
        self.session = db.session
        self.name = 'invoices'

        self.Proforma = db.PurchaseProforma    
        if sale:
            self.Proforma = db.SaleProforma
        
        self.invoices = self.session.query(self.Proforma).where(self.Proforma.invoice != None).all()         


    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return 
        
        row, col = index.row(), index.column()
        proforma = self.invoices[row]

        if col in (InvoiceModel.FINANCIAL, InvoiceModel.OWING, InvoiceModel.TOTAL):
            paid = sum([payment.amount for payment in proforma.payments])
            total_debt = sum([line.quantity * line.price for line in proforma.lines])
        elif col == InvoiceModel.LOGISTIC:
            total_quantity = sum([line.quantity for line in proforma.lines])
            try:
                processed_quantity = 0 
                for line in proforma.order.lines:
                    for serie in line.series:
                        processed_quantity+=1 
            except AttributeError:
                processed_quantity = 0 

        if role == Qt.DisplayRole:
            if col == InvoiceModel.TYPE_NUM:
                s = str(proforma.invoice.type) + '-' + str(proforma.invoice.number).zfill(6)
                return s 
            elif col == InvoiceModel.DATE:
                return proforma.date.strftime('%d/%m/%Y')
            elif col == InvoiceModel.ETA:
                return proforma.eta.strftime('%d/%m/%Y')
            elif col == InvoiceModel.PARTNER:
                return proforma.partner.fiscal_name 
            elif col == InvoiceModel.AGENT:
                return proforma.agent.fiscal_name 
            elif col == InvoiceModel.FINANCIAL:
                if proforma.cancelled:
                    return 'Cancelled'     
                else:
                    if paid == 0:
                        return 'Not Paid'
                    elif 0 < paid < total_debt:
                        return 'Partial Paid' 
                    elif paid == total_debt:
                        return 'Paid'
                    elif paid > total_debt:
                        return 'They Owe'

            elif col == InvoiceModel.LOGISTIC:
                if processed_quantity == 0:
                    return "Waiting Stock"
                elif 0 < processed_quantity < total_quantity:
                    return "Partially Received"
                elif processed_quantity == total_quantity:
                    return 'Fully Received'
            elif col == PurchaseProformaModel.SENT:
                return "Sent" if proforma.sent else "Not Sent"
            elif col == PurchaseProformaModel.OWING:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt - paid) + sign       
            elif col == PurchaseProformaModel.TOTAL:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt) + sign

        elif role == Qt.DecorationRole:
            if col == InvoiceModel.FINANCIAL:
                if proforma.cancelled:
                    return QtGui.QIcon(':\cross')
                else:
                    if total_debt == paid:
                        return QtGui.QIcon(':\greentick')
                    elif paid == 0 or (0 < paid < total_debt) or (paid > total_debt) :
                        return QtGui.QIcon(':\cross')
            elif col == InvoiceModel.DATE or col == InvoiceModel.ETA:
                return QtGui.QIcon(':\calendar')
            elif col == InvoiceModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == InvoiceModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif col == InvoiceModel.SENT:
                return QtGui.QIcon(':\greentick') if proforma.sent else QtGui.QIcon(':\cross')
            elif col == InvoiceModel.LOGISTIC:
                if processed_quantity == 0:
                    return QtGui.QIcon(':\cross')
                elif processed_quantity == total_quantity:
                    return QtGui.QIcon(':\greentick')
                elif 0 < processed_quantity < total_quantity:
                    return QtGui.QIcon(':\cross')
    
    def sort(self, section, order):
        pass 
    
class PurchaseProformaModel(BaseTable, QtCore.QAbstractTableModel):
    
    TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 

    def __init__(self, filters=None, search_key=None):  
        super().__init__() 
        self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', 'Financial', 'Logistic', \
            'Shipment', 'Owing', 'Total']
        self.name = 'proformas'
        db.session = db.Session() 
        self.session = db.session 
        query = self.session.query(db.PurchaseProforma) 

        if search_key:
            query = query.where(db.PProforma.date.contains(search_key)) 

        self.proformas = query.all() 

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return 
        row, col = index.row(), index.column()
        proforma = self.proformas[row]

        if col in (PurchaseProformaModel.FINANCIAL, PurchaseProformaModel.OWING, PurchaseProformaModel.TOTAL):
            paid = sum([payment.amount for payment in proforma.payments])
            total_debt = sum([line.quantity * line.price for line in proforma.lines])
        elif col == PurchaseProformaModel.LOGISTIC:
            total_quantity = sum([line.quantity for line in proforma.lines])
            try:
                processed_quantity = 0 
                for line in proforma.order.lines:
                    for serie in line.series:
                        processed_quantity+=1 
            except AttributeError:
                processed_quantity = 0 

        if role == Qt.DisplayRole:
            if col == PurchaseProformaModel.TYPE_NUM:
                s = str(proforma.type) + '-' + str(proforma.number).zfill(6)
                return s 
            elif col == PurchaseProformaModel.DATE:
                return proforma.date.strftime('%d/%m/%Y')
            elif col == PurchaseProformaModel.ETA:
                return proforma.eta.strftime('%d/%m/%Y')
            elif col == PurchaseProformaModel.PARTNER:
                return proforma.partner.fiscal_name 
            elif col == PurchaseProformaModel.AGENT:
                return proforma.agent.fiscal_name 
            elif col == PurchaseProformaModel.FINANCIAL:
                if proforma.cancelled:
                    return 'Cancelled'     
                else:
                    if paid == 0 and total_debt > paid:
                        return 'Not Paid'
                    elif 0 < paid < total_debt:
                        return 'Partial Paid' 
                    elif paid == total_debt:
                        return 'Paid'
                    elif paid > total_debt:
                        return 'They Owe'

            elif col == PurchaseProformaModel.LOGISTIC:
                if processed_quantity == 0:
                    return "Waiting Stock"
                elif 0 < processed_quantity < total_quantity:
                    return "Partially Received"
                elif processed_quantity == total_quantity:
                    return 'Fully Received'
            elif col == PurchaseProformaModel.SENT:
                return "Sent" if proforma.sent else "Not Sent"
            elif col == PurchaseProformaModel.OWING:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt - paid) + sign       
            elif col == PurchaseProformaModel.TOTAL:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt) + sign

        elif role == Qt.DecorationRole:
            if col == PurchaseProformaModel.FINANCIAL:
                if proforma.cancelled:
                    return QtGui.QIcon(':\cross')
                else:
                    if total_debt == paid:
                        return QtGui.QIcon(':\greentick')
                    elif paid == 0 or (0 < paid < total_debt) or (paid > total_debt) :
                        return QtGui.QIcon(':\cross')
            elif col == PurchaseProformaModel.DATE or col == PurchaseProformaModel.ETA:
                return QtGui.QIcon(':\calendar')
            elif col == PurchaseProformaModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == PurchaseProformaModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif col == PurchaseProformaModel.SENT:
                return QtGui.QIcon(':\greentick') if proforma.sent else QtGui.QIcon(':\cross')
            elif col == PurchaseProformaModel.LOGISTIC:
                if processed_quantity == 0:
                    return QtGui.QIcon(':\cross')
                elif processed_quantity == total_quantity:
                    return QtGui.QIcon(':\greentick')
                elif 0 < processed_quantity < total_quantity:
                    return QtGui.QIcon(':\cross')

    def sort(self, section, order):
        reverse = True if order == Qt.DescendingOrder else False
        if section == PurchaseProformaModel.TYPE_NUM:
            self.layoutAboutToBeChanged.emit() 
            self.proformas.sort(key = lambda p : (p.type, p.number), reverse=reverse) 
            self.layoutChanged.emit() 

        else:
            attr = {
                PurchaseProformaModel.DATE:'date', 
                PurchaseProformaModel.PARTNER:'partner.trading_name', 
                PurchaseProformaModel.AGENT:'agent.fiscal_name',
                PurchaseProformaModel.SENT:'sent', 
            }.get(section) 
            
            if attr:
                self.layoutAboutToBeChanged.emit() 
                self.proformas.sort(key=operator.attrgetter(attr), reverse=reverse)
                self.layoutChanged.emit() 

    def add(self, proforma):
        self.session.add(proforma)
        try:
            self.session.commit()
            self.proformas.append(proforma) 
            self.layoutChanged.emit()   
        except:
            self.session.rollback()
            raise 
    
    def nextNumberOfType(self, type):
        current_num = self.session.query(func.max(db.PurchaseProforma.number)). \
            where(db.PurchaseProforma.type == type).scalar()  
        return 1 if not current_num else current_num + 1 
    
    def cancel(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            p = self.proformas[row]
            if not p.cancelled:
                p.cancelled = True 
        try:
            self.session.commit()
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 

    def associateInvoice(self, proforma):
        current_num = self.session.query(db.PurchaseInvoice.number).\
            where(db.PurchaseInvoice.type == proforma.type).scalar() 
        if current_num: 
            next_num = current_num + 1 
        else:
            next_num = 1 
        proforma.invoice = db.PurchaseInvoice(proforma.type, next_num)
        try:
            self.session.commit() 
            return proforma.invoice 
            # Should reset PurchaseInvoice model through a reference to parent
        except:
            self.session.rollback() 
            raise 

    def ship(self, proforma, tracking):
        proforma.tracking = tracking
        proforma.sent = True
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise 

    def toWarehouse(self, proforma, note):
        # put this code in wareohouse model 
        order = db.PurchaseOrder(proforma, proforma.warehouse, note) 
        self.session.add(order) 
        for line in proforma.lines:
            self.session.add(db.PurchaseOrderLine(order, line.item, line.condition,\
                line.specification, line.quantity))    
        try:
            self.session.commit() 
        except:
            self.session.rollback() 
            raise

class SaleProformaModel(BaseTable, QtCore.QAbstractTableModel):
    
    TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

    def __init__(self, search_key=None, filters=None):
        super().__init__() 
        self._headerData = ['Type  & Num', 'Date', 'ETA', 'Partner','Agent', 'Financial', 'Logistic',\
            'Shipment', 'Owes', 'Total']
        self.proformas = [] 
        self.name = 'proformas'
        db.sale_session = db.Session() 
        self.session = db.sale_session
        query = self.session.query(db.SaleProforma) 

        if search_key:
            query = query.join(db.Partner).where(Partner.fiscal_name.contains(saerch_key))
        
        self.proformas = query.all() 
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return 
        row, col = index.row(), index.column()
        proforma = self.proformas[row]

        if col in (SaleProformaModel.FINANCIAL, SaleProformaModel.OWING, SaleProformaModel.TOTAL):
            paid = sum([payment.amount for payment in proforma.payments])
            total_debt = sum([line.quantity * line.price for line in proforma.lines])
        elif col == SaleProformaModel.LOGISTIC:
            total_quantity = sum([line.quantity  for line in proforma.lines])
            try:
                processed_quantity = 0 
                for line in proforma.order.lines:
                    for serie in line.series:
                        processed_quantity+=1 
            except AttributeError:
                processed_quantity = 0 

        if role == Qt.DisplayRole:
            if col == SaleProformaModel.TYPE_NUM:
                s = str(proforma.type) + '-' + str(proforma.number).zfill(6)
                return s 
            elif col == SaleProformaModel.DATE:
                return proforma.date.strftime('%d/%m/%Y')
            elif col == SaleProformaModel.ETA:
                return proforma.eta.strftime('%d/%m/%Y')
            elif col == SaleProformaModel.PARTNER:
                return proforma.partner.fiscal_name 
            elif col == SaleProformaModel.AGENT:
                return proforma.agent.fiscal_name 
            elif col == SaleProformaModel.FINANCIAL:
                if proforma.cancelled:
                    return 'Cancelled'     
                else:
                    if paid == 0 and total_debt > paid:
                        return 'Not Paid'
                    elif 0 < paid < total_debt:
                        return 'Partial Paid' 
                    elif paid == total_debt:
                        return 'Paid'
                    elif paid > total_debt:
                        return 'We Owe'

            elif col == SaleProformaModel.LOGISTIC:
                if processed_quantity == 0:
                    return "Waiting Stock"
                elif 0 < processed_quantity < total_quantity:
                    return "Partially Received"
                elif processed_quantity == total_quantity:
                    return 'Fully Received'
            elif col == SaleProformaModel.SENT:
                return "Sent" if proforma.sent else "Not Sent"
            elif col == SaleProformaModel.OWING:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt - paid) + sign       
            elif col == SaleProformaModel.TOTAL:
                sign = ' -€' if proforma.eur_currency else ' $'
                return str(total_debt) + sign

        elif role == Qt.DecorationRole:
            if col == SaleProformaModel.FINANCIAL:
                if proforma.cancelled:
                    return QtGui.QIcon(':\cross')
                else:
                    if total_debt == paid:
                        return QtGui.QIcon(':\greentick')
                    elif paid == 0 or (0 < paid < total_debt) or (paid > total_debt) :
                        return QtGui.QIcon(':\cross')
            elif col == SaleProformaModel.DATE or col == SaleProformaModel.ETA:
                return QtGui.QIcon(':\calendar')
            elif col == SaleProformaModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif col == SaleProformaModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif col == SaleProformaModel.SENT:
                return QtGui.QIcon(':\greentick') if proforma.sent else QtGui.QIcon(':\cross')
            elif col == SaleProformaModel.LOGISTIC:
                if processed_quantity == 0:
                    return QtGui.QIcon(':\cross')
                elif processed_quantity == total_quantity:
                    return QtGui.QIcon(':\greentick')
                elif 0 < processed_quantity < total_quantity:
                    return QtGui.QIcon(':\cross')


    def sort(self, section, order):
        reverse = True if order == Qt.DescendingOrder else False
        if section == SaleProformaModel.TYPE_NUM:
            self.layoutAboutToBeChanged.emit() 
            self.proformas.sort(key = lambda p : (p.type, p.number), reverse=reverse) 
            self.layoutChanged.emit() 

        else:
            attr = {
                SaleProformaModel.DATE:'date', 
                SaleProformaModel.PARTNER:'partner.trading_name', 
                SaleProformaModel.AGENT:'agent.fiscal_name',
                SaleProformaModel.SENT:'sent', 
            }.get(section) 
            
            if attr:
                self.layoutAboutToBeChanged.emit() 
                self.proformas.sort(key=operator.attrgetter(attr), reverse=reverse)
                self.layoutChanged.emit() 

    def add(self, proforma):
        self.session.add(proforma)
        try:
            self.session.commit()
            self.proformas.append(proforma) 
            self.layoutChanged.emit()   
        except:
            self.session.rollback()
            raise 
    
    def nextNumberOfType(self, type):
        current_num = self.session.query(func.max(db.SaleProforma.number)). \
            where(db.SaleProforma.type == type).scalar()  
        if not current_num: # Means first number of type
            return 1 
        else:
            return current_num + 1 
    
    def cancel(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            p = self.proformas[row]
            if not p.cancelled:
                p.cancelled = True 
        try:
            self.session.commit()
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 

    def associateInvoice(self, proforma):
        current_num = self.session.query(db.SaleInvoice.number).\
            where(db.SaleInvoice.type == proforma.type).scalar() 
        if current_num: 
            next_num = current_num + 1 
        else:
            next_num = 1 
        proforma.invoice = db.SaleInvoice(proforma.type, next_num)
        try:
            self.session.commit() 
            return proforma.invoice 
        except:
            self.session.rollback() 
            raise 

    def ship(self, proforma, tracking):
        proforma.tracking = tracking
        proforma.sent = True
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise 

    def toWarehouse(self, proforma, note):
        order = db.SaleOrder(proforma, proforma.warehouse, note) 
        self.session.add(order) 
        for line in proforma.lines:
            self.session.add(db.SaleOrderLine(order, line.item, line.condition,\
                line.specification, line.quantity))    
        try:
            self.session.commit() 
        except:
            self.session.rollback() 
            raise

class SaleProformaLineModel(BaseTable, QtCore.QAbstractTableModel):

    def __init__(self, session):
        super().__init__() 
        self._headerData = ['Description', 'Condition', 'Spec', 'Qty.', 'Price', 'Subtotal', 'Tax', 'Total']   
        self.session = session
        self.name = 'lines'
        self.lines = []
    
    def data(self):
        pass 

class ProductModel(BaseTable, QtCore.QAbstractTableModel):

    def __init__(self):

        super().__init__() 
        self.session = db.Session() 
        self._headerData = ['Manufacturer', 'Category', 'Model', 'Capacity', 'Color']
        self.name = 'items'
        self.items = self.session.query(db.Item).all() 
        

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return

        item = self.items[index.row()]
        col = index.column() 
        if role != Qt.DisplayRole:
            return
        else:
            return {
                0:item.manufacturer, 
                1:item.category, 
                2:item.model, 
                3:item.capacity, 
                4:item.color 
            }.get(col) 

    def addItem(self, manufacturer, category, model, capacity, color):
        item = db.Item(manufacturer, category, model, capacity, color) 
        self.session.add(item)

        try:
            self.session.commit()
            self.items.append(item)
            self.layoutChanged.emit() 
        except:
            self.session.rollback()
            raise 

    def removeItem(self, index):
        if not index.isValid():
            return
        row = index.row() 
        candidate = self.items[row]
        self.session.delete(candidate) 
        try:
            self.session.commit() 
            del self.items[row]
            self.layoutChanged.emit() 
        except:
            self.session.rollback()
            raise 

class PurchaseProformaLineModel(BaseTable, QtCore.QAbstractTableModel):

    def __init__(self, session):
        super().__init__()
        self._headerData = ['Description', 'Condition', 'Spec', 'Qty.', 'Price', 'Subtotal', 'Tax', 'Total']
        self.session = session
        self.name = 'lines'
        self.lines = [] 


    def data(self, index, role = Qt.DisplayRole):
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
            total = (line.quantity * float(line.price)) * (1 + line.tax/100)
            subtoal = line.quantity * line.price 
            return {
                0:build_description(line.item), 
                1:line.condition,
                2:line.specification, 
                3:str(line.quantity), 
                4:str(line.price), 
                5:str(subtoal), 
                6:str(line.tax), 
                7:str(total)
            }.get(col) 

    @property
    def tax(self):
        return sum([line.quantity * line.price * line.tax / 100 for line in self.lines])

    @property
    def subtotal(self):
        return sum([line.quantity * line.price for line in self.lines])
    
    @property
    def total(self):
        return self.tax + self.subtotal

    def add(self, item, condition, spec, quantity, price, tax):
        
        line = db.PurchaseProformaLine(item, condition, spec, price, quantity, tax) 

        if self._alreadyPresent(line):
            raise DuplicateLine

        self.lines.append(line) 
        self.layoutChanged.emit() 

    def delete(self, indexes):
        rows = { index.row() for index in indexes}
        for row in sorted(rows, reverse=True):
            try:
                del self.lines[row]
            except:
                pass 
        self.layoutChanged.emit() 

    def _alreadyPresent(self, line):
        for _line in self.lines:
            if _line.item.id == line.item.id and _line.specification == line.specification \
                and _line.condition  == line.condition:
                    return True
        else:
            return False

    def save(self, proforma):
        for line in self.lines:
            line.proforma = proforma 
            self.session.add(line) 
        try:
            self.session.commit() 
        except:
            self.session.rollback() 
            raise 

class PaymentModel(BaseTable, QtCore.QAbstractTableModel):

    def __init__(self, session, proforma, sale):
        super().__init__()
        self.session = session 
        self.proforma = proforma 
        self._headerData = ['Date', 'Amount', 'Info']
        self.name = 'payments'
        if sale:
            self.Payment = db.SalePayment
        else:
            self.Payment = db.PurchasePayment

        self.payments = self.session.query(self.Payment).\
            where(self.Payment.proforma.has(id=proforma.id)).all() 

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return 
        payment = self.payments[index.row()]
        column = index.column() 

        if role == Qt.DisplayRole:
            if column == 0:
                return payment.date.strftime('%d/%m/%Y')
            elif column == 1:
                return str(payment.amount) 
            elif column == 2:
                return payment.note
        elif role == Qt.DecorationRole:
            if column == 0:
                return QtGui.QIcon(':\calendar') 
        else:
            return            

    def add(self, date, amount, note):
        payment = self.Payment(date, amount, note, self.proforma)
        self.session.add(payment)
        try:
            self.session.commit()
            self.payments.append(payment)
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 
    
    def delete(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            payment = self.payments[row]
            self.session.delete(payment)
        try:
            self.session.commit() 
        except:
            self.session.rollback() 
            raise 
        else:
            for row in sorted(rows, reverse=True):
                del self.payments[row]
            self.layoutChanged.emit() 

    @property
    def paid(self):
        return sum([p.amount for p in self.payments])

class ExpenseModel(BaseTable, QtCore.QAbstractTableModel):
    
    def __init__(self, session, proforma, sale):
        super().__init__() 
        self.session = session
        self.proforma = proforma
        self._headerData = ['Date', 'Amount', 'Info']
        self.name = 'expenses'
        if sale:
            self.Expense = db.SaleExpense
        else:
            self.Expense = db.PurchaseExpense

        self.expenses = self.session.query(self.Expense).\
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

    def add(self, date, amount, info):
        expense = self.Expense(date, amount, info, self.proforma)
        self.session.add(expense)
        try:
            self.session.commit() 
            self.expenses.append(expense)
            self.layoutChanged.emit() 
        except:
            self.session.rollback()
            raise 

    def delete(self, indexes):
        rows = {index.row() for index in indexes}
        for row in rows:
            expense = self.expenses[row]
            self.session.delete(expense)
        try:
            self.session.commit() 
        except:
            self.session.rollback() 
            raise 
        else:
            for row in sorted(rows, reverse=True):
                del self.expenses[row]
            self.layoutChanged.emit() 

    @property
    def spent(self):
        return sum([expense.amount for expense in self.expenses])

class SerieModel(QtCore.QAbstractListModel):

    def __init__(self, session, line, order, sale=False):
        super().__init__() 
        self.session = session 

        if sale:
            self.Serie = db.SaleSerie
            self.Line = db.SaleOrderLine
            self.Order = db.SaleOrder
        else:
            self.Serie = db.PurchaseSerie
            self.Line = db.PurchaseOrderLine
            self.Order = db.PurchaseOrder

        self.series = self.session.query(self.Serie).join(self.Line).\
            where(self.Serie.line_id == line.id).all()

        self.series_at_order_level  = self.session.query(self.Serie).join(self.Line).join(self.Order).\
            where(self.Order.id == order.id).all() 

    def add(self, line, _serie):

        if self._seriePresent(_serie):
            raise SeriePresentError 

        if line.quantity == len(self.series):
            raise LineCompletedError

        serie = self.Serie() 
        serie.serie = _serie
        serie.line = line 
        self.session.add(serie) 
        try:
            self.session.commit() 
            self.series.append(serie)
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 

    def delete(self, index):
        serie = self.series[index.row()]
        self.session.delete(serie) 
        try:
            self.session.commit() 
            del self.series[index.row()]
            self.layoutChanged.emit() 
        except:
            self.session.rollback() 
            raise 

    def rowCount(self, index):
        return len(self.series)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        if role == Qt.DisplayRole:
            return self.series[index.row()].serie 

    def _seriePresent(self, serie):
        for _serie in self.series_at_order_level:
            if serie == _serie.serie:
                return True 
        else:
            return False

class OrderModel(BaseTable, QtCore.QAbstractTableModel):

    ID, WAREHOUSE, TOTAL, PROCESSED, STATUS, PARTNER, AGENT, WARNING = 0, 1, 2, 3, 4, 5, 6, 7

    def __init__(self, sale=False, search_key=None, filters=None):
        super().__init__() 
        self.session = db.Session() 
        self._headerData = ['Order_id', 'Warehouse', 'Total', 'Processed', 'Status','Partner', 'Agent', 'Warning']
        self.name = 'orders' 
        
        if sale:
            self.Order = db.SaleOrder
        else:
            self.Order = db.PurchaseOrder

        self.query = self.session.query(self.Order)

        if search_key:
            pass 
        
        if filters:
            pass 

        self.orders = self.query.all() 

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return 
        order = self.orders[index.row()]
        column = index.column() 

        if role == Qt.DisplayRole: 
            if column == OrderModel.ID:
                return str(order.id).zfill(6)
            elif column == OrderModel.WAREHOUSE:
                return order.warehouse.description
            elif column == OrderModel.TOTAL:
                return str(self._total(order))
            elif column == OrderModel.PARTNER:
                return order.proforma.partner.fiscal_name
            elif column == OrderModel.PROCESSED:
                return str(self._processed(order)) 
            elif column == OrderModel.STATUS:
                total = self._total(order) 
                processed = self._processed(order) 
                if order.proforma.cancelled:
                    return 'Cancelled'
                else:
                    if total == processed:
                        return 'Completed'
                    elif 0 < processed < total:
                        return 'Partially Prepared'
                    elif processed == 0:
                        return 'Empty'
            elif column == OrderModel.AGENT:
                return order.proforma.agent.fiscal_name 
            elif column == OrderModel.WARNING:
                return order.note 
        elif role == Qt.DecorationRole:
            if column == OrderModel.AGENT:
                return QtGui.QIcon(':\\agents')
            elif column == OrderModel.PARTNER:
                return QtGui.QIcon(':\partners')
            elif column == OrderModel.STATUS:
                if order.proforma.cancelled:
                    return QtGui.QIcon(':\cancel')
                else:
                    total = self._total(order) 
                    processed = self._processed(order) 
                    if total == processed:
                        return QtGui.QIcon(':\greentick')
                    elif 0 < processed < total:
                        return QtGui.QIcon(':\cross')
                    elif processed == 0:
                        return QtGui.QIcon(':\cross')

    def _total(self, order):
        return sum([line.quantity for line in order.lines])

    def _processed(self, order):
        processed = 0
        for line in order.lines:
            for serie in line.series:
                processed += 1
        return processed


from db import Warehouse, Item
from db import PurchaseProformaLine as pl
from db import PurchaseProforma as pp 
from db import session, func
from db import SaleProforma as sp
from db import SaleProformaLine as sl 

class StockEntry:

    def __init__(self, eta, item, warehouse, specification, condition, quantity):
        self.eta = eta
        self.item = str(item) 
        self.specification = specification
        self.condition = condition
        self.warehouse = warehouse 
        self.quantity = quantity        

    def __str__(self):
        return ' '.join([str(v) for v in self.__dict__.values()])

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if self.eta == other.eta and self.item == other.item and self.specification == other.specification \
            and self.condition == other.condition and self.warehouse == other.warehouse:
                return True 
        return False

    def __hash__(self):
        return hash(' '.join([str(v) for v in self.__dict__.values()][:-1]))


class AvailableStockModel(BaseTable, QtCore.QAbstractTableModel):

    def __init__(self, warehouse, *, coming, item_id, condition, specification):

        super().__init__() 
        self._headerData = ['Description', 'Condition', 'Specification', 'ETA', 'quantity']
        self.name = 'stocks'
        self.session = db.Session() 

        purchases_query = self.session.query(pp.eta, Item, Warehouse.description.label('warehouse'), pl.condition, pl.specification, \
            func.sum(pl.quantity).label('quantity')).select_from(pp, pl, Warehouse).group_by(pp.eta, Item.id, pl.condition,\
                pl.specification, Warehouse.id).where(pp.id == pl.proforma_id).where(pp.warehouse_id == Warehouse.id).\
                    where(pl.item_id == Item.id).where(Warehouse.description == warehouse).where(pp.order == None)

        sales_query = self.session.query(sp.eta, Item, Warehouse.description.label('warehouse'), sl.condition, sl.specification, \
            func.sum(sl.quantity).label('quantity')).select_from(sp, sl, Warehouse).group_by(sp.eta, Item.id, sl.condition, \
                sl.specification, Warehouse.id).where(sp.id == sl.proforma_id).where(sp.warehouse_id == Warehouse.id).\
                    where(sl.item_id == Item.id).where(Warehouse.description == warehouse)
    
        purchases = { StockEntry(r.eta, r.Item, r.warehouse, r.specification, r.condition, r.quantity) for r in purchases_query}

        sales = { StockEntry(r.eta, r.Item, r.warehouse, r.specification, r.condition, r.quantity) for r in sales_query}
        
        for sale in sales:
            for purchase in purchases:
                if sale == purchase:
                    purchase.quantity -= sale.quantity       

        aux = sales.difference(purchases) 
        
        self.stocks = list(filter(lambda o : o.quantity != 0, purchases)) 

        if aux:
            for e in aux:
                e.quantity = (-1) * e.quantity 
            self.stocks += list(aux) 

        del self.session

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row, column = index.row(), index.column() 
        entry = self.stocks[row]
        if role == Qt.DisplayRole:
            if column == 0:
                return entry.item 
            elif column == 1:
                return entry.condition
            elif column == 2:
                return entry.specification 
            elif column == 3:
                return entry.eta.strftime('%d/%m/%Y')
            elif column == 4:
                return str(entry.quantity) + ' pcs'
        elif role == Qt.DecorationRole:
            if column == 3:
                return QtGui.QIcon(':\calendar')


if __name__ == '__main__':

    SaleProformaModel(search_key='xyz')