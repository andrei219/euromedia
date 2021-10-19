
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5 import QtGui

from sqlalchemy import inspect, or_ 
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select, func

import db 

import operator

from copy import deepcopy

from exceptions import DuplicateLine, SeriePresentError, LineCompletedError

from bidict import bidict

from utils import parse_date

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

def map(db_class):
	return {o.fiscal_name:o.id for o in db.session.query(db_class.fiscal_name, db_class.id).\
		where(db_class.active == True)}

def complete_descriptions(descriptions):

	d = set() 
	for ds in descriptions:
		manufacturer, category, model, *_ = ds.split(' ')
		d.add(' '.join([manufacturer, category, model, \
			'Mixed GB', 'Mixed Color']))
	for ds in descriptions:
		index = ds.index('GB') + 2 
		ds = ds[0:index] + ' Mixed Color'
		d.add(ds)
	
	for ds in descriptions:
		manufacturer, category, model, capacity, gb, color = ds.split(' ')
		d.add(' '.join([manufacturer, category, model, 'Mixed GB', color]))
	
	return d.union(descriptions)

description_id_map = bidict({str(item):item.id for item in db.session.query(db.Item)})
descriptions = complete_descriptions(description_id_map.keys())

specs = {s.description for s in db.session.query(db.Spec)}
conditions = {c.description for c in db.session.query(db.Condition)}


partner_id_map = map(db.Partner)
agent_id_map = map(db.Agent)

courier_id_map = {c.description:c.id for c in db.session.query(db.Courier)}
warehouse_id_map = {w.description:w.id for w in db.session.query(db.Warehouse)}


def refresh_maps():
	global descriptions, description_id_map, specs, \
		conditions, partner_id_map, agent_id_map, courier_id_map, warehouse_id_map
	
	description_id_map = bidict({str(item):item.id for item in db.session.query(db.Item)})
	descriptions = complete_descriptions(description_id_map.keys())

	specs = {s.description for s in db.session.query(db.Spec)}
	conditions = {c.description for c in db.session.query(db.Condition)}

	partner_id_map = map(db.Partner)
	agent_id_map = map(db.Agent)

	courier_id_map = {c.description:c.id for c in db.session.query(db.Courier)}
	warehouse_id_map = {w.description:w.id for w in db.session.query(db.Warehouse)}

	

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
	
	# Protect against None results from partners with no credits.
	if max_credit is None:
		max_credit = 0
	if total is None:
		total = 0
	if paid is None:
		paid = 0 

	return max_credit + paid - total


# Proformas utils::
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
	return sum([line.quantity for line in proforma.lines if \
		line.description in descriptions or line.item_id])

def total_processed(proforma):
	proforma = get_actual_object(proforma) 
	try:
		return len([1 for line in proforma.reception.lines \
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
	for line in proforma.reception.lines:
		try:
			if line.quantity < len(line.series):
				return True 
		except AttributeError:
			continue
	else:
		return False 

def not_paid(proforma):
	return total_paid(proforma) == 0

def partially_paid(proforma):
	return 0 < total_paid(proforma) < total_debt(proforma)

def fully_paid(proforma):
	return total_paid(proforma) == total_debt(proforma)

def overpaid(proforma):
	return total_paid(proforma) > total_debt(proforma) 


# Warehouse utils: 

# def w_total_quantity(reception):
# 	try:
# 		return total_quantity(reception.proforma) 
# 	except AttributeError:
# 		pass 

# def w_total_processed(reception):
# 	return total_processed(reception.proforma)  

# def w_empty(reception):
# 	return total_processed(reception.proforma) == 0

# def w_partially_processed(reception):
# 	return partially_processed(reception.proforma) 

# def w_completed(reception):
# 	return total_processed(reception.proforma) == total_quantity(reception.proforma) 

# def w_overflowed(reception):
# 	return overflowed(reception.proforma) 

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


class InvoiceModel(BaseTable, QtCore.QAbstractTableModel):
	 
	TYPE_NUM , DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL, \
		FROM_PROFORMA = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 
	
	def __init__(self, sale=False, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'Partner', 'Agent', 'Financial', \
			'Logistic', 'Shipment', 'Owing', 'Total', 'From Proforma']
		self.name = 'invoices'
		self.sale = sale 
		self.Proforma = db.PurchaseProforma    
		if sale:
			self.Proforma = db.SaleProforma
		
		self.invoices = db.session.query(self.Proforma).where(self.Proforma.invoice != None).all()         

	
	def total_debt(self, invoice):
		return sum([line.quantity * line.price for line in invoice.lines])
	
	def totaltotaltotaltotaltotaltotal_paid(self, invoice):
		return sum([payment.amount for payment in invoice.payments])

	def total_quantity(self, invoice):
		return sum([line.quantity for line in invoice.lines])

	def tota_processed(self, invoice):
		processed = 0
		try:
			lines = invoice.expedition.lines if self.sale else \
				invoice.reception.lines
			
			for line in lines:
				for serie in line.series:
					processed += 1
			return processed
		except AttributeError:
			return 0 

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return 
		
		row, col = index.row(), index.column()
		proforma = self.invoices[row]

		if col in (InvoiceModel.FINANCIAL, InvoiceModel.OWING, InvoiceModel.TOTAL):
			paid = sum([payment.amount for payment in proforma.payments])
			total_debt = sum([line.quantity * line.price for line in proforma.lines])
		elif col == InvoiceModel.LOGISTIC:
			total_quantity = self.total_quantity(proforma)
			processed = self.tota_processed(proforma)

		if role == Qt.DisplayRole:
			if col == InvoiceModel.TYPE_NUM:
				s = str(proforma.invoice.type) + '-' + str(proforma.invoice.number).zfill(6)
				return s 
			elif col == InvoiceModel.DATE:
				return proforma.date.strftime('%d/%m/%Y')
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
						return 'partially paid' 
					elif paid == total_debt:
						return 'Paid'
					elif paid > total_debt:
						if self.sale:
							return 'We Owe'
						else:
							return 'They owe'

			elif col == InvoiceModel.LOGISTIC:
				if processed_quantity == 0:
					return "Empty"
				elif 0 < processed_quantity < total_quantity:
					if self.sale:
						return 'Partially Prepared'
					else:
						return 'Partially Received'                
				elif processed_quantity == total_quantity:
					return 'completed'
			elif col == InvoiceModel.SENT:
				return "Sent" if proforma.sent else "Not Sent"
			elif col == InvoiceModel.OWING:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(total_debt - paid) + sign       
			elif col == InvoiceModel.TOTAL:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(total_debt) + sign
			elif col == InvoiceModel.FROM_PROFORMA:
				return str(proforma.type) + '-' + str(proforma.number).zfill(6)

		elif role == Qt.DecorationRole:
			if col == InvoiceModel.FINANCIAL:
				if proforma.cancelled:
					return QtGui.QIcon(':\cross')
				else:
					if total_debt == paid:
						return QtGui.QIcon(':\greentick')
					elif paid == 0 or (0 < paid < total_debt) or (paid > total_debt) :
						return QtGui.QIcon(':\cross')
			elif col == InvoiceModel.DATE:
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
	
	TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, CANCELLED, \
		OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

	def __init__(self, filters=None, search_key=None):  
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', \
			'Financial', 'Logistic', 'Sent', 'Cancelled','Owing', 'Total']
		self.name = 'proformas'
		query = db.session.query(db.PurchaseProforma).join(db.PurchasePayment).\
			join(db.PurchaseProformaLine).join(db.Reception) 

		if search_key:
			# Rememeber to check here
			# query = query.join(db.Partner).join(db.Agent)
			predicate = or_(db.Agent.fiscal_name.contains(search_key), \
				db.Partner.fiscal_name.contains(search_key)) 
			query = query.where(predicate)

		if filters:
			self.proformas = query.all() 

			if filters['types']:
				print(filters['types'])
				self.proformas = filter(lambda p : p.type in filters['types'], self.proformas)

			if filters['financial']:
				if 'notpaid' in filters['financial']:
					self.proformas = filter(lambda p: not_paid(p), self.proformas)
				if 'fullypaid' in filters['financial']:
					self.proformas = filter(lambda p:fully_paid(p), self.proformas)
				if 'partiallypaid' in filters['financial']:
					self.proformas = filter(lambda p:partially_paid(p) ,self.proformas)
			
			if filters['logistic']:
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:empty(p), self.proformas)
				if 'partially_processed' in filters['logistic']:
					self.proformas = filter(lambda p:partially_processed(p), self.proformas) 
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:completed(p), self.proformas)
				if 'overflowed' in filters['logistic']:
					self.proformas = filter(lambda p:overflowed(p), self.proformas)

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
				if not_paid(proforma):
					return "Not Paid"
				elif partially_paid(proforma):
					return "Partially Paid"
				elif fully_paid(proforma):
					return "Paid"
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
				elif partially_paid(proforma):
					return QtGui.QColor(ORANGE)
				elif fully_paid(proforma):
					return QtGui.QColor(GREEN)
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
					return QtGui.QColor(ORANGE)
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
				return QtGui.QColor(RED) if proforma.sent else\
					QtGui.QColor(GREEN)


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
			}.get(section) 
			
			if attr:
				self.layoutAboutToBeChanged.emit() 
				self.proformas.sort(key=operator.attrgetter(attr), reverse=reverse)
				self.layoutChanged.emit() 

	def add(self, proforma):
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
			proforma.tracking = Tracking
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
				descriptions:
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
			if line.item_id or line.description in descriptions:
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
	
	TYPE_NUM, DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'Partner','Agent', 'Financial', 'Logistic',\
			'Shipment', 'Owes', 'Total']
		self.proformas = [] 
		self.name = 'proformas'
		query = db.session.query(db.SaleProforma) 

		if search_key:
			query = query.join(db.Partner).join(db.Agent)
			predicate = or_(db.Agent.fiscal_name.contains(search_key),db.Partner.fiscal_name.contains(search_key)) 
			query = query.where(predicate)

		if filters:
			self.proformas = query.all() 

			if 'type' in filters:
				self.proformas = filter(lambda p : p.type in filters['type'], self.proformas)

			if 'financial' in filters:
				if 'not paid' in filters['financial']:
					self.proformas = filter(lambda p: not self.totaltotaltotaltotaltotal_paid(p), self.proformas)
				if 'cancelled' in filters['financial']:
					self.proformas = filter(lambda p:p.cancelled, self.proformas)
				if 'fully paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and self.totaltotaltotaltotaltotal_paid(p) == self.total_debt(p), self.proformas)
				if 'partially paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self.totaltotaltotaltotaltotal_paid(p) < self.total_debt(p) ,self.proformas)
			
			if 'logistic' in filters:
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and not self.total_processed(p), self.proformas)
				if 'partially prepared' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self.total_processed(p) < self.total_quantity(p),\
						self.proformas) 
				
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and self.total_processed(p) == self.total_quantity(p), \
						self.proformas)

			if 'shipment' in filters:
				if 'sent' in filters['shipment']:
					self.proformas = filter(lambda p:p.sent, self.proformas)
				if 'not sent' in filters['shipment']:
					self.proformas = filter(lambda p:not p.sent, self.proformas)

			if isinstance(self.proformas, filter):
				self.proformas = list(self.proformas) 

		else:
			self.proformas = query.all() 
	
	def total_debt(self, proforma):
		return sum([line.quantity * line.price for line in proforma.lines])
	
	def totaltotaltotaltotaltotal_paid(self, proforma):
		return sum([payment.amount for payment in proforma.payments])


	def total_quantity(self, proforma):
		return sum([line.quantity for line in proforma.lines])

	def tota_processed(self, proforma):
		processed = 0
		try:
			for line in proforma.expedition.lines:
				for serie in line.series:
					processed += 1
			return processed
		except AttributeError:
			return 0 

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return 
		row, col = index.row(), index.column()
		proforma = self.proformas[row]

		if col in (SaleProformaModel.FINANCIAL, SaleProformaModel.OWING, SaleProformaModel.TOTAL):
			paid = self.totaltotaltotaltotaltotaltotal_paid(proforma) 
			total_debt = self.total_debt(proforma) 
		elif col == SaleProformaModel.LOGISTIC:
			total_quantity = self.total_quantity(proforma) 
			try:
				processed_quantity = 0 
				for line in proforma.expedition.lines:
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
						return 'partially paid' 
					elif paid == total_debt:
						return 'Paid'
					elif paid > total_debt:
						return 'We Owe'

			elif col == SaleProformaModel.LOGISTIC:
				if processed_quantity == 0:
					return "Empty"
				elif 0 < processed_quantity < total_quantity:
					return "Partially Prepared"
				elif processed_quantity == total_quantity:
					return 'Fully Prepared'
			elif col == SaleProformaModel.SENT:
				return "Sent" if proforma.sent else "Not Sent"
			elif col == SaleProformaModel.OWING:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(round(total_debt - paid, 2)) + sign       
			elif col == SaleProformaModel.TOTAL:
				sign = ' -€' if proforma.eur_currency else ' $'
				return str(round(total_debt)) + sign

		elif role == Qt.DecorationRole:
			if col == SaleProformaModel.FINANCIAL:
				if proforma.cancelled:
					return QtGui.QIcon(':\cross')
				else:
					if total_debt == paid:
						return QtGui.QIcon(':\greentick')
					elif paid == 0 or (0 < paid < total_debt) or (paid > total_debt) :
						return QtGui.QIcon(':\cross')
			elif col == SaleProformaModel.DATE:
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
			db.session.add(db.ExpeditionLine(expedition, line.item, line.condition,\
				line.spec, line.quantity))    
		try:
			db.session.commit() 
		except:
			db.session.rollback() 
			raise

	
	def physicalStockAvailable(self, warehouse_id, lines):
		matches = 0 
		lines_number = len(lines)
		
		for line in lines:
			for stock in db.session.query(func.count(db.Imei.imei).label('quantity'), db.Imei.item_id, db.Imei.condition, \
				db.Imei.spec).join(Warehouse).where(Warehouse.id == warehouse_id).\
					group_by(db.Imei.item_id, db.Imei.spec, db.Imei.condition):
						if line.item_id == stock.item_id and line.condition == stock.condition and \
							line.spec == stock.spec:
								if line.quantity <= stock.quantity:
									matches += 1 
		return len(lines) == matches

class SaleProformaLineModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, SHOWING_CONDITION, SPEC, IGNORING_SPEC, \
		QUANTITY, PRICE, SUBTOTAL, TAX, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 


	# Need to change the data structure into a dict like:
	# {
	#   0: SaleProformaLine(···), 
	#   1: [
	#           SaleProformaLine(···), 
	#           SaleProformaLine(···), 
	#           SaleProformaLIne(···)
	#       ], 
	#   n : SaleProformaLine(···)
	# 
	# }
	# The data method will be more inteligent exposing 
	# simply the line like already does or 
	# building a mixed representation of the lines 
	# if the value in the dictionary is a list
	# simple type checking 


	def __init__(self):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Showing Condt.', 'Spec', \
			'Ignoring Spec?','Qty.', 'Price', 'Subtotal', 'Tax', 'Total']   
		self.name = '_lines'
		self._lines = {}

	
	@property
	def lines(self):
		lines = []
		for index in self._lines:
			if type(self._lines[index]) == db.SaleProformaLine:
				lines.append(self._lines[index])
			elif type(self._lines[index]) == list:
				lines.extend(self._lines[index])
		return lines

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return 
		row = index.row() 
		line = self._lines[row]
		col = index.column() 
		if role == Qt.DisplayRole:
			if type(line) == db.SaleProformaLine:
				return self._return_simple_line(line, col) 
			elif type(line) == list:
				return self._return_complex_line(line, col) 

	def _return_simple_line(self, line, col):
		total = round((line.quantity * line.price) * (1 + line.tax/100), 2)
		subtotal = round(line.quantity * line.price, 2)
		ignore_spec = 'Yes' if line.ignore_spec else 'No'
		showing_condition = line.showing_condition or line.condition
		return {
			SaleProformaLineModel.DESCRIPTION:str(line.item), 
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
		
	def _return_complex_line(self, lines, col):
		
		# Made item hashable
		# Now diff_descritons elements are Item objects
		diff_descriptions = {line.item for line in lines}
		diff_conditions = {line.condition for line in lines}
		diff_specs = {line.spec for line in lines}


		if len(diff_descriptions) == 1:
			description = str(diff_descriptions.pop())
		else:
			description = str(diff_descriptions.pop()).split('GB')[0] + 'Mixed Color'
		
		if len(diff_conditions) == 1:
			condition = diff_conditions.pop()
		else:
			condition = 'Mix'
		showing_condition = condition

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

	@property
	def tax(self):
		total_tax = 0
		for index in self._lines:
			line_s = self._lines[index]
			if isinstance(line_s, db.SaleProformaLine):
				total_tax += self._tax_from_line(line_s) 
			elif isinstance(line_s, list):
				total_tax += sum([self._tax_from_line(line) for line in line_s])
		return total_tax
		
	def _tax_from_line(self, line):
		return line.quantity * line.price * line.tax / 100
		
		# return sum([line.quantity * line.price * line.tax / 100 for line in self.lines])

	@property
	def subtotal(self):
		total = 0
		for index in self._lines:
			line_s = self._lines[index]
			if isinstance(line_s, db.SaleProformaLine):
				total += self._subtotal_from_line(line_s)
			elif isinstance(line_s, list):
				total += sum([self._subtotal_from_line(line) for line in line_s])
		return total

	def _subtotal_from_line(self, line):
		return line.price * line.quantity

	@property
	def total(self):
		return self.tax + self.subtotal

	def add(self, item, condition, spec, ignore, \
		quantity, price, tax, eta=None, showing_condition=None):
		line = db.SaleProformaLine(item, condition, spec, \
			ignore, price, quantity, tax, showing_condition, eta) 
		self._add_line(line) 
		self.layoutChanged.emit() 

	# sers are StockEntryRequest list 
	def add_bulk(self, sers:list, ignore, price, tax):
		next = self._get_next_row_number() 
		self._lines[next] = [
			db.SaleProformaLine.from_stock(ser, ignore, price, tax) 
			for ser in sers
		]
		self.layoutChanged.emit() 


	def _add_line(self, line):
		next = self._get_next_row_number() 
		self._lines[next] = line

	def _get_next_row_number(self):
		try:
			return max(self._lines) + 1
		except ValueError:
			return 0

	def delete(self, indexes):
		rows = { index.row() for index in indexes}
		aux_dict = {k:self._lines[k] for k in set(self._lines) - rows}        
		self._lines = {}
		for i, v in enumerate(aux_dict.values()):
			self._lines[i] = v 
		self.layoutChanged.emit() 

	def reset(self):
		self.layoutAboutToBeChanged.emit() 
		self._lines = {}
		self.layoutChanged.emit() 

	def save(self, proforma):
		last_group_number = self._get_last_group_number() 
		for index in self._lines:
			line_s = self._lines[index]
			if isinstance(line_s, db.SaleProformaLine):
				line_s.proforma = proforma
				db.session.add(line_s) 
			elif isinstance(line_s, list):
				for line in line_s:
					line.proforma = proforma
					line.mixed_group_id = last_group_number
					db.session.add(line) 
				last_group_number += 1 

		try:
			db.session.commit() 
		except:
			db.session.rollback()
			raise 	
	
	def _get_last_group_number(self):
		last_group_number = db.session.query(func.max(db.SaleProformaLine.mixed_group_id)).scalar()
		if last_group_number is None:
			last_group_number = 0 
		else:
			last_group_number += 1
		return last_group_number

	def last_row(self):
		return len(self._lines) - 1

	def actual_lines_from_mixed(self, index):
		try:
			l = self._lines[index]
		except KeyError:
			return 
		else:
			return l if type(l) == list else None 


class ActualLinesFromMixedModel(BaseTable, QtCore.QAbstractTableModel):

	DESCRIPTION, CONDITION, spec, REQUEST = 0, 1, 2, 3

	def __init__(self, lines):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'spec', 'Requested Quantity']
		self.name = 'lines'
		self.lines = lines 


	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row, column = index.row(), index.column() 
		line = self.lines[row]
		if role == Qt.DisplayRole:
			if column == ActualLinesFromMixedModel.DESCRIPTION:
				return str(line.item) # Item object
			elif column == ActualLinesFromMixedModel.CONDITION:
				return line.condition
			elif column == ActualLinesFromMixedModel.spec:
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

	def __init__(self, lines=None, delete_allowed=True):
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
					return description_id_map.inverse[line.item_id]
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
		# if not self.editable_column(column):return False
		line = self.lines[row]
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
		return line.item_id or line.description in descriptions

	@property
	def tax(self):
		return round(sum([line.quantity * line.price * line.tax / 100 for line in self.lines]), 2)
	
	@property
	def subtotal(self):
		return round(sum([line.quantity * line.price for line in self.lines]), 2)
	
	@property
	def total(self):
		return self.tax + self.subtotal
	
	def add(self, description, condition, spec, quantity, price, tax):
		line = db.PurchaseProformaLine() 
		try:
			line.item_id = description_id_map[description]
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
		if description not in descriptions and \
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

	def __init__(self, proforma, sale):
		super().__init__()
		self.proforma = proforma 
		self._headerData = ['Date', 'Amount', 'Info']
		self.name = 'payments'
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
					d = parse_date(value)
					payment.date = d
					return True 
				except ValueError:
					return False
			elif column == self.__class__.AMOUNT:
				try:
					v = float(value)
					payment.amount = v
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


	def save(self):
		try:
			db.session.commit()
		except:
			db.session.rollback()
			raise 

	@property
	def paid(self):
		return sum([p.amount for p in self.payments])

class ExpenseModel(BaseTable, QtCore.QAbstractTableModel):
	
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
		self.series = db.session.query(self.ExpeditionSerie).join(self.ExpeditionLine).\
			where(self.ExpeditionSerie.line_id == line.id).all()

		self.series_at_expedition_level  = {r[0] for r in db.session.query(self.ExpeditionSerie.serie)\
			.join(self.ExpeditionLine).join(self.Expedition).where(db.Expedition.id == expedition.id)}


		
	def add(self, line, _serie):

		if self._seriePresent(_serie):
			raise SeriePresentError 

		if line.quantity == len(self.series):
			raise LineCompletedError

		serie = self.Serie() 
		serie.serie = _serie
		serie.line = line 
		db.session.add(serie) 
		try:
			db.session.commit() 
			self.series.append(serie)
			self.series_at_expedition_level.add(_serie)
			self.layoutChanged.emit() 
		except:
			db.session.rollback() 
			raise 

	def delete(self, index):
		serie = self.series[index.row()]
		db.session.delete(serie) 
		try:
			db.session.commit() 
			del self.series[index.row()]
			self.series_at_expedition_level.remove(serie.serie)
			self.layoutChanged.emit() 
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

	def _seriePresent(self, serie):
		if serie in self.series_at_expedition_level:
			return True 
		else:
			return False

class ExpeditionModel(BaseTable, QtCore.QAbstractTableModel):

	ID, WAREHOUSE, TOTAL, PROCESSED, STATUS, PARTNER, AGENT, WARNING, FROM_PROFORMA =\
		0, 1, 2, 3, 4, 5, 6, 7, 8, 

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Expedition ID', 'Warehouse', 'Total', 'Processed', 'Status','Partner', 'Agent', \
			'Warning', 'From Proforma']
		self.name = 'expeditions' 
		query = db.session.query(db.Expedition).join(db.SaleProforma).\
			join(db.Agent).join(db.Partner).join(db.Warehouse) 
		if search_key:
			clause = or_(
				db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
					db.Warehouse.description.contains(search_key)) 
			query = query.where(clause) 

		if filters:
			self.expeditions = query.all() 
			if 'cancelled' in filters:
				self.expeditions = filter(lambda o:o.proforma.cancelled, self.expeditions)
			if 'partially processed' in filters:
				self.expeditions = filter(lambda o:not o.proforma.cancelled and 0 < self._processed(o) < self._total(o), self.expeditions)
			if 'empty' in filters:
				self.expeditions = filter(lambda o :not o.cancelled and not self._processed(o), self.expeditions)
			if 'completed' in filters:
				self.expeditions = filter(lambda o: not o.cancelled and self._processed(o) == self._tota(o), self.expeditions)

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
				return str(self._total(expedition))
			elif column == ExpeditionModel.PARTNER:
				return expedition.proforma.partner.fiscal_name
			elif column == ExpeditionModel.PROCESSED:
				return str(self._processed(expedition)) 
			elif column == ExpeditionModel.STATUS:
				total = self._total(expedition) 
				processed = self._processed(expedition) 
				if expedition.proforma.cancelled:
					return 'Cancelled'
				else:
					if total == processed:
						return 'Completed'
					elif 0 < processed < total:
						if self.sale:
							return 'Partially Prepared'
						else:
							return 'Partially Received'
					elif processed == 0:
						return 'Empty'
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
			elif column == ExpeditionModel.STATUS:
				if expedition.proforma.cancelled:
					return QtGui.QIcon(':\cancel')
				else:
					total = self._total(expedition) 
					processed = self._processed(expedition) 
					if total == processed:
						return QtGui.QIcon(':\greentick')
					elif 0 < processed < total:
						return QtGui.QIcon(':\cross')
					elif processed == 0:
						return QtGui.QIcon(':\cross')

	def _total(self, expedition):
		return sum([line.quantity for line in expedition.lines])  

	def _processed(self, expedition):
		processed = 0 
		try:
			for line in expedition.lines:
				for serie in line.series:
					processed += 1 
		except AttributeError: return 0 

class ReceptionModel(BaseTable, QtCore.QAbstractTableModel):

	ID, WAREHOUSE, TOTAL, PROCESSED, LOGISTIC, CANCELLED, PARTNER, AGENT, WARNING, FROM_PROFORMA =\
		0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Reception ID', 'Warehouse', 'Total', 'Processed', 'Logistic', 'Cancelled', \
			'Partner', 'Agent', 'Warning', 'From Proforma']
		self.name = 'receptions' 
		query = db.session.query(db.Reception)
		# .join(db.PurchaseProforma).join(db.Agent).\
			# join(db.Partner).join(db.Warehouse) 

		if search_key:
			clause = or_(
				db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
					db.Warehouse.description.contains(search_key)) 
			query = query.where(clause) 

		if filters:
			self.receptions = query.all() 
			if filters['logistic']:
				if 'reception_empty' in filters['logistic']:
					self.receptions = filter(lambda r :empty(r), self.receptions)
				elif 'reception_partially' in filters['reception']:
					self.receptions = filter(lambda r:partially_processed(r), self.receptions)
				if 'reception_completed' in filters:
					self.receptions = filter(lambda r:completed(r), self.receptions)
				if "reception_overflowed" in filters:
					self.receptions = filter(lambda r:overflowed(r), self.receptions) 
		
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
					return "Overflowed"
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
					return QtGui.QColor(ORANGE)
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

class ActualStockEntry:

	def __init__(self, item, spec, condition, quantity):
		self.item = str(item) 
		self.spec = spec
		self.condition = condition
		self.quantity = int(quantity)

	def __str__(self):
		return ' '.join([str(v) for v in self.__dict__.values()])

	def __eq__(self, other):
		if id(self) == id(other):
			return True
		if self.item == other.item and self.spec == other.spec \
			and self.condition == other.condition:
				return True 
		return False

	def __hash__(self):
		return hash(' '.join([str(v) for v in self.__dict__.values()][:-1]))


class IncomingStockEntry(ActualStockEntry):

	def __init__(self, item, spec, condition, quantity, eta):
		super().__init__(item, spec, condition, quantity)
		self.eta = eta 

	def __eq__(self, other):
		if id(self) == id(other):
			return True 
		if self.item == other.item and self.spec == other.spec and \
			self.condition == other.condition and self.eta == other.eta:
				return True 
		return False
	
	def __hash__(self):
		return hash(' '.join(str(v) for v in (self.item, self.condition, self.spec, self.eta)))


class AvailableStockModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, warehouse,*, condition, spec, item=None, mixed_description=None, lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'spec', 'Quantity']
		self.name = 'stocks'
		self.stocks = self.computeStock(warehouse, condition, spec, \
			lines=lines, item=item, mixed_description=mixed_description) 

	def computeStock(self, warehouse, condition, spec, lines =None,\
		item=None ,mixed_description=None):
		session = db.Session()
		query = session.query(db.Imei, db.Imei.condition, db.Imei.spec, \
			func.count(db.Imei.imei).label('quantity')).join(db.Item).join(db.Warehouse).\
			where(db.Warehouse.description == warehouse).group_by(Item.id, db.Warehouse.id, \
				db.Imei.condition, db.Imei.spec)
		if condition:
			query = query.where(db.Imei.condition == condition)
		if spec:
			query = query.where(db.Imei.spec == spec)
		
		if mixed_description:
			from sqlalchemy import and_
			manufacturer, category, model, capacity, *_ = mixed_description.split(' ')
			clause = and_(
				Item.manufacturer == manufacturer, 
				Item.category == category, 
				Item.model == model, 
				Item.capacity == capacity
			)
			query = query.where(clause)
		elif item:
			query = query.where(Item.id == item.id)

		# Result: (<db.Imei object at 0x000001FFAB4B3640>, 'A+', 'JAPAN', 4)
		# keys: RMKeyView(['Imei', 'condition', 'spec', 'quantity'])

		actual_stock = {ActualStockEntry(r.Imei.item, r.spec, r.condition, r.quantity)\
			for r in query}

		query = session.query(Item, sl.condition, sl.spec,func.sum(sl.quantity).label('quantity')).\
			select_from(sp, sl, Warehouse, Item).group_by(Item.id, sl.condition, \
				sl.spec, Warehouse.id).where(sp.id == sl.proforma_id).where(sp.warehouse_id == Warehouse.id).\
					where(sl.item_id == Item.id).where(Warehouse.description == warehouse).\
						where(sp.cancelled == False).where(sp.normal == True)
						# .where(sp.id.in_(relevant))

		if condition:
			query = query.where(sl.condition == condition)
		if spec:
			query = query.where(sl.spec == spec) 
		if item:
			query = query.where(Item.id == item.id)

		# Result : (<db.Item object at 0x000001FBB74CB5E0>, 'A+', 'JAPAN', Decimal('10'))  
		# keys: RMKeyView(['Item', 'condition', 'spec', 'quantity'])

		actual_sales = {ActualStockEntry(r.Item, r.spec, r.condition, r.quantity) for r in query}

		query = session.query(Item, el.condition, el.spec, func.count(es.serie).label('quantity')).\
			select_from(el, es, sp, Warehouse, Item).where(el.id == es.line_id).where(sp.warehouse_id == Warehouse.id).\
				where(el.item_id == Item.id).where(so.proforma_id == sp.id).where(e.expedition_id == so.id).\
					where(sp.cancelled == False).where(Warehouse.description == warehouse).\
						group_by(Item.id, el.condition, el.spec)

		current_outputs = {ActualStockEntry(r.Item, r.spec, r.condition, r.quantity) for r in query}

		for output in current_outputs:
			for stock in actual_stock:
				if output == stock:
					stock.quantity += output.quantity

		for sale in actual_sales:
			for stock in actual_stock:
				if sale == stock:
					stock.quantity -= sale.quantity
					break 
		
		aux = actual_sales.difference(actual_stock)

		actual_stock = list(actual_stock)

		for e in aux:
			e.quantity = (-1) * e.quantity
		actual_stock += list(aux)

		if lines:
			for line in lines:
				for stock in actual_stock:
					if str(line.item) == stock.item and line.condition == stock.condition and \
						line.spec == stock.spec:
							stock.quantity -= line.quantity

		stocks = list(filter(lambda o : o.quantity != 0, actual_stock))

		return stocks

	def checkAgainstLinesBeforeSaving(self):
		pass 

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		row, column = index.row(), index.column() 
		stock = self.stocks[row]

		if role == Qt.DisplayRole:
			if column == 0:
				return stock.item 
			elif column == 1:
				return stock.condition
			elif column == 2:
				return stock.spec
			elif column == 3:
				return str(stock.quantity) + ' pcs'

from collections import namedtuple


# Bad solution
# In ActualStockEntry initializer I 
# execute self.item = str(item)
# Bad decision there, I could let a reference to the 
# object like it is and execute str(item) whenever it
#  needs to be represented.I dont want to change it now 
# because i dont know the side effects of that code. 
# This "patch" will increment the memory foot print
# the size of the items dictionary.

items = {str(item):item for item in db.session.query(Item)}
class StockEntryRequest:

	def __init__(self, stock_entry, requested_quantity):
		self.stock_entry = stock_entry
		self.requested_quantity = requested_quantity
		self.item_object = items[stock_entry.item]

	# For unpacking
	def __iter__(self):
		return iter([self.stock_entry, self.requested_quantity])

class ManualStockModel(AvailableStockModel):

	DESCRIPTION, CONDITION, SPEC, AVAILABLE, REQUEST = 0, 1, 2, 3, 4 

	def __init__(self, warehouse, mixed_description, condition, spec, lines=None):
		super(QtCore.QAbstractTableModel, self).__init__() 
		self._headerData = ['Description', 'Condition', 'spec', \
			'Available', 'Request']
		self.name = 'stocks'
		stocks = self.computeStock(warehouse, mixed_description=mixed_description, \
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

class IncomingStockModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, warehouse, *, item, condition, spec, lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'spec', 'ETA', 'quantity']
		self.name = 'stocks'
		self.stocks = self.computeStock(warehouse, item, condition, spec, lines) 

	def computeStock(self, warehouse, item, condition, spec, lines):
		# Logic:
		# not_arrived_yet = asked - processed 
		# incoming = not_arrived_yet + total purchase with no warehouse order
		# Remember the special case:
		#   if not incoming_stock:
		#       incoming_stock = stock_not_arrived_yet
		#   else:
		#       iterate incoming, iterate asked - processed, add up 

		session = db.Session() 


		proformas = {r[0] for r in session.query(pp.id)}
		orders = {r[0] for r in session.query(po.proforma_id)}

		relevant = proformas.difference(orders)

		processed_query = session.query(Item, pol.condition, pol.spec, pp.eta, func.count(ps.serie).label('processed')).\
			select_from(pp, pol, po, Warehouse, Item, ps).where(pp.id == po.proforma_id).where(pol.order_id == po.id).\
				where(Item.id == pol.item_id).where(ps.line_id == pol.id).where(Warehouse.id == pp.warehouse_id).\
					group_by(Item.id, pp.eta, pol.condition, pol.spec).\
						where(Warehouse.description == warehouse).where(pp.cancelled == False)

		# Result: <db.Item object at 0x00000192B77C2610>, 'NEW', 'EEUU', datetime.date(2020, 10, 16), 10)
		# r.Keys():MKeyView(['Item', 'condition', 'spec', 'eta'])

		asked_query = session.query(Item, pl.condition, pl.spec, pp.eta, func.sum(pl.quantity).label('quantity')).\
			select_from(pp, pl, Warehouse, Item, po).where(pp.id == pl.proforma_id).where(pp.warehouse_id == Warehouse.id).\
				where(pl.item_id == Item.id).where(Warehouse.description == warehouse).where(pp.cancelled == False).\
					where(po.proforma_id == pp.id).\
					group_by(pp.eta, pl.condition, pl.spec, Item.id)


		incoming_query = session.query(Item, pp.eta, pl.condition, pl.spec, func.sum(pl.quantity).label('incoming')).\
			select_from(Item, Warehouse, pp, pl).where(pp.id == pl.proforma_id).where(Warehouse.id == pp.warehouse_id).\
				where(pl.item_id == Item.id).where(pp.cancelled == False).where(pp.id.in_(relevant)).\
					where(Warehouse.description == warehouse).\
					group_by(pp.eta, pl.condition, pl.spec, Item.id)


		sales_query = session.query(Item, sl.eta, sl.condition, sl.spec, func.sum(sl.quantity).label('outgoing')).\
			select_from(Item, Warehouse, sp, sl).where(sp.warehouse_id == Warehouse.id).where(Item.id == sl.item_id).\
				where(sp.id == sl.proforma_id).where(sp.cancelled == False).where(sp.normal == False).\
					where(Warehouse.description == warehouse).\
					group_by(sl.eta, sl.condition, sl.spec, Item.id)

		if item:
			asked_query = asked_query.where(Item.id == item.id)
			processed_query = processed_query.where(Item.id == item.id)
			incoming_query = incoming_query.where(Item.id == item.id)
			sales_query = sales_query.where(Item.id == item.id)
		if condition:
			asked_query = asked_query.where(pl.condition == condition)
			processed_query = processed_query.where(pol.condition == condition)
			incoming_query = incoming_query.where(pl.condition == condition)
			sales_query = sales_query.where(sl.condition == condition)
		if spec:
			asked_query = asked_query.where(pl.spec == spec)
			processed_query = processed_query.where(pol.spec == spec) 
			incoming_query = incoming_query.where(pl.spec == spec)
			sales_query = sales_query.where(sl.spec == spec)

		processed = {IncomingStockEntry(e.Item, e.spec, e.condition, e.processed, e.eta) for e \
			in processed_query}

		asked = {IncomingStockEntry(e.Item, e.spec, e.condition, e.quantity, e.eta) for e \
			in asked_query}

		incomings = { IncomingStockEntry(e.Item, e.spec, e.condition, e.incoming, e.eta) for e \
			in incoming_query}

		
		sales = { IncomingStockEntry(e.Item, e.spec, e.condition, e.outgoing, e.eta) for e \
			in sales_query}

		for a in asked:
			for p in processed:
				if a == p:
					a.quantity -= p.quantity
					break 

		not_arrived_yet = asked 
		
		if not incomings:
			incomings = not_arrived_yet
		else:
			for i in incomings:
				for n in not_arrived_yet:
					if i == n:
						i.quantity += n.quantity
						break 
		
		if sales:
			for sale in sales:
				for incoming in incomings:
					if sale == incoming:
						incoming.quantity -= sale.quantity
						break 
			lost_sales = sales.difference(incomings)
			for sale in lost_sales:
				sale.quantity = (-1) * sale.quantity

		if lines:
			for line in lines:
				for incoming in incomings:
					if str(line.item) == incoming.item and line.condition == incoming.condition and \
						line.spec == incoming.spec and line.eta == incoming.eta:
							incoming.quantity -= line.quantity
							break 

		incomings = list(filter(lambda o : o.quantity != 0, incomings))

		if sales:
			incomings += list(lost_sales)

		return incomings
	
	def checkAgainstLinesBeforeSaving(self):
		pass 

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
				return entry.spec
			elif column == 3:
				return entry.eta.strftime('%d/%m/%Y')
			elif column == 4:
				return str(entry.quantity) + ' pcs'
		elif role == Qt.DecorationRole:
			if column == 3:
				return QtGui.QIcon(':\calendar')

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
			print('seie exists')
			
			raise ValueError('Serie already processed in this reception order')
		
		if any((
			description not in description_id_map.keys(), 
			condition not in conditions.difference({'Mix'}), 
			spec not in specs.difference({'Mix'})
		)): raise ValueError('Invalid description, condition or spec')

		reception_serie = db.ReceptionSerie(
			description_id_map[description], 
			line, serie, condition, spec
		)
		db.session.add(reception_serie)
		try:
			db.session.commit()
			print('dd_model.after commit')
			self.reception_series.append(reception_serie)
		except:
			db.session.rollback()
			raise 

		print('len(self.reception_series)=', len(self.reception_series))

	def delete(self, serie):
		for index, object in enumerate(self.reception_series):
			if serie == object.serie:
				break 
		
		object = self.reception_series[index]
		try:
			db.session.delete(object)
			del self.reception_series[index]
		except:
			db.session.rollback()
			raise 

	def bulk_delete(self, series):
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
				r.item_id == description_id_map[description], 
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
				Group(description_id_map.inverse[item_id], 
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



if __name__ == '__main__':
	
	for d in descriptions:
		print(d)