from collections import namedtuple

from collections.abc import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5 import QtGui

from sqlalchemy import inspect, or_ 
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select, func

import db, utils

import operator

from copy import deepcopy

from exceptions import DuplicateLine, SeriePresentError, LineCompletedError

# COLORS:
# RED FOR CANCELLED
# GREEN FOR COMPLETED
# ORANGE FOR EMPTY OR PARTIAL
# YELLOW FOR OVERFLOW
RED, GREEN, YELLOW, ORANGE = '#FF7F7F', '#90EE90', '#FFFF66', '#FFD580'

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



def computeCreditAvailable(partner_id):

	max_credit = db.session.query(db.Partner.amount_credit_limit).\
             where(db.Partner.id == partner_id).scalar()

	total = db.session.query(func.sum(db.PurchaseProformaLine.quantity * db.PurchaseProformaLine.price)).\
		select_from(db.Partner, db.PurchaseProforma, db.PurchaseProformaLine).\
			where(db.PurchaseProformaLine.proforma_id == db.PurchaseProforma.id).\
				where(db.PurchaseProforma.partner_id == db.Partner.id).\
					where(db.Partner.id == partner_id).scalar() 

	paid = db.session.query(func.sum(db.PurchasePayment.amount)).select_from(db.Partner, \
		db.PurchaseProforma, db.PurchasePayment).where(db.PurchaseProforma.partner_id == db.Partner.id).\
			where(db.PurchasePayment.proforma_id == db.PurchaseProforma.id).\
				where(db.Partner.id == partner_id).scalar() 
	
	credit_taken = db.session.query(func.sum(db.PurchaseProforma.credit_amount)).\
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

import math 
def get_actual_object(object):
	if isinstance(object, db.Reception):
		return object.proforma
	elif isinstance(object, db.PurchaseProforma):
		return object
	elif isinstance(object, db.SaleProforma):
		return object 
	elif isinstance(object, db.Expedition):
		return object.proforma

def total_debt(proforma):
	return sum([line.quantity * line.price for line in proforma.lines])

def total_paid(proforma):
	return sum([payment.amount for payment in proforma.payments])

def total_quantity(proforma):
	proforma = get_actual_object(proforma) 
	if isinstance(proforma, db.SaleProforma):
		return sum([line.quantity for line in proforma.lines])

	return sum([line.quantity for line in proforma.lines if \
		line.description in utils.descriptions or line.item_id])

def total_processed(proforma):
	proforma = get_actual_object(proforma) 
	if isinstance(proforma, db.PurchaseProforma):
		try:
			return len([1 for line in proforma.reception.lines \
				for serie in line.series])
		except AttributeError:
			return 0 
	elif isinstance(proforma, db.SaleProforma):
		try:
			return len([1 for line in proforma.expedition.lines \
				for serie in line.series])
		except AttributeError:
			return 0 


def empty(proforma):
	return total_processed(proforma) == 0

def partially_processed(proforma):
	return 0 < total_processed(proforma) < total_quantity(proforma) 

def completed(proforma):
	return total_processed(proforma) == total_quantity(proforma) 

def overflowed(proforma):
	proforma = get_actual_object(proforma) 
	try:
		lines_iterable = iter(proforma.reception.lines)
	except AttributeError:
		lines_iterable = iter(proforma.expedition.lines)
	
	for line in lines_iterable:
		try:
			if line.quantity < len(line.series):
				return True 
		except AttributeError:
			continue
	else:
		return False 

def stock_gap():
	return not all(
		completed(expedition)
		for expedition in db.session.query(db.Expedition)
		.join(db.SaleProforma)
		.where(db.SaleProforma.cancelled == False)
		.order_by(db.Expedition.id.desc())
	)

def not_paid(proforma):
	return math.isclose(total_paid(proforma), 0)

def partially_paid(proforma):
	return 0 < total_paid(proforma) < total_debt(proforma)

def fully_paid(proforma):
	return math.isclose(total_paid(proforma), total_debt(proforma))

def overpaid(proforma):
	return total_paid(proforma) > total_debt(proforma) 

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
		db.session.add(agent)
		try:
			db.session.commit() 
			self.agents.append(agent) 
			self.layoutChanged.emit() 
		except:
			db.session.rollback()
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
			db.session.commit()
		except:
			db.session.rollback()
			raise
		self.dataChanged.emit(QModelIndex(), QModelIndex())

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
		self.key = key
		self.value = value  
		self.sqlAlchemyChildClass = sqlAlchemyChildClass
		self.sqlAlchemyParentClass = sqlAlchemyParentClass
		self.documents = db.session.query(sqlAlchemyChildClass). \
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
		db.session.delete(document)
		try:
			db.session.commit()
			del self.documents[index.row()]
			self.layoutChanged.emit()
		except:
			db.session.rollback()
			raise 


	def add(self, filename, base64Pdf):
		document = self.sqlAlchemyChildClass(name=filename, document=base64Pdf)
		setattr(document, self.key, self.value)
		db.session.add(document)        
		try:
			db.session.commit()
			self.documents.append(document)
			self.layoutChanged.emit() 
		except:
			db.session.rollback() 
			raise 

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


class SaleInvoiceModel(QtCore.QAbstractTableModel):
	 
	TYPE_NUM, PROFORMA = 0, 10 
	
	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self.parent_model = SaleProformaModel(
			filters = filters, 
			search_key = search_key, 
			proxy = True 
		)
	
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
				key = lambda p:(p.invoice.type, p.invoice.number), 
				reverse = reverse
			) 
			self.layoutChanged.emit() 

		elif section == self.__class__.PROFORMA:		
			self.layoutAboutToBeChanged.emit()
			self.invoices.sort(
				key = lambda p:(p.type, p.number), 
				reverse = reverse 
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

	


class PurchaseInvoiceModel(QtCore.QAbstractTableModel):
	
	TYPE_NUM, PROFORMA = 0, 11

	def __init__(self, filters=None, search_key=None):
		super().__init__()
		self.parent_model = PurchaseProformaModel(
			filters = filters, 
			search_key=search_key, 
			proxy = True
		)

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
				key = lambda p:(p.invoice.type, p.invoice.number), 
				reverse = reverse
			) 
			self.layoutChanged.emit() 
		
		elif section == self.__class__.PROFORMA:
			self.layoutAboutToBeChanged.emit()
			self.invoices.sort(
				key = lambda p:(p.type, p.number), 
				reverse = reverse 
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

class PurchaseProformaModel(BaseTable, QtCore.QAbstractTableModel):
	
	TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, CANCELLED, \
		OWING, TOTAL, PROFORMA = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 

	def __init__(self, filters=None, search_key=None, proxy=False):  
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', \
			'Financial', 'Logistic', 'Sent', 'Cancelled','Owing', 'Total']
		self.name = 'proformas'
		self.proxy = proxy 

		query = db.session.query(db.PurchaseProforma).\
			select_from(db.Agent, db.Partner).\
				where(
					db.Agent.id == db.PurchaseProforma.agent_id, 
					db.Partner.id == db.PurchaseProforma.partner_id
				)

		if proxy:
			self._headerData.append('From proforma')
			query = query.where(db.PurchaseProforma.invoice != None)

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
				self.proformas = filter(lambda p : p.type in filters['types'], self.proformas)

			if filters['financial']:
				if 'notpaid' in filters['financial']:
					self.proformas = filter(lambda p: not_paid(p), self.proformas)
				if 'fullypaid' in filters['financial']:
					self.proformas = filter(lambda p:fully_paid(p), self.proformas)
				if 'partiallypaid' in filters['financial']:
					self.proformas = filter(lambda p:partially_paid(p) ,self.proformas)
			
			if filters['logistic']:
				if 'overflowed' in filters['logistic']:
					self.proformas = filter(lambda p:overflowed(p), self.proformas)
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:empty(p), self.proformas)
				if 'partially_processed' in filters['logistic']:
					self.proformas = filter(lambda p:partially_processed(p), self.proformas) 
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:completed(p), self.proformas)
				

			if filters['shipment']:
				if 'sent' in filters['shipment']:
					self.proformas = filter(lambda p:p.sent, self.proformas)
				if 'notsent' in filters['shipment']:
					self.proformas = filter(lambda p:not p.sent, self.proformas)

			if filters['cancelled']:
				if 'cancelled' in filters['cancelled']:
					self.proformas = filter(lambda p:p.cancelled,self.proformas)
				if 'notcancelled' in filters['cancelled']:
					self.proformas = filter(lambda p:not p.cancelled, self.proformas) 

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
			elif col == PurchaseProformaModel.PARTNER:
				return proforma.partner.fiscal_name 
			elif col == PurchaseProformaModel.AGENT:
				return proforma.agent.fiscal_name 
			elif col == PurchaseProformaModel.FINANCIAL:
				if not_paid(proforma):
					return "Not Paid"
				elif fully_paid(proforma):
					return "Paid"
				elif partially_paid(proforma):
					return "Partially Paid"
				elif overpaid(proforma):
					return "They owe"
			elif col == PurchaseProformaModel.LOGISTIC:
				if empty(proforma):
					return "Empty"
				elif overflowed(proforma):
					return "Overflowed"	
				elif partially_processed(proforma):
					return "Partially Received"
				elif completed(proforma):
					return "Completed"
			
			elif col == PurchaseProformaModel.SENT:
				return "Yes" if proforma.sent else "No"

			elif col == PurchaseProformaModel.CANCELLED:
				return 'Yes' if proforma.cancelled else 'No'

			elif col == PurchaseProformaModel.OWING:
				sign = ' -€' if proforma.eur_currency else ' $'
				owing = total_debt(proforma) - total_paid(proforma) 
				return str(round(owing, 2)) + sign       
			
			elif col == PurchaseProformaModel.TOTAL:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(round(total_debt(proforma), 2)) + sign
		elif role == Qt.DecorationRole:
			if col == PurchaseProformaModel.FINANCIAL:
				if not_paid(proforma):
					return QtGui.QColor(YELLOW)
				elif fully_paid(proforma):
					return QtGui.QColor(GREEN)
				elif partially_paid(proforma):
					return QtGui.QColor(ORANGE)
				elif overpaid(proforma):
					return QtGui.QColor(YELLOW)
				elif overpaid(proforma):
					return QtGui.QColor(RED) 
			elif col == PurchaseProformaModel.DATE or col == PurchaseProformaModel.ETA:
				return QtGui.QIcon(':\calendar')
			elif col == PurchaseProformaModel.PARTNER:
				return QtGui.QIcon(':\partners')
			elif col == PurchaseProformaModel.AGENT:
				return QtGui.QIcon(':\\agents')
			elif col == PurchaseProformaModel.LOGISTIC:
				if empty(proforma):
					return QtGui.QColor(YELLOW)
				elif overflowed(proforma):
					return QtGui.QColor(RED)
				elif partially_processed(proforma):
					return QtGui.QColor(ORANGE)
				elif completed(proforma):
					return QtGui.QColor(GREEN)
			elif col == PurchaseProformaModel.CANCELLED:
				return QtGui.QColor(RED) if proforma.cancelled else\
					QtGui.QColor(GREEN)
			elif col == PurchaseProformaModel.SENT:
				return QtGui.QColor(GREEN) if proforma.sent else\
					QtGui.QColor(RED)

	def sort(self, section, order):
		reverse = True if order == Qt.AscendingOrder else False
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
				PurchaseProformaModel.ETA:'eta'
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
			self.proformas.append(proforma) 
			self.layoutChanged.emit()   
		except:
			db.session.rollback()
			raise 
	
	def nextNumberOfType(self, type):
		current_num = db.session.query(func.max(db.PurchaseProforma.number)). \
			where(db.PurchaseProforma.type == type).scalar()  
		return 1 if not current_num else current_num + 1 
	
	def cancel(self, indexes):
		rows = {index.row() for index in indexes}
		for row in rows:
			p = self.proformas[row]
			if not p.cancelled:
				p.cancelled = True 
		try:
			# Update advanced lines depending on this purchase
			ids = (line.id for line in p.lines)
			db.session.query(db.AdvancedLine).\
				where(db.AdvancedLine.origin_id.in_(ids)).\
					update({db.AdvancedLine.quantity:0})

			db.session.commit() 
			self.layoutChanged.emit() 
		except:
			db.session.rollback() 
			raise

	def associateInvoice(self, proforma):
		current_num = db.session.query(func.max(db.PurchaseInvoice.number)).\
			where(db.PurchaseInvoice.type == proforma.type).scalar() 
		if current_num: 
			next_num = current_num + 1 
		else:
			next_num = 1 
		proforma.invoice = db.PurchaseInvoice(proforma.type, next_num)
		try:
			db.session.commit() 
			return proforma.invoice 
			# Should reset PurchaseInvoice model through a reference to parent
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
			self.buildReceptionLine(line, reception)
		try:
			db.session.commit() 
		except:
			db.session.rollback() 
			raise

	def buildReceptionLine(self, line, reception):
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

	def updateWarehouse(self, proforma):
		
		if proforma.reception is None:
			return False

		warehouse_lines = set(proforma.reception.lines)
		proforma_lines = set(proforma.lines)
		
		for line in warehouse_lines.difference(proforma_lines):
			line.quantity = 0 
			if sum(1 for serie in line.series) == 0:
				db.session.delete(line) 
		

		for line in proforma_lines.difference(warehouse_lines):
			if line.item_id or line.description in utils.descriptions:
				self.buildReceptionLine(line, proforma.reception)
		
		for proforma_line in proforma_lines:
			for reception_line in proforma.reception.lines:
				if reception_line == proforma_line:
					reception_line.quantity = proforma_line.quantity
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise 
		
	

class SaleProformaModel(BaseTable, QtCore.QAbstractTableModel):
	
	TYPE_NUM, DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, \
		CANCELLED, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, search_key=None, filters=None, proxy=False):
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'Partner','Agent', \
			'Financial', 'Logistic','Sent', 'Cancelled', 'Owes', 'Total']
		self.proformas = [] 
		self.name = 'proformas'
		query = db.session.query(db.SaleProforma).\
			select_from(db.Agent, db.Partner).\
				where(
					db.Agent.id == db.SaleProforma.agent_id, 
					db.Partner.id == db.SaleProforma.partner_id, 
					db.Warehouse.id == db.SaleProforma.warehouse_id
				)

		if proxy:
			self._headerData.append('From proforma')
			query = query.where(db.SaleProforma.invoice != None)
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
				self.proformas = filter(lambda p : p.type in filters['types'], self.proformas)

			if filters['financial']:
				if 'notpaid' in filters['financial']:
					self.proformas = filter(lambda p: not_paid(p), self.proformas)
				if 'fullypaid' in filters['financial']:
					self.proformas = filter(lambda p:fully_paid(p), self.proformas)
				if 'partiallypaid' in filters['financial']:
					self.proformas = filter(lambda p:partially_paid(p) ,self.proformas)

			if filters['logistic']:
				if 'overflowed' in filters['logistic']:
					self.proformas = filter(lambda p:overflowed(p), self.proformas)
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:empty(p), self.proformas)
				if 'partially_processed' in filters['logistic']:
					self.proformas = filter(lambda p:partially_processed(p), self.proformas) 
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:completed(p), self.proformas)
			
			if filters['shipment']:
				if 'sent' in filters['shipment']:
					self.proformas = filter(lambda p:p.sent, self.proformas)
				if 'notsent' in filters['shipment']:
					self.proformas = filter(lambda p:not p.sent, self.proformas)

			if filters['cancelled']:
				if 'cancelled' in filters['cancelled']:
					self.proformas = filter(lambda p:p.cancelled,self.proformas)
				if 'notcancelled' in filters['cancelled']:
					self.proformas = filter(lambda p:not p.cancelled, self.proformas) 

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
			if col == SaleProformaModel.TYPE_NUM:
				s = str(proforma.type) + '-' + str(proforma.number).zfill(6)
				return s 
			elif col == SaleProformaModel.DATE:
				return proforma.date.strftime('%d/%m/%Y')
			elif col == SaleProformaModel.PARTNER:
				return proforma.partner.fiscal_name 
			elif col == SaleProformaModel.AGENT:
				return proforma.agent.fiscal_name 
			elif col == SaleProformaModel.FINANCIAL:
				if not_paid(proforma):
					return 'Not Paid'
				elif fully_paid(proforma):
					return 'Paid' 
				elif partially_paid(proforma):
					return 'Partially Paid'
				elif overpaid(proforma):
					return 'We Owe'
			elif col == SaleProformaModel.LOGISTIC:
				if empty(proforma):
					return 'Empty'
				elif overflowed(proforma):
					return 'Overflowed'
				elif partially_processed(proforma):
					return 'Partially Prepared'
				elif completed(proforma):
					return 'Completed'
			
			elif col == SaleProformaModel.SENT:
				return 'Yes' if proforma.sent else 'No'
			elif col == SaleProformaModel.CANCELLED:
				return 'Yes' if proforma.cancelled else 'No'
			elif col == SaleProformaModel.OWING:
				sign = ' -€' if proforma.eur_currency else ' $'
				owes = total_debt(proforma) - total_paid(proforma)
				return str(round(owes, 2)) + sign       
			elif col == SaleProformaModel.TOTAL:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(round(total_debt(proforma), 2)) + sign

		elif role == Qt.DecorationRole:
			if col == SaleProformaModel.FINANCIAL:
				if not_paid(proforma):
					return QtGui.QColor(YELLOW) 
				elif fully_paid(proforma):
					return QtGui.QColor(GREEN)
				elif partially_paid(proforma):
					return QtGui.QColor(ORANGE)
				elif overpaid(proforma):
					return QtGui.QColor(YELLOW)

			elif col == SaleProformaModel.DATE:
				return QtGui.QIcon(':\calendar')
			elif col == SaleProformaModel.PARTNER:
				return QtGui.QIcon(':\partners')
			elif col == SaleProformaModel.AGENT:
				return QtGui.QIcon(':\\agents')
			elif col == SaleProformaModel.LOGISTIC:
				if empty(proforma):
					return QtGui.QColor(YELLOW)
				elif overflowed(proforma):
					return QtGui.QColor(RED)
				elif partially_processed(proforma):
					return QtGui.QColor(ORANGE)
				elif completed(proforma):
					return QtGui.QColor(GREEN)
			elif col == SaleProformaModel.SENT:
				return QtGui.QColor(GREEN) if proforma.sent \
					else QtGui.QColor(RED)
			elif col == SaleProformaModel.CANCELLED:
				return QtGui.QColor(RED) if proforma.cancelled \
					else QtGui.QColor(GREEN)

	def __getitem__(self, index):
		return self.proformas[index]

	def sort(self, section, order):
		reverse = True if order == Qt.AscendingOrder else False
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
		proforma.number = self.nextNumberOfType(proforma.type)
		db.session.add(proforma)
		try:
			db.session.commit()
			self.proformas.append(proforma)
			self.layoutChanged.emit()
		except:
			db.session.rollback()
			raise 
		
	
	def nextNumberOfType(self, type):
		current_num = db.session.query(func.max(db.SaleProforma.number)). \
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
			db.session.commit()
			self.layoutChanged.emit() 
		except:
			db.session.rollback() 
			raise 

	def associateInvoice(self, proforma):
		current_num = db.session.query(func.max(db.SaleInvoice.number)).\
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

	def ship(self, proforma, tracking):
		proforma.tracking = tracking
		proforma.sent = True
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise 

	def toWarehouse(self, proforma, note):
		expedition = db.Expedition(proforma, note) 
		db.session.add(expedition) 
		for line in proforma.lines:
			exp_line = db.ExpeditionLine()
			exp_line.item_id = line.item_id
			exp_line.condition = line.condition
			exp_line.spec = line.spec 
			exp_line.quantity = line.quantity
			exp_line.expedition = expedition
		try:
			db.session.commit() 
		except:
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
		exp_line = db.ExpeditionLine()
		exp_line.condition = line.condition
		exp_line.spec = line.spec 
		exp_line.item_id = line.item_id 
		exp_line.quantity = line.quantity

		exp_line.expedition = expedition

	def updateWarehouse(self, proforma):
		if proforma.expedition is None:
			return 

		warehouse_lines = set(proforma.expedition.lines)

		proforma_lines = set(
			filter(
				lambda line: line.item_id in utils.description_id_map.values(), 
				proforma.lines
			)
		)

		added_lines = proforma_lines.difference(warehouse_lines)
		for line in added_lines:
			self.build_expedition_line(line, proforma.expedition)
		
		deleted_lines = warehouse_lines.difference(proforma_lines) 
		for line in deleted_lines:
			line.quantity = 0
			if sum(1 for serie in line.series) == 0:
				db.session.delete(line) 

		for proforma_line in proforma_lines:
			for exp_line in proforma.expedition.lines:
				if exp_line == proforma_line:
					exp_line.quantity = proforma_line.quantity
		
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise 


from collections.abc import Iterable 

def copy_line(line):
	l = db.SaleProformaLine() 
	l.item_id = line.item_id
	l.spec = line.spec
	l.condition = line.condition
	l.quantity = line.quantity
	return l 

class OrganizedLines:

	def __init__(self, lines):
		self.instrumented_lines = lines 
		self.initial_lines = [copy_line(line) for line in lines]
		self.organized_lines = self.organize_lines(lines) 
		self.next_mix = self.get_next_mix()

	@property
	def lines(self):
		return self.instrumented_lines

	@property
	def added_lines(self):
		k= set(self.instrumented_lines).\
			difference(set(self.initial_lines)) 
		print('added lines', k)
		return k

	@property
	def deleted_lines(self):
	
		k= set(self.initial_lines).\
			difference(set(self.instrumented_lines))
		print('deleted_lines:', k)
		return k 

	def get_next_mix(self):
		last_mix = db.session.query(func.max(db.SaleProformaLine.mix_id)).scalar()
		if last_mix is None:
			last_mix = 0 
		else:
			last_mix += 1
		return last_mix

	def delete(self, i, j=None):
		if j is None:
			lines = self.organized_lines.pop(i)
			try:
				for line in lines:
					self.instrumented_lines.remove(line)
			except TypeError:
				self.instrumented_lines.remove(lines) 
		else:
			line = self.organized_lines[i].pop(j)
			try:
				if len(self.organized_lines[i]) == 1:
					self.organized_lines[i] = self.organized_lines[i][0]
				elif not self.organize_lines:
					del self.organized_lines[i]
			except IndexError:
				pass 
			
			self.instrumented_lines.remove(line) 

		self.organized_lines = [e for e in self.organized_lines if e]


	def append(self, price, ignore_spec, tax, showing, *stocks, row=None):
		if len(stocks) == 0:
			raise ValueError('At least one stock must be provided')
		if any((
			stock == line
			for line in self.lines
			for stock in stocks
		)):
			raise ValueError("I can't handle duplicate stocks")

		new_lines = [
			self.build_line(
				price, ignore_spec, 
				tax, showing, stock
			) for stock in stocks
		]

		if row is not None:
			group = self.organized_lines[row]
			if isinstance(group, Iterable):
				if self.group_conflict(group, *stocks):
					raise ValueError('You can only mix colors or capacities')
				mix_id = group[0].mix_id
				for line in new_lines:
					line.mix_id = mix_id 
				group.extend(new_lines) 
			else:
				if group.item_id not in utils.description_id_map.values():
					raise ValueError("You cannot add stocks in this line")
					if any((
						self.conflict_check(group)
						for stock in stocks
					)):
						raise ValueError('You can only mix colors or capacities')
				self.organized_lines[row] = [group] + new_lines
		else:
			if len(new_lines) == 1:
				self.organized_lines.append(new_lines[0])
			else:
				if self.group_conflict(stocks, *stocks):
					raise ValueError('You can only mix colors or capacities')
				
				for line in new_lines:
					line.mix_id = self.next_mix
				self.organized_lines.append(new_lines) 
				self.next_mix += 1
		
		self.instrumented_lines.extend(new_lines) 


	def insert_free(self, description, quantity, price, tax):
		
		line = db.SaleProformaLine() 
		line.description = description
		line.quantity = quantity
		line.price = price
		line.tax = tax 

		self.organized_lines.append(line)
		self.instrumented_lines.append(line) 


	def group_conflict(self, lines, *stocks):
		return any((
			self.conflict_check(line, stock)
			for stock in stocks
			for line in lines 
		))
 
	def conflict_check(self, line, stock):
		line_description = utils.description_id_map.inverse[line.item_id]
		line_manufacturer, line_category, line_model, *_ = line_description.split() 
		stock_description = utils.description_id_map.inverse[stock.item_id]
		stock_manufacturer, stock_category, stock_model , *_ = stock_description.split()
		return any((
			line_manufacturer != stock_manufacturer, 
			line_category != stock_category, 
			line_model != stock_model
		))

	def repr(self, row, col):
		line = self.organized_lines[row]
		if isinstance(line, Iterable):
			return self.complex_line_repr(line, col)
		else:
			return self.simple_line_repr(line, col)
	
	def organize_lines(self, lines):
		searched, aux = set(), [] 
		for line in lines:
			if line.mix_id is None:
				aux.append(line) 
			else:
				if line.mix_id not in searched:
					aux.append(
						[l for l in lines if l.mix_id == line.mix_id]
					)
					searched.add(line.mix_id)
		return aux  


	def complex_line_repr(self, lines, col):
		diff_items = {line.item_id for line in lines}
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
		total = subtotal * ( 1 + tax / 100)
		return {
			SaleProformaLineModel.DESCRIPTION:description, 
			SaleProformaLineModel.CONDITION:condition,
			SaleProformaLineModel.SHOWING_CONDITION:showing_condition, 
			SaleProformaLineModel.SPEC:spec, 
			SaleProformaLineModel.IGNORING_SPEC:ignore, 
			SaleProformaLineModel.SUBTOTAL:str(subtotal), 
			SaleProformaLineModel.PRICE:str(price), 
			SaleProformaLineModel.QUANTITY:str(quantity),
			SaleProformaLineModel.TAX:str(tax), 
			SaleProformaLineModel.TOTAL: str(total)
		}.get(col)
	
	def simple_line_repr(self, line, col):
		total = round((line.quantity * line.price) * (1 + line.tax/100), 2)
		subtotal = round(line.quantity * line.price, 2)
		ignore_spec = 'Yes' if line.ignore_spec else 'No'
		showing_condition = line.showing_condition or line.condition
		if  col == SaleProformaLineModel.DESCRIPTION:
			if line.item_id is None:
				return line.description
			else:
				return utils.description_id_map.inverse[line.item_id]
		else:
			return {
				# SaleProformaLineModel.DESCRIPTION:utils.description_id_map.inverse[line.item_id], 
				SaleProformaLineModel.CONDITION:line.condition,
				SaleProformaLineModel.SHOWING_CONDITION:showing_condition, 
				SaleProformaLineModel.SPEC:line.spec, 
				SaleProformaLineModel.IGNORING_SPEC:ignore_spec, 
				SaleProformaLineModel.SUBTOTAL:str(subtotal),
				SaleProformaLineModel.PRICE:str(round(line.price, 2)), 
				SaleProformaLineModel.QUANTITY:str(line.quantity),
				SaleProformaLineModel.TAX:str(line.tax), 
				SaleProformaLineModel.TOTAL: str(total)
			}.get(col) 

	def build_line(self, price, ignore, tax, showing, stock, mix_id=None):
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

	def __init__(self, proforma):
		super().__init__()
		self._headerData = ['Description', 'Condition', 'Showing Condt.', 'Spec', \
			'Ignoring Spec?','Qty.', 'Price', 'Subtotal', 'Tax', 'Total']
		self.organized_lines = OrganizedLines(proforma.lines)
		self.name = 'organized_lines'

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid(): return 
		row, column = index.row(), index.column() 
		if role == Qt.DisplayRole:
			return self.organized_lines.repr(row, column) 

	def get_next_mix(self):
		last_mix = db.session.query(func.max(db.SaleProformaLine.mix_id)).scalar()
		if last_mix is None:
			last_mix = 0 
		else:
			last_mix += 1
		return last_mix

	@property 
	def lines(self):
		return self.organized_lines.lines 

	@property
	def tax(self):
		return sum(map(lambda l:l.tax, self.lines))

	@property
	def subtotal(self):
		return sum(
			line.quantity * line.price * line.tax / 100
			for line in self.lines 
		)
 
	@property
	def total(self):
		return self.tax + self.subtotal

	@property
	def deleted_lines(self):
		return self.organized_lines.deleted_lines
	
	@property
	def added_lines(self):
		return self.organized_lines.added_lines

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
		return self.organized_lines[row]

	def __bool__(self):
		return bool(self.organized_lines)


class ActualLinesFromMixedModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SPEC, REQUEST = 0, 1, 2, 3

	def __init__(self, lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'spec', 'Requested Quantity']
		self.name = 'lines'
		self.lines = lines or []


	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row, column = index.row(), index.column() 
		line = self.lines[row]
		if role == Qt.DisplayRole:
			if column == ActualLinesFromMixedModel.DESCRIPTION:
				return utils.description_id_map.inverse[line.item_id]
			elif column == ActualLinesFromMixedModel.CONDITION:
				return line.condition
			elif column == ActualLinesFromMixedModel.SPEC:
				return line.spec
			elif column == ActualLinesFromMixedModel.REQUEST:
				return str(line.quantity)

	def reset(self):
		self.layoutAboutToBeChanged.emit()
		self.lines = []
		self.layoutChanged.emit() 

class ProductModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self):

		super().__init__() 
		self._headerData = ['Manufacturer', 'Category', 'Model', 'Capacity', 'Color']
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
				0:item.manufacturer, 
				1:item.category, 
				2:item.model, 
				3:item.capacity, 
				4:item.color 
			}.get(col) 

	def addItem(self, manufacturer, category, model, capacity, color):
		item = db.Item(manufacturer, category, model, capacity, color) 
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

class PurchaseProformaLineModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SPEC, QUANTITY, PRICE, SUBTOTAL, \
		TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7

	def __init__(self, lines=None):
		super().__init__()
		self._headerData = ['Description', 'Condition', 'Spec', 'Qty.(Editable)', \
			'Price (Editable)', 'Subtotal', 'Tax (Editable)', 'Total']
		self.name = 'lines'
		self.lines = lines or [] 

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
			total = round((line.quantity * line.price) * (1 + line.tax/100), 2) 
			subtotal = round(line.quantity * line.price) 
			# Allowing mixed and precised lines:
			if col == 0:
				if line.description is not None:
					return line.description
				else:
					return utils.description_id_map.inverse[line.item_id]
			return {
				self.__class__.CONDITION:line.condition,
				self.__class__.SPEC:line.spec, 
				self.__class__.QUANTITY:str(line.quantity), 
				self.__class__.PRICE:str(line.price), 
				self.__class__.SUBTOTAL:str(subtotal), 
				self.__class__.TAX:str(line.tax), 
				self.__class__.TOTAL:str(total)
			}.get(col) 

	def setData(self, index, value, role=Qt.EditRole):
		if not index.isValid():return False
		row, column = index.row(), index.column()
		if not self.editable_column(column):return False
		line = self.lines[row]
		if role == Qt.EditRole:
			if column == self.__class__.PRICE:
				try:
					value = float(value)
				except: return False
				else:
					line.price = value 
					return False 
			elif column == self.__class__.QUANTITY:
				try:
					value = int(value)
				except: return False 
				else:
					line.quantity = value 
					return True 
			elif column == self.__class__.TAX:
				try:
					value = int(value)
					if value not in (0, 4, 10, 21):
						return False 
				except:return False 
				else:
					line.tax = value
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
		if not index.isValid(): return 
		if self.editable_column(index.column()):
			return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
		else:
			return Qt.ItemFlags(~Qt.ItemIsEditable)

	def is_stock_relevant(self, line):
		return line.item_id or line.description in utils.descriptions

	@property
	def tax(self):
		return round(sum([line.quantity * line.price * line.tax / 100 for line in self.lines]), 2)
	
	@property
	def subtotal(self):
		return round(sum(line.quantity * line.price for line in self.lines), 2)
	
	@property
	def total(self):
		return self.tax + self.subtotal
	
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

		if not self.line_exists(line):
			self.lines.append(line) 
			self.layoutChanged.emit()
		else:
			raise ValueError("I can't process duplicate lines") 

	def line_exists(self, new_line):
		# First check not stock relevant lines:
		description = new_line.description
		if description not in utils.descriptions and \
			new_line.item_id is None:
				return description in \
					[line.description for line in self.lines]

		for line in self.lines:
			if all((
				new_line.condition == line.condition, 
				new_line.item_id == line.item_id, 
				new_line.description == line.description, 
				new_line.spec == line.spec 
			)):
				return True 
		return False


	def delete(self, indexes):
		rows = { index.row() for index in indexes}
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
				del self.lines[row] # Should not rise Index Error
				deleted = True 		
		if deleted:
			self.layoutChanged.emit() 

	def save(self, proforma):
		if not self.lines:return
		for line in self.lines:
			line.proforma = proforma 
			db.session.add(line) 
		try:
			db.session.commit() 
		except:
			db.session.rollback() 
			raise 
	
	def __bool__(self):
		return bool(len(self.lines))

class PaymentModel(BaseTable, QtCore.QAbstractTableModel):

	DATE, AMOUNT, NOTE = 0, 1, 2

	def __init__(self, proforma, sale, form):
		super().__init__()
		self.proforma = proforma 
		self._headerData = ['Date', 'Amount', 'Info']
		self.name = 'payments'
		self.form = form
		if sale:
			self.Payment = db.SalePayment
		else:
			self.Payment = db.PurchasePayment

		self.payments = db.session.query(self.Payment).\
			where(self.Payment.proforma.has(id=proforma.id)).all() 

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return 
		payment = self.payments[index.row()]
		column = index.column() 

		if role == Qt.DisplayRole:
			if column == self.__class__.DATE:
				return payment.date.strftime('%d/%m/%Y')
			elif column == self.__class__.AMOUNT:
				return str(payment.amount) 
			elif column == self.__class__.NOTE:
				return payment.note
		elif role == Qt.DecorationRole:
			if column == self.__class__.DATE:
				return QtGui.QIcon(':\calendar') 
		else:
			return            

	def setData(self, index, value, role = Qt.EditRole):
		if not index.isValid(): return False
		row, column = index.row(), index.column()
		payment = self.payments[row]
		if role == Qt.EditRole:
			if column == self.__class__.DATE:
				try:
					d = utils.parse_date(value)
					payment.date = d
					return True 
				except ValueError:
					return False
			elif column == self.__class__.AMOUNT:
				try:
					v = float(value.replace(',', '.'))
					payment.amount = v
					self.form.updateOwing() 
					return True 
				except ValueError:
					return False
			elif column == self.__class__.NOTE:
				payment.note = value[0:255]
				return True 
		return False

	def flags(self, index):
		if not index.isValid():
			return Qt.ItemIsEnabled
		return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)	

	def add(self, date, amount, note):
		payment = self.Payment(date, amount, note, self.proforma)
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
			self.__class__.DATE:'date', 
			self.__class__.AMOUNT:'amount', 
			self.__class__.NOTE:'note'
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

	def __init__(self,  proforma, sale):
		super().__init__() 
		self.proforma = proforma
		self._headerData = ['Date', 'Amount', 'Info']
		self.name = 'expenses'
		if sale:
			self.Expense = db.SaleExpense
		else:
			self.Expense = db.PurchaseExpense

		self.expenses = db.session.query(self.Expense).\
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


	def setData(self, index, value, role = Qt.EditRole):
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
			self.__class__.DATE:'date', 
			self.__class__.AMOUNT:'amount', 
			self.__class__.NOTE:'note'
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

class SerieModel(QtCore.QAbstractListModel):

	def __init__(self, line, expedition):
		super().__init__() 
		self.expedition = expedition
		self.series = db.session.query(db.ExpeditionSerie).join(db.ExpeditionLine).\
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

	ID, WAREHOUSE, TOTAL, PROCESSED, LOGISTIC ,CANCELLED, PARTNER,\
		AGENT, WARNING, FROM_PROFORMA = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Expedition ID', 'Warehouse', 'Total', 'Processed', 
		'Logistic','Cancelled', 'Partner', 'Agent', 'Warning', 'From Proforma']
		self.name = 'expeditions' 
		query = db.session.query(db.Expedition).\
			select_from(
				db.SaleProforma, 
				db.Partner, db.Agent, 
				db.Warehouse).\
				where(
					db.Agent.id == db.SaleProforma.agent_id, 
					db.Partner.id == db.SaleProforma.partner_id, 
					db.Expedition.proforma_id == db.SaleProforma.id, 
					db.Warehouse.id == db.SaleProforma.warehouse_id
				)
		
		
		if search_key:
			clause = or_(
				db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
					db.Warehouse.description.contains(search_key)) 
			query = query.where(clause) 

		if filters:
			self.expeditions = query.all() 

			if filters['logistic']:
				if 'empty' in filters['logistic']:
					self.expeditions = filter(lambda e:empty(e), self.expeditions)
				if 'overflowed' in filters['logistic']:
					self.expeditions = filter(lambda e:overflowed(e), self.expeditions)
				if 'partially_processed' in filters['logistic']:
					self.expeditions = filter(lambda e:partially_processed(e), self.expeditions)
				if 'completed' in filters['logistic']:
					self.expeditions = filter(lambda e:completed(e), self.expeditions)
			if filters['cancelled']:
				if 'cancelled' in filters['cancelled']:
					self.expeditions = filter(lambda e:e.proforma.cancelled, self.expeditions)
				if 'notcancelled' in filters['cancelled']:
					self.expeditions = filter(lambda e:not e.proforma.cancelled, self.expeditions)

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
			if column == ExpeditionModel.ID:
				return str(expedition.id).zfill(6)
			elif column == ExpeditionModel.WAREHOUSE:
				return expedition.proforma.warehouse.description 
			elif column == ExpeditionModel.TOTAL:
				return str(total_quantity(expedition))
			elif column == ExpeditionModel.PARTNER:
				return expedition.proforma.partner.fiscal_name
			elif column == ExpeditionModel.PROCESSED:
				return str(total_processed(expedition)) 
			elif column == ExpeditionModel.LOGISTIC:
				if empty(expedition):
					return 'Empty'
				elif overflowed(expedition):
					return 'Overflowed'
				elif partially_processed(expedition):
					return 'Partially Prepared'
				elif completed(expedition):
					return 'Completed'
			elif column == ExpeditionModel.CANCELLED:
				return 'Yes' if expedition.proforma.cancelled else 'No'
			elif column == ExpeditionModel.AGENT:
				return expedition.proforma.agent.fiscal_name 
			elif column == ExpeditionModel.WARNING:
				return expedition.note 
			elif column == ExpeditionModel.FROM_PROFORMA:
				return str(expedition.proforma.type) + '-' + str(expedition.proforma.number).zfill(6)

		elif role == Qt.DecorationRole:
			if column == ExpeditionModel.AGENT:
				return QtGui.QIcon(':\\agents')
			elif column == ExpeditionModel.PARTNER:
				return QtGui.QIcon(':\partners')
			elif column == ExpeditionModel.LOGISTIC:
				if empty(expedition):
					return QtGui.QColor(YELLOW)
				elif overflowed(expedition):
					return QtGui.QColor(RED)
				elif partially_processed(expedition):
					return QtGui.QColor(ORANGE)
				elif completed(expedition):
					return QtGui.QColor(GREEN) 
			elif column == ExpeditionModel.CANCELLED:
				return QtGui.QColor(RED) if expedition.proforma.cancelled \
					else QtGui.QColor(GREEN)
				
class ReceptionModel(BaseTable, QtCore.QAbstractTableModel):

	ID, WAREHOUSE, TOTAL, PROCESSED, LOGISTIC, CANCELLED, PARTNER,\
		AGENT, WARNING, FROM_PROFORMA =0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Reception ID', 'Warehouse', 'Total', 'Processed', 'Logistic', 'Cancelled', \
			'Partner', 'Agent', 'Warning', 'From Proforma']
		self.name = 'receptions' 
		query = db.session.query(db.Reception).\
			select_from(
				db.PurchaseProforma,
				db.Partner, db.Agent, 
				db.Warehouse).\
				where(
					db.Agent.id == db.PurchaseProforma.agent_id, 
					db.Partner.id == db.PurchaseProforma.partner_id, 
					db.Reception.proforma_id == db.PurchaseProforma.id, 
					db.Warehouse.id == db.PurchaseProforma.warehouse_id
				)

		if search_key:
			clause = or_(
				db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
					db.Warehouse.description.contains(search_key)) 
			query = query.where(clause) 

		if filters:
			self.receptions = query.all() 
			if filters['logistic']:
				if 'empty' in filters['logistic']:
					self.receptions = filter(lambda r :empty(r), self.receptions)
				if 'overflowed' in filters['logistic']:
					self.receptions = filter(lambda r:overflowed(r), self.receptions)
				if 'partially_processed' in filters['logistic']:
					self.receptions = filter(lambda r:partially_processed(r), self.receptions)
				if "completed" in filters['logistic']:
					self.receptions = filter(lambda r:completed(r), self.receptions) 
		
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
		reception= self.receptions[index.row()]
		column = index.column() 

		if role == Qt.DisplayRole: 
			if column == ReceptionModel.ID:
				return str(reception.id).zfill(6)
			elif column == ReceptionModel.WAREHOUSE:
				return reception.proforma.warehouse.description 
			elif column == ReceptionModel.TOTAL:
				return str(total_quantity(reception))
			elif column == ReceptionModel.PARTNER:
				return reception.proforma.partner.fiscal_name
			elif column == ReceptionModel.PROCESSED:
				return str(total_processed(reception)) 
			elif column == ReceptionModel.LOGISTIC:
				if empty(reception):
					return "Empty"
				elif overflowed(reception):
					return 'Overflowed'
				elif partially_processed(reception):
					return 'Partially Received'
				elif completed(reception):
					return "Completed"
			elif column == ReceptionModel.CANCELLED:
				return "Yes" if reception.proforma.cancelled else "No"
			elif column == ReceptionModel.AGENT:
				return reception.proforma.agent.fiscal_name 
			elif column == ReceptionModel.WARNING:
				return reception.note 
			elif column == ReceptionModel.FROM_PROFORMA:
				return str(reception.proforma.type) + '-' + str(reception.proforma.number).zfill(6)

		elif role == Qt.DecorationRole:
			if column == ReceptionModel.AGENT:
				return QtGui.QIcon(':\\agents')
			elif column == ReceptionModel.PARTNER:
				return QtGui.QIcon(':\partners')
			elif column == ReceptionModel.LOGISTIC:
				if empty(reception):
					return QtGui.QColor(YELLOW)
				elif overflowed(reception):
					return QtGui.QColor(RED)
				elif partially_processed(reception):
					return QtGui.QColor(ORANGE)
				elif completed(reception):
					return QtGui.QColor(GREEN) 
			elif column == ReceptionModel.CANCELLED:
				return QtGui.QColor(RED) if reception.proforma.cancelled \
					else QtGui.QColor(GREEN)

from db import Warehouse, Item
from db import session, func
from db import SaleProforma as sp
from db import SaleProformaLine as sl 
from db import ExpeditionLine as el 
from db import ExpeditionSerie as es 
from db import Expedition as e  
	
import operator, functools

class StockEntry:

	def __init__(self, item_id, condition, spec, quantity):
		self._item_id = item_id
		self._spec = spec
		self._condition = condition
		self._quantity = int(quantity)
		self._request = 0 

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
		return (i for i in (self.item_id, self.spec, \
			self.condition, self.quantity, self.request))

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
		hashes = (hash(x) for x in (self._item_id, self._spec, self._condition))
		return functools.reduce(operator.xor, hashes, 0)

class StockModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SPEC, QUANTITY, REQUEST = \
		0, 1, 2, 3, 4 

	def __init__(self, warehouse_id, description, condition, spec, 
			added_lines=None, deleted_lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Spec', \
			'Quantity avail. ', 'Requested quant.']
		self.name = 'stocks'
		self.stocks = self.computeStock(
			warehouse_id,
			description,
			condition,
			spec,
			added_lines = added_lines, 
			deleted_lines = deleted_lines
		) 

	def computeStock(self, warehouse_id, description, condition, spec, 
			added_lines	=None, deleted_lines=None):
		session = db.Session()
		
		item_id = utils.description_id_map.get(description)
		query = session.query(
			db.Imei.item_id, db.Imei.condition, 
			db.Imei.spec, func.count(db.Imei.imei).label('quantity')
		).where(
			db.Warehouse.id == warehouse_id, 
			db.Warehouse.id == db.Imei.warehouse_id, 
			
		).group_by(
			db.Imei.item_id, db.Imei.condition, db.Imei.spec
		)

		if item_id:
			query = query.where(db.Imei.item_id == item_id)
		
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
			db.Warehouse.id == db.ImeiMask.warehouse_id , 
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
		).select_from(
			db.SaleProforma,
			db.SaleProformaLine,
			db.Warehouse
		).where(
			db.SaleProformaLine.proforma_id == db.SaleProforma.id, 
			db.SaleProforma.warehouse_id == db.Warehouse.id, 
			db.Warehouse.id == warehouse_id,
			db.SaleProforma.cancelled == False, 
		).group_by(
			db.SaleProformaLine.item_id, 
			db.SaleProformaLine.condition, 
			db.SaleProformaLine.spec, 
		) 

		if item_id:
			query = query.where(db.SaleProformaLine.item_id == item_id)
		
		if condition:
			query = query.where(
				db.SaleProformaLine.condition == condition
			)
		
		if spec:
			query = query.where(
				db.SaleProformaLine.spec == spec 
			)

		sales = {StockEntry(r.item_id, r.condition, r.spec, r.quantity) for r in query}

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

		stocks = self.resolve(imeis, imeis_mask, sales, outputs) 
		
		if added_lines:
			for line in added_lines:
				for stock in stocks:
					if stock == line:
						stock -= line 
		
		if deleted_lines:
			for line in deleted_lines:
				for stock in stocks:
					if stock == line:
						stock += line 


		del session 

		return list(filter(lambda stock:stock.quantity > 0, stocks))

	def lines_against_stock(self, warehouse_id, lines):
		stocks = self.computeStock(
			warehouse_id, 
			description = None, condition=None, spec=None, 
			added_lines = None, deleted_lines = None
		)
		return any((
			line.quantity > stock.quantity 
			and line == stock
			for line in lines
			for stock in stocks
		))
		
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

	def check_before_saving(self):
		pass 

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
			return
		if index.column() == 4:
			return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
		else:
			return Qt.ItemFlags(~Qt.ItemIsEditable)

	@property
	def requested_stocks(self):
		return list(filter(lambda s:s.request > 0, self.stocks))


class ManualStockModel(StockModel):

	DESCRIPTION, CONDITION, SPEC, AVAILABLE, REQUEST = 0, 1, 2, 3, 4 

	def __init__(self, warehouse, mixed_description, condition, spec, lines=None):
		super(QtCore.QAbstractTableModel, self).__init__() 
		self._headerData = ['Description', 'Condition', 'Spec', \
			'Available', 'Request']
		self.name = 'stocks'
		stocks = super().computeStock(warehouse, mixed_description=mixed_description, \
			condition=condition, spec=spec, lines=lines) 
		
		self.stocks = {}
		for i, stock in enumerate(stocks):
			self.stocks[i] = StockEntryRequest(stock, 0)

	def computeStock(self, warehouse, *, mixed_description, condition, spec, lines=None):
		return super().computeStock(warehouse, condition, spec, \
			lines, mixed_description=mixed_description)

	def flags(self, index):
		if not index.isValid():
			return
		if index.column() == 4:
			return Qt.ItemFlags(super().flags(index) | Qt.ItemIsEditable)
		else:
			return Qt.ItemFlags(~Qt.ItemIsEditable)


	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row, column = index.row(), index.column() 
		stock, request_qnt = self.stocks[row]

		if role == Qt.DisplayRole:
			if column == ManualStockModel.DESCRIPTION:
				return stock.item
			elif column == ManualStockModel.CONDITION:
				return stock.condition
			elif column == ManualStockModel.SPEC:
				return stock.spec
			elif column == ManualStockModel.AVAILABLE:
				return str(stock.quantity)
			elif column == ManualStockModel.REQUEST:
				return str(request_qnt) 

	def setData(self, index, value, role=Qt.EditRole):
		if not index.isValid():
			return
		try:
			value = int(value)
		except ValueError:
			return False 
		else:
			row, column = index.row(), index.column() 
			available_qnt = self.stocks[row].stock_entry.quantity
			if value < 0:
				return False
			elif value > available_qnt:
				return False 
			stock_entry = self.stocks[row].stock_entry
			if column == ManualStockModel.REQUEST:
				self.stocks[row] = StockEntryRequest(stock_entry, value)
				self.dataChanged.emit(index, index) 
				return True
			return False
	

	def __len__(self):
		return len(self.stocks)


from db import PurchaseProforma as pp
from db import PurchaseProformaLine as pl 
from db import Reception as r 
from db import ReceptionLine as rl 
from db import ReceptionSerie as rs 

# class IncomingStockModel(BaseTable, QtCore.QAbstractTableModel):

# 	def __init__(self, warehouse, *, item, condition, spec, lines=None):
# 		super().__init__() 
# 		self._headerData = ['Description', 'Condition', 'spec', 'ETA', 'quantity']
# 		self.name = 'stocks'
# 		self.stocks = self.computeStock(warehouse, item, condition, spec, lines) 

# 	def computeStock(self, warehouse, item, condition, spec, lines):
# 		# Logic:
# 		# not_arrived_yet = asked - processed 
# 		# incoming = not_arrived_yet + total purchase with no warehouse order
# 		# Remember the special case:
# 		#   if not incoming_stock:
# 		#       incoming_stock = stock_not_arrived_yet
# 		#   else:
# 		#       iterate incoming, iterate asked - processed, add up 

# 		session = db.Session() 


# 		proformas = {r[0] for r in session.query(pp.id)}
# 		orders = {r[0] for r in session.query(po.proforma_id)}

# 		relevant = proformas.difference(orders)

# 		processed_query = session.query(Item, pol.condition, pol.spec, pp.eta, func.count(ps.serie).label('processed')).\
# 			select_from(pp, pol, po, Warehouse, Item, ps).where(pp.id == po.proforma_id).where(pol.order_id == po.id).\
# 				where(Item.id == pol.item_id).where(ps.line_id == pol.id).where(Warehouse.id == pp.warehouse_id).\
# 					group_by(Item.id, pp.eta, pol.condition, pol.spec).\
# 						where(Warehouse.description == warehouse).where(pp.cancelled == False)

# 		# Result: <db.Item object at 0x00000192B77C2610>, 'NEW', 'EEUU', datetime.date(2020, 10, 16), 10)
# 		# r.Keys():MKeyView(['Item', 'condition', 'spec', 'eta'])

# 		asked_query = session.query(Item, pl.condition, pl.spec, pp.eta, func.sum(pl.quantity).label('quantity')).\
# 			select_from(pp, pl, Warehouse, Item, po).where(pp.id == pl.proforma_id).where(pp.warehouse_id == Warehouse.id).\
# 				where(pl.item_id == Item.id).where(Warehouse.description == warehouse).where(pp.cancelled == False).\
# 					where(po.proforma_id == pp.id).\
# 					group_by(pp.eta, pl.condition, pl.spec, Item.id)


# 		incoming_query = session.query(Item, pp.eta, pl.condition, pl.spec, func.sum(pl.quantity).label('incoming')).\
# 			select_from(Item, Warehouse, pp, pl).where(pp.id == pl.proforma_id).where(Warehouse.id == pp.warehouse_id).\
# 				where(pl.item_id == Item.id).where(pp.cancelled == False).where(pp.id.in_(relevant)).\
# 					where(Warehouse.description == warehouse).\
# 					group_by(pp.eta, pl.condition, pl.spec, Item.id)


# 		sales_query = session.query(Item, sl.eta, sl.condition, sl.spec, func.sum(sl.quantity).label('outgoing')).\
# 			select_from(Item, Warehouse, sp, sl).where(sp.warehouse_id == Warehouse.id).where(Item.id == sl.item_id).\
# 				where(sp.id == sl.proforma_id).where(sp.cancelled == False).where(sp.normal == False).\
# 					where(Warehouse.description == warehouse).\
# 					group_by(sl.eta, sl.condition, sl.spec, Item.id)

# 		if item:
# 			asked_query = asked_query.where(Item.id == item.id)
# 			processed_query = processed_query.where(Item.id == item.id)
# 			incoming_query = incoming_query.where(Item.id == item.id)
# 			sales_query = sales_query.where(Item.id == item.id)
# 		if condition:
# 			asked_query = asked_query.where(pl.condition == condition)
# 			processed_query = processed_query.where(pol.condition == condition)
# 			incoming_query = incoming_query.where(pl.condition == condition)
# 			sales_query = sales_query.where(sl.condition == condition)
# 		if spec:
# 			asked_query = asked_query.where(pl.spec == spec)
# 			processed_query = processed_query.where(pol.spec == spec) 
# 			incoming_query = incoming_query.where(pl.spec == spec)
# 			sales_query = sales_query.where(sl.spec == spec)

# 		processed = {IncomingStockEntry(e.Item, e.spec, e.condition, e.processed, e.eta) for e \
# 			in processed_query}

# 		asked = {IncomingStockEntry(e.Item, e.spec, e.condition, e.quantity, e.eta) for e \
# 			in asked_query}

# 		incomings = { IncomingStockEntry(e.Item, e.spec, e.condition, e.incoming, e.eta) for e \
# 			in incoming_query}

		
# 		sales = { IncomingStockEntry(e.Item, e.spec, e.condition, e.outgoing, e.eta) for e \
# 			in sales_query}

# 		for a in asked:
# 			for p in processed:
# 				if a == p:
# 					a.quantity -= p.quantity
# 					break 

# 		not_arrived_yet = asked 
		
# 		if not incomings:
# 			incomings = not_arrived_yet
# 		else:
# 			for i in incomings:
# 				for n in not_arrived_yet:
# 					if i == n:
# 						i.quantity += n.quantity
# 						break 
		
# 		if sales:
# 			for sale in sales:
# 				for incoming in incomings:
# 					if sale == incoming:
# 						incoming.quantity -= sale.quantity
# 						break 
# 			lost_sales = sales.difference(incomings)
# 			for sale in lost_sales:
# 				sale.quantity = (-1) * sale.quantity

# 		if lines:
# 			for line in lines:
# 				for incoming in incomings:
# 					if str(line.item) == incoming.item and line.condition == incoming.condition and \
# 						line.spec == incoming.spec and line.eta == incoming.eta:
# 							incoming.quantity -= line.quantity
# 							break 

# 		incomings = list(filter(lambda o : o.quantity != 0, incomings))

# 		if sales:
# 			incomings += list(lost_sales)

# 		return incomings
	
# 	def checkAgainstLinesBeforeSaving(self):
# 		pass 

# 	def data(self, index, role=Qt.DisplayRole):
# 		if not index.isValid():
# 			return
# 		row, column = index.row(), index.column()
# 		entry = self.stocks[row]
# 		if role == Qt.DisplayRole:
# 			if column == 0:
# 				return entry.item
# 			elif column == 1:
# 				return entry.condition
# 			elif column == 2:
# 				return entry.spec
# 			elif column == 3:
# 				return entry.eta.strftime('%d/%m/%Y')
# 			elif column == 4:
# 				return str(entry.quantity) + ' pcs'
# 		elif role == Qt.DecorationRole:
# 			if column == 3:
# 				return QtGui.QIcon(':\calendar')


from sqlalchemy import inspect

def print_states(line):
	insp = inspect(line) 
	for state in [
		'transient',
		'pending', 
		'persistent', 
		'detached'
	]:
		print(state, ':', getattr(insp, state))

class IncomingVector:

	def __init__(self, line):
		self.origin_id = line.id 
		self.origin = line 
		self.type = line.proforma.type
		self.number = line.proforma.number 
		self.partner = line.proforma.partner.fiscal_name
		self.eta = line.proforma.eta.strftime('%d/%m/%Y')
		self.item_id = line.item_id
		self.spec = line.spec 
		self.condition = line.condition
		
		if line.description:
			self.description = line.description
		else:
			self.description = utils.description_id_map.inverse[line.item_id]

		quantity = line.quantity
		
		# Esto lo hago porque contaba los objetos que han sido
		# borrados, quedando fuera de la base de datos
		# y fuera de la session, lo que significa 
		# transient= True
		asked = sum(
			line.quantity for line in line.advanced_lines 
			if inspect(line).transient != True)

		processed = self.compute_processed(line) 

		if asked == quantity and quantity < processed:
			self.available = 0
		elif asked < quantity < processed:
			self.available = 0
		elif asked < processed < quantity:
			self.available = quantity - processed
		elif processed < asked < quantity:
			self.available = quantity - asked
		elif processed < quantity and quantity == asked:
			self.available = 0 
		elif asked == processed == 0:
			self.available = quantity


	def compute_processed(self, line):
		line_alias = line 
		try:
			for line in line.proforma.reception.lines:
				if line_alias == line:
					return sum(1 for serie in line.series)

		except AttributeError as ex:
			return 0 


	def __eq__(self, other):
		return all((
			self.origin_id == other.origin_id, 
			self.type == other.type, 
			self.number == other.number
		))

	def __hash__(self):
		hashes = (hash(x) for x in (
			self.origin_id, self.type, self.number
		))
		return functools.reduce(operator.xor, hashes, 0)

	def __iter__(self):
		return iter(self.__dict__.values())

	def __repr__(self):
		return repr(self.__dict__)


class IncomingStockModel(BaseTable, QtCore.QAbstractTableModel):

	DOCUMENT, PARTNER, ETA, DESC, CONDITION, SPEC, AVAILABLE =\
		0, 1, 2, 3, 4, 5, 6

	def __init__(self, warehouse, *, description, condition, spec, \
		added_lines=None, deleted_lines=None):
		super().__init__() 
		self._headerData = ['Document', 'Partner', 'Eta', 'Description', 'Condition', 'Spec.', 'Available']
		self.name = 'stocks'
		self.stocks = self.computeIncomingStock(
			warehouse,
			description=description, 
			condition = condition, 
			spec = spec
		) 

	def computeIncomingStock(self, warehouse_id, *, description,  \
		condition, spec, added_lines=None, deleted_lines=None):

		query = session.query(db.PurchaseProformaLine).\
			join(db.PurchaseProforma).join(db.Partner).outerjoin(db.Reception).\
				join(db.Warehouse).where(db.Warehouse.id == warehouse_id)
		
		item_id = utils.description_id_map.get(description) 

		if item_id:
			query = query.where(db.PurchaseProformaLine.item_id == item_id)
		
		if condition:
			query = query.where(db.PurchaseProformaLine.condition == condition)

		if spec:
			query = query.where(db.PurchaseProformaLine.spec == spec)


		stocks =  [IncomingVector(line) for line in query.all()]

		if added_lines:
			for line in added_lines:
				for stock in stocks:
					if line == stock:
						stock.available -= line.quantity

		if deleted_lines:
			for line in deleted_lines:
				for stock in stocks:
					if line == stock:
						stock.available += line.quantity 
		
		return list(filter(lambda s:s.available != 0, stocks))

	def lines_against_stock(self, warehouse_id, lines):
		print('lines against stock')
		return False 

	def data(self, index, role = Qt.DisplayRole):
		if not index.isValid(): return 

		row, col = index.row(), index.column() 

		if role == Qt.DisplayRole:
			vector = self.stocks[row]
			if col == self.__class__.DOCUMENT:
				return str(vector.type) + '-' + str(vector.number).zfill(6) 
			elif col == self.__class__.PARTNER:
				return vector.partner
			elif col == self.__class__.ETA:
				return vector.eta 
			elif col == self.__class__.DESC:
				return vector.description
			elif col == self.__class__.CONDITION:
				return vector.condition
			elif col == self.__class__.SPEC:
				return vector.spec 
			elif col == self.__class__.AVAILABLE:
				return str(vector.available)

	def reset(self):
		self.stocks = []
		self.layoutChanged.emit() 

	def __getitem__(self, index):
		return self.stocks[index]

def copy_advanced_line(line):
	l = db.AdvancedLine()
	l.origin_id = line.origin_id
	l.type = line.type
	l.number = line.number
	l.quantity = line.quantity
	return l 

class AdvancedLinesModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SHOWING_CONDITION, SPEC, IGNORING_SPEC, \
		QUANTITY, PRICE, SUBTOTAL, TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, proforma):
		super().__init__()
		self._headerData = ['Description', 'Condition', 'Showing Condt.', 'Spec', \
			'Ignoring Spec?','Qty.', 'Price', 'Subtotal', 'Tax', 'Total']
		self.name = 'lines'
		self._lines = proforma.advanced_lines 
		self.initial_lines = [copy_advanced_line(line) for line in self._lines]
		

	
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid(): return
		row, col = index.row(), index.column()
		if role == Qt.DisplayRole:
			line = self._lines[row]
			if col == self.__class__.DESCRIPTION:
				try:
					description = line.origin.description
				except AttributeError:
					description = line.description
			
				if description is None:
					description = utils.description_id_map.inverse[line.origin.item_id]
				return description
			elif col == self.__class__.CONDITION:
				try:
					return line.origin.condition
				except AttributeError:
					return '' 
			elif col == self.__class__.SHOWING_CONDITION:
				return line.showing_condition or '' 
			elif col == self.__class__.SPEC:
				try:
					return line.origin.spec 
				except AttributeError:
					return '' 
			elif col == self.__class__.IGNORING_SPEC:
				return 'Yes' if line.ignore_spec else 'No'
			elif col == self.__class__.QUANTITY:
				return str(line.quantity)
			elif col == self.__class__.PRICE:
				return str(line.price)
			elif col == self.__class__.TAX:
				return str(line.tax)
			elif col == self.__class__.SUBTOTAL:
				return str(round(line.price * line.quantity)) 
			elif col == self.__class__.TOTAL:
				total = round((line.quantity * line.price) * (1 + line.tax/100), 2)
				return str(total) 

	def add(self, quantity, price, ignore, tax, showing_condition, origin, type, number):

		for line in self._lines:
			if line.origin == origin:
				raise ValueError('I cannot handle duplicate stocks')		

		line = db.AdvancedLine() 
		line.quantity = quantity
		line.price = price
		line.ignore_spec = ignore
		line.tax = tax 
		line.showing_condition = showing_condition 
		line.origin = origin
		line.origin_id = origin.id
		line.type = type
		line.number = number

		self._lines.append(line)
		self.layoutChanged.emit() 

	def delete(self, rows):
		for row in sorted(rows, reverse=True):
			line = self._lines[row]
			db.session.expunge(line)
			del self._lines[row]

		# db.session.commit() 	
		self.layoutChanged.emit() 

	def reset(self):
		for line in self._lines:
			db.session.expunge(line)
		self.layoutChanged.emit() 

	def insert_free(self, description, quantity, price, tax):
		
		line = db.AdvancedLine() 
		line.description = description
		line.quantity = quantity
		line.price = price
		line.tax = tax 
		line.ignore_spec = True 


		self._lines.append(line) 
		self.layoutChanged.emit() 

	def deleted_lines(self):
		return set(self.initial_lines).difference(set(self._lines))

	def added_lines(self):
		return set(self._lines).difference(set(self.initial_lines))


	@property
	def lines(self):
		return self._lines 

	@property
	def tax(self):
		return sum(
			line.quantity * line.price * line.tax /100
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

	

class InventoryModel(BaseTable, QtCore.QAbstractTableModel):
	
	def __init__(self):
		super().__init__()
		self._headerData = ['Serie', 'Description', 'Condition', 'spec', 'Warehouse']
		self.name = 'series'
		self.series = db.session.query(db.Imei).join(Item).join(Warehouse).all() 
	
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row, column = index.row(), index.column() 
		entry = self.series[row]
		if role == Qt.DisplayRole:
			if column == 0:
				return entry.imei 
			elif column == 1:
				return str(entry.item) 
			elif column == 2:
				return entry.condition
			elif column == 3:
				return entry.spec
			elif column == 4:
				return entry.warehouse.description





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
		self.conditions = [ c for c in db.session.query(db.Condition)]
	
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
		except:return 
		else:
			if condition == 'Mix':return 
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
	
class SpecListModel(QtCore.QAbstractListModel):

	def __init__(self):
		super().__init__()
		self.specs = [s for s in db.session.query(db.Spec)]
	
	def rowCount(self, index=QModelIndex()):
		return len(self.specs)
	
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():return
		if role == Qt.DisplayRole:
			return self.specs[index.row()].description
		
	def delete(self, row):
		try:
			spec = self.specs[row]
		except IndexError: return
		else:
			if spec == 'Mix':return 
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
		self.reception_series = db.session.query(db.ReceptionSerie).\
			join(db.ReceptionLine).join(db.Reception).\
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
		return len([
			o for o in self.reception_series if o.line_id == line.id
		])

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

from operator import attrgetter
Group = namedtuple('Group', 'description condition spec quantity')
class GroupModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SPEC, QUANTITY = 0, 1, 2, 3

	def __init__(self, rs_model, line):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Spec', \
			'Quantity']
		self.name = 'groups'
		key = attrgetter('item_id', 'condition', 'spec')

		series = rs_model.reception_series
		_filter = lambda o:o.line_id == line.id
		series = list(filter(_filter, series))
		series = sorted(series, key=key)
		from itertools import groupby
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
				self.__class__.DESCRIPTION:group.description, 
				self.__class__.CONDITION:group.condition,
				self.__class__.SPEC:group.spec, 
				self.__class__.QUANTITY:group.quantity 
			}.get(col)
