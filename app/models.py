
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5 import QtGui

from sqlalchemy import inspect, or_ 
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select, func

import db 
import operator


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
	 
	TYPE_NUM , DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL, \
		FROM_PROFORMA = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 
	
	def __init__(self, sale=False, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'Partner', 'Agent', 'Financial', \
			'Logistic', 'Shipment', 'Owing', 'Total', 'From Proforma']
		self.session = db.session
		self.name = 'invoices'
		self.sale = sale 
		self.Proforma = db.PurchaseProforma    
		if sale:
			self.Proforma = db.SaleProforma
		
		self.invoices = self.session.query(self.Proforma).where(self.Proforma.invoice != None).all()         

	
	def _totalDebt(self, invoice):
		return sum([line.quantity * line.price for line in invoice.lines])
	
	def _paid(self, invoice):
		return sum([payment.amount for payment in invoice.payments])


	def _totalQuantity(self, invoice):
		return sum([line.quantity for line in invoice.lines])


	def _totalProcessed(self, invoice):
		processed = 0
		try:
			for line in invoice.order.lines:
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
	
	TYPE_NUM , DATE, ETA, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL, MIXED = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 

	def __init__(self, filters=None, search_key=None):  
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'ETA', 'Partner', 'Agent', 'Financial', 'Logistic', \
			'Shipment', 'Owing', 'Total', 'Mixed']
		self.name = 'proformas'
		db.session = db.Session() 
		self.session = db.session 
		query = self.session.query(db.PurchaseProforma) 

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
					self.proformas = filter(lambda p: not self._paid(p), self.proformas)
				if 'cancelled' in filters['financial']:
					self.proformas = filter(lambda p:p.cancelled, self.proformas)
				if 'fully paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and self._paid(p) == self._totalDebt(p), self.proformas)
				if 'partially paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self._paid(p) < self._totalDebt(p) ,self.proformas)
			
			if 'logistic' in filters:
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and not self._totalProcessed(p), self.proformas)
				if 'partially prepared' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self._totalProcessed(p) < self._totalQuantity(p),\
						self.proformas) 
				
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and self._totalProcessed(p) == self._totalQuantity(p), \
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

	def _totalDebt(self, proforma):
		return sum([line.quantity * line.price for line in proforma.lines]) + \
			sum([line.quantity * line.price for line in proforma.mixed_lines])
	
	def _paid(self, proforma):
		return sum([payment.amount for payment in proforma.payments])


	def _totalQuantity(self, proforma):
		return sum([line.quantity for line in proforma.lines]) + sum([line.quantity for line \
			in proforma.mixed_lines])

	def _totalProcessed(self, proforma):
		processed = 0
		try:
			for line in proforma.order.lines:
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

		if col in (PurchaseProformaModel.FINANCIAL, PurchaseProformaModel.OWING, PurchaseProformaModel.TOTAL):
			paid = self._paid(proforma) 
			total_debt = self._totalDebt(proforma) 
		elif col == PurchaseProformaModel.LOGISTIC:
			total_quantity = self._totalQuantity(proforma)
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
						return 'partially paid' 
					elif paid == total_debt:
						return 'Paid'
					elif paid > total_debt:
						return 'They Owe'

			elif col == PurchaseProformaModel.LOGISTIC:
				if processed_quantity == 0:
					return "Empty"
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
			elif col == PurchaseProformaModel.MIXED:
				return 'Yes' if proforma.mixed else 'No'

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
		current_num = self.session.query(func.max(db.PurchaseInvoice.number)).\
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

		order = db.PurchaseOrder(proforma, note) 
		self.session.add(order) 
		
		if proforma.mixed :
			for line in proforma.mixed_lines:
				self.session.add(db.MixedPurchaseOrderLine(order, line.description, \
					line.condition, line.specification, line.quantity))
		else:
			for line in proforma.lines:
				self.session.add(db.PurchaseOrderLine(order, line.item, line.condition, \
					line.specification, line.quantity))
		try:
			self.session.commit() 
		except:
			self.session.rollback() 
			raise

class SaleProformaModel(BaseTable, QtCore.QAbstractTableModel):
	
	TYPE_NUM, DATE, PARTNER, AGENT, FINANCIAL, LOGISTIC, SENT, OWING, TOTAL = 0, 1, 2, 3, 4, 5, 6, 7, 8

	def __init__(self, search_key=None, filters=None):
		super().__init__() 
		self._headerData = ['Type & Num', 'Date', 'Partner','Agent', 'Financial', 'Logistic',\
			'Shipment', 'Owes', 'Total']
		self.proformas = [] 
		self.name = 'proformas'
		db.sale_session = db.Session() 
		self.session = db.sale_session
		query = self.session.query(db.SaleProforma) 

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
					self.proformas = filter(lambda p: not self._paid(p), self.proformas)
				if 'cancelled' in filters['financial']:
					self.proformas = filter(lambda p:p.cancelled, self.proformas)
				if 'fully paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and self._paid(p) == self._totalDebt(p), self.proformas)
				if 'partially paid' in filters['financial']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self._paid(p) < self._totalDebt(p) ,self.proformas)
			
			if 'logistic' in filters:
				if 'empty' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and not self._totalProcessed(p), self.proformas)
				if 'partially prepared' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and 0 < self._totalProcessed(p) < self._totalQuantity(p),\
						self.proformas) 
				
				if 'completed' in filters['logistic']:
					self.proformas = filter(lambda p:not p.cancelled and self._totalProcessed(p) == self._totalQuantity(p), \
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
	
	def _totalDebt(self, proforma):
		return sum([line.quantity * line.price for line in proforma.lines])
	
	def _paid(self, proforma):
		return sum([payment.amount for payment in proforma.payments])


	def _totalQuantity(self, proforma):
		return sum([line.quantity for line in proforma.lines])

	def _totalProcessed(self, proforma):
		processed = 0
		try:
			for line in proforma.order.lines:
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
			paid = self._paid(proforma) 
			total_debt = self._totalDebt(proforma) 
		elif col == SaleProformaModel.LOGISTIC:
			total_quantity = self._totalQuantity(proforma) 
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
		current_num = self.session.query(func.max(db.SaleInvoice.number)).\
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
		order = db.SaleOrder(proforma, note) 
		self.session.add(order) 
		for line in proforma.lines:
			self.session.add(db.SaleOrderLine(order, line.item, line.condition,\
				line.specification, line.quantity))    
		try:
			self.session.commit() 
		except:
			self.session.rollback() 
			raise

	
	def physicalStockAvailable(self, warehouse_id, lines):
		matches = 0 
		lines_number = len(lines)
		
		for line in lines:
			for stock in self.session.query(func.count(db.Imei.imei).label('quantity'), db.Imei.item_id, db.Imei.condition, \
				db.Imei.specification).join(Warehouse).where(Warehouse.id == warehouse_id).\
					group_by(db.Imei.item_id, db.Imei.specification, db.Imei.condition):
						if line.item_id == stock.item_id and line.condition == stock.condition and \
							line.specification == stock.specification:
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


	def __init__(self, session):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Showing Condt.', 'Spec', \
			'Ignoring Spec?','Qty.', 'Price', 'Subtotal', 'Tax', 'Total']   
		self.session = session
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
		total = str((line.quantity * float(line.price)) * (1 + line.tax/100))
		subtotal = str(line.quantity * line.price) 
		ignore_spec = 'Yes' if line.ignore_specification else 'No'
		showing_condition = line.showing_condition or line.condition
		return {
			SaleProformaLineModel.DESCRIPTION:str(line.item), 
			SaleProformaLineModel.CONDITION:line.condition,
			SaleProformaLineModel.SHOWING_CONDITION:showing_condition, 
			SaleProformaLineModel.SPEC:str(line.specification), 
			SaleProformaLineModel.IGNORING_SPEC:ignore_spec, 
			SaleProformaLineModel.SUBTOTAL:subtotal,
			SaleProformaLineModel.PRICE:str(line.price), 
			SaleProformaLineModel.QUANTITY:(line.quantity),
			SaleProformaLineModel.TAX:str(line.tax), 
			SaleProformaLineModel.TOTAL: total 
		}.get(col) 
		
	def _return_complex_line(self, lines, col):
		
		# Made item hashable
		# Now diff_descritons elements are Item objects
		diff_descriptions = {line.item for line in lines}
		diff_conditions = {line.condition for line in lines}
		diff_specs = {line.specification for line in lines}


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
			specification = diff_specs.pop()
		else:
			specification = 'Mix'

		ignore = 'Yes' if lines[0].ignore_specification else 'No' 
		price = lines[0].price
		quantity = sum([line.quantity for line in lines])
		subtotal = float(price * quantity)
		tax = lines[0].tax
		total = subtotal * ( 1 + tax / 100)
		return {
			SaleProformaLineModel.DESCRIPTION:description, 
			SaleProformaLineModel.CONDITION:condition,
			SaleProformaLineModel.SHOWING_CONDITION:showing_condition, 
			SaleProformaLineModel.SPEC:specification, 
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
		last_group_number = self.session.query(func.max(db.SaleProformaLine.mixed_group_id)).scalar()
		if not last_group_number:
			last_group_number = 0 
		for index in self._lines:
			line_s = self._lines[index]
			if isinstance(line_s, db.SaleProformaLine):
				line_s.proforma = proforma
				self.session.add(line_s) 
			elif isinstance(line_s, list):
				for line in line_s:
					line.proforma = proforma
					line.mixed_group_id = last_group_number
					self.session.add(line) 
				last_group_number += 1 

		try:
			self.session.commit() 
		except:
			self.session.rollback()
			raise 	
	
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

	DESCRIPTION, CONDITION, SPECIFICATION, REQUEST = 0, 1, 2, 3

	def __init__(self, lines):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Specification', 'Requested Quantity']
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
			elif column == ActualLinesFromMixedModel.SPECIFICATION:
				return line.specification
			elif column == ActualLinesFromMixedModel.REQUEST:
				return str(line.quantity)

	def reset(self):
		self.layoutAboutToBeChanged.emit()
		self.lines = []
		self.layoutChanged.emit() 

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
				0:str(line.item), 
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

class MixedPurchaseLineModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, session):
		super().__init__()
		self._headerData = ['Description', 'Condition', 'Spec', 'Qty.', 'Price', 'Subtotal', 'Tax', 'Total']
		self.session = session
		self.name = 'lines'
		self.lines = [] 


	
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
			total = (line.quantity * float(line.price)) * (1 + line.tax/100)
			subtoal = line.quantity * line.price 
			return {
				0:str(line.description), 
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


	def add(self, description, condition, specification, quantity, price, tax):
		line = db.MixedPurchaseLine(description, condition, specification, quantity, price, tax) 

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
			if _line.description == line.description and _line.specification == line.specification \
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

		self.series_at_order_level  = {r[0] for r in self.session.query(self.Serie.serie).join(self.Line).join(self.Order).\
			where(self.Order.id == order.id)}


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
			self.series_at_order_level.add(_serie)
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
			self.series_at_order_level.remove(serie.serie)
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
		if serie in self.series_at_order_level:
			return True 
		else:
			return False

class OrderModel(BaseTable, QtCore.QAbstractTableModel):

	ID, WAREHOUSE, TOTAL, PROCESSED, STATUS, PARTNER, AGENT, WARNING, FROM_PROFORMA, MIXED =\
		0, 1, 2, 3, 4, 5, 6, 7, 8, 9

	def __init__(self, sale=False, search_key=None, filters=None):
		super().__init__() 
		self.session = db.Session() 
		_headerData = ['Order_id', 'Warehouse', 'Total', 'Processed', 'Status','Partner', 'Agent', \
			'Warning', 'From Proforma', 'Mixed']
		self.name = 'orders' 
		self.sale = sale 
		if sale:
			Order = db.SaleOrder
			Proforma = db.SaleProforma
			_headerData.remove('Mixed')
			self._headerData = _headerData
		else:
			Order = db.PurchaseOrder
			Proforma = db.PurchaseProforma
			self._headerData = _headerData



		query = self.session.query(Order).join(Proforma).join(db.Agent).join(db.Partner).join(db.Warehouse) 

		if search_key:
			clause = or_(
				db.Agent.fiscal_name.contains(search_key), db.Partner.fiscal_name.contains(search_key), \
					db.Warehouse.description.contains(search_key)) 
			query = query.where(clause) 

		if filters:
			self.orders = query.all() 
			if 'cancelled' in filters:
				self.orders = filter(lambda o:o.proforma.cancelled, self.orders)
			if 'partially processed' in filters:
				self.orders = filter(lambda o:not o.proforma.cancelled and 0 < self._processed(o) < self._total(o), self.orders)
			if 'empty' in filters:
				self.orders = filter(lambda o :not o.cancelled and not self._processed(o), self.orders)
			if 'completed' in filters:
				self.orders = filter(lambda o: not o.cancelled and self._processed(o) == self._tota(o), self.orders)

			if isinstance(self.orders, filter):
				self.orders = list(self.orders)
		else:
			self.orders = query.all() 

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return 
		order = self.orders[index.row()]
		column = index.column() 

		if role == Qt.DisplayRole: 
			if column == OrderModel.ID:
				return str(order.id).zfill(6)
			elif column == OrderModel.WAREHOUSE:
				return order.proforma.warehouse.description 
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
						if self.sale:
							return 'Partially Prepared'
						else:
							return 'Partially Received'
					elif processed == 0:
						return 'Empty'
			elif column == OrderModel.AGENT:
				return order.proforma.agent.fiscal_name 
			elif column == OrderModel.WARNING:
				return order.note 
			elif column == OrderModel.FROM_PROFORMA:
				return str(order.proforma.type) + '-' + str(order.proforma.number).zfill(6)
			elif column == OrderModel.MIXED:
				try:
					# sale proforma has no mixed attribute
					return 'Yes' if order.proforma.mixed else 'No'
				except AttributeError:
					pass 

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
		if order.lines:
			return sum([line.quantity for line in order.lines])  
		elif order.mixed_lines:
			return sum([line.quantity for line in order.mixed_lines])

	def _processed(self, order):
		processed = 0
		lines = order.lines or order.mixed_lines 
		for line in lines:
			for serie in line.series:
				processed += 1
		return processed


from db import Warehouse, Item
from db import session, func
from db import SaleProforma as sp
from db import SaleProformaLine as sl 

class ActualStockEntry:

	def __init__(self, item, specification, condition, quantity):
		self.item = str(item) 
		self.specification = specification
		self.condition = condition
		self.quantity = int(quantity)

	def __str__(self):
		return ' '.join([str(v) for v in self.__dict__.values()])

	def __eq__(self, other):
		if id(self) == id(other):
			return True
		if self.item == other.item and self.specification == other.specification \
			and self.condition == other.condition:
				return True 
		return False

	def __hash__(self):
		return hash(' '.join([str(v) for v in self.__dict__.values()][:-1]))


class IncomingStockEntry(ActualStockEntry):

	def __init__(self, item, specification, condition, quantity, eta):
		super().__init__(item, specification, condition, quantity)
		self.eta = eta 

	def __eq__(self, other):
		if id(self) == id(other):
			return True 
		if self.item == other.item and self.specification == other.specification and \
			self.condition == other.condition and self.eta == other.eta:
				return True 
		return False
	
	def __hash__(self):
		return hash(' '.join(str(v) for v in (self.item, self.condition, self.specification, self.eta)))


class AvailableStockModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, warehouse,*, condition, specification, item=None, mixed_description=None, lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Specification', 'Quantity']
		self.name = 'stocks'
		self.stocks = self.computeStock(warehouse, condition, specification, \
			lines=lines, item=item, mixed_description=mixed_description) 

	def computeStock(self, warehouse, condition, specification, lines =None,\
		item=None ,mixed_description=None):
		session = db.Session()
		query = session.query(db.Imei, db.Imei.condition, db.Imei.specification, \
			func.count(db.Imei.imei).label('quantity')).join(db.Item).join(db.Warehouse).\
			where(db.Warehouse.description == warehouse).group_by(Item.id, db.Warehouse.id, \
				db.Imei.condition, db.Imei.specification)
		if condition:
			query = query.where(db.Imei.condition == condition)
		if specification:
			query = query.where(db.Imei.specification == specification)
		
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
		# keys: RMKeyView(['Imei', 'condition', 'specification', 'quantity'])

		actual_stock = {ActualStockEntry(r.Imei.item, r.specification, r.condition, r.quantity)\
			for r in query}

		proformas = { r[0] for r in session.query(sp.id)}
		orders = { r[0] for r in session.query(db.SaleOrder.proforma_id)}

		relevant = proformas.difference(orders)

		query = session.query(Item, sl.condition, sl.specification,func.sum(sl.quantity).label('quantity')).\
			select_from(sp, sl, Warehouse, Item).group_by(Item.id, sl.condition, \
				sl.specification, Warehouse.id).where(sp.id == sl.proforma_id).where(sp.warehouse_id == Warehouse.id).\
					where(sl.item_id == Item.id).where(Warehouse.description == warehouse).\
						where(sp.cancelled == False).where(sp.normal == True).where(sp.id.in_(relevant))

		if condition:
			query = query.where(sl.condition == condition)
		if specification:
			query = query.where(sl.specification == specification) 
		if item:
			query = query.where(Item.id == item.id)

		# Result : (<db.Item object at 0x000001FBB74CB5E0>, 'A+', 'JAPAN', Decimal('10'))  
		# keys: RMKeyView(['Item', 'condition', 'specification', 'quantity'])

		actual_sales = {ActualStockEntry(r.Item, r.specification, r.condition, r.quantity) for r in query}

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
						line.specification == stock.specification:
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
				return stock.specification
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

	def __init__(self, warehouse, mixed_description, condition, specification, lines=None):
		super(QtCore.QAbstractTableModel, self).__init__() 
		self._headerData = ['Description', 'Condition', 'Specification', \
			'Available', 'Request']
		self.name = 'stocks'
		stocks = self.computeStock(warehouse, mixed_description=mixed_description, \
			condition=condition, specification=specification, lines=lines) 
		
		self.stocks = {}
		for i, stock in enumerate(stocks):
			self.stocks[i] = StockEntryRequest(stock, 0)


	def computeStock(self, warehouse, *, mixed_description, condition, specification, lines=None):
		return super().computeStock(warehouse, condition, specification, \
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
				return stock.specification
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
from db import PurchaseOrder as po 
from db import PurchaseOrderLine as pol 
from db import PurchaseSerie as ps 

class IncomingStockModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, warehouse, *, item, condition, specification, lines=None):
		super().__init__() 
		self._headerData = ['Description', 'Condition', 'Specification', 'ETA', 'quantity']
		self.name = 'stocks'
		self.stocks = self.computeStock(warehouse, item, condition, specification, lines) 

	def computeStock(self, warehouse, item, condition, specification, lines):
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

		processed_query = session.query(Item, pol.condition, pol.specification, pp.eta, func.count(ps.serie).label('processed')).\
			select_from(pp, pol, po, Warehouse, Item, ps).where(pp.id == po.proforma_id).where(pol.order_id == po.id).\
				where(Item.id == pol.item_id).where(ps.line_id == pol.id).where(Warehouse.id == pp.warehouse_id).\
					group_by(Item.id, pp.eta, pol.condition, pol.specification).\
						where(Warehouse.description == warehouse).where(pp.cancelled == False)

		# Result: <db.Item object at 0x00000192B77C2610>, 'NEW', 'EEUU', datetime.date(2020, 10, 16), 10)
		# r.Keys():MKeyView(['Item', 'condition', 'specification', 'eta'])

		asked_query = session.query(Item, pl.condition, pl.specification, pp.eta, func.sum(pl.quantity).label('quantity')).\
			select_from(pp, pl, Warehouse, Item, po).where(pp.id == pl.proforma_id).where(pp.warehouse_id == Warehouse.id).\
				where(pl.item_id == Item.id).where(Warehouse.description == warehouse).where(pp.cancelled == False).\
					where(po.proforma_id == pp.id).\
					group_by(pp.eta, pl.condition, pl.specification, Item.id)


		incoming_query = session.query(Item, pp.eta, pl.condition, pl.specification, func.sum(pl.quantity).label('incoming')).\
			select_from(Item, Warehouse, pp, pl).where(pp.id == pl.proforma_id).where(Warehouse.id == pp.warehouse_id).\
				where(pl.item_id == Item.id).where(pp.cancelled == False).where(pp.id.in_(relevant)).\
					where(Warehouse.description == warehouse).\
					group_by(pp.eta, pl.condition, pl.specification, Item.id)


		sales_query = session.query(Item, sl.eta, sl.condition, sl.specification, func.sum(sl.quantity).label('outgoing')).\
			select_from(Item, Warehouse, sp, sl).where(sp.warehouse_id == Warehouse.id).where(Item.id == sl.item_id).\
				where(sp.id == sl.proforma_id).where(sp.cancelled == False).where(sp.normal == False).\
					where(Warehouse.description == warehouse).\
					group_by(sl.eta, sl.condition, sl.specification, Item.id)

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
		if specification:
			asked_query = asked_query.where(pl.specification == specification)
			processed_query = processed_query.where(pol.specification == specification) 
			incoming_query = incoming_query.where(pl.specification == specification)
			sales_query = sales_query.where(sl.specification == specification)

		processed = {IncomingStockEntry(e.Item, e.specification, e.condition, e.processed, e.eta) for e \
			in processed_query}

		asked = {IncomingStockEntry(e.Item, e.specification, e.condition, e.quantity, e.eta) for e \
			in asked_query}

		incomings = { IncomingStockEntry(e.Item, e.specification, e.condition, e.incoming, e.eta) for e \
			in incoming_query}

		
		sales = { IncomingStockEntry(e.Item, e.specification, e.condition, e.outgoing, e.eta) for e \
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
						line.specification == incoming.specification and line.eta == incoming.eta:
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
				return entry.specification
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
		self._headerData = ['Serie', 'Description', 'Condition', 'Specification', 'Warehouse']
		self.session = db.Session() 
		self.name = 'series'
		self.series = self.session.query(db.Imei).join(Item).join(Warehouse).all() 
	
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
				return entry.specification
			elif column == 4:
				return entry.warehouse.description

class DefinedDevicesModel(BaseTable, QtCore.QAbstractTableModel):

	ITEM, CONDITION, SPECIFICATION, QUANTITY = 0, 1, 2, 3

	def __init__(self, processed_store, form):
		
		from operator import attrgetter
		from itertools import groupby 

		grouper = attrgetter('item', 'condition', 'spec')

		super().__init__() 
		self._headerData = ('Actual Item', 'Condition', 'Specification', 'Quantity')
		self.name = 'devices'
		self.devices = []
		
		self.desc_to_item_id = form.desc_to_item_id_holder
 
		self.processed_store = processed_store
		processed_store = sorted(self.processed_store, key=grouper) # Python docs advice 
		for item_condt_spec, group in groupby(processed_store, key=grouper):
			qnt = 0
			for g in group:
				qnt += 1 
			self.devices.append(item_condt_spec + (qnt, ))

		
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid(): 
			return
		row, col = index.row(), index.column() 
		reg = self.devices[row]
		if role == Qt.DisplayRole:
			return reg[col]

	
	def save(self):
		session = db.Session() 
		cnt = 0 
		for key in self.processed_store.container:
			for register in self.processed_store.container[key]:
				session.add(db.MixedPurchaseSerie(
					self.desc_to_item_id[register.item], 
					register.line, 
					register.sn, 
					register.condition, 
					register.spec
				))
		try:
			session.commit()
		except:
			raise 

	def __getitem__(self, index):
		try:
			return self.devices[index]
		except IndexError:
			return None

class SeriesListModel(QtCore.QAbstractListModel):

	def __init__(self, series=None):
		super().__init__() 
		self.series = list(series) if series else [] 

	def rowCount(self, index):
		return len(self.series)

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return
		if role == Qt.DisplayRole:
			return self.series[index.row()]

	def delete(self, sn):
		try:
			self.series.remove(sn)
			self.layoutChanged.emit() 
		except ValueError:
			pass 

	def __len__(self):
		return len(self.series) 

	def __getitem__(self, index):
		try:
			return self.series[index]
		except IndexError:
			return None  
	
	def __iter__(self):
		return iter(self.series)

	def __contains__(self, serie):
		return serie in self.series 

	def indexOf(self, serie):
		return self.series.index(serie)

class WarehouseListModel(QtCore.QAbstractListModel):

	def __init__(self):
		super().__init__() 
		self.session = db.Session() 
		self.warehouses = [w for w in self.session.query(db.Warehouse)]
		
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
			self.session.delete(warehouse)
			try:
				self.session.commit()
				del self.warehouses[row]
				self.layoutChanged.emit() 
			except:
				self.session.rollback() 
				raise 
	
	def add(self, warehouse_name):
		if warehouse_name in self.warehouses:
			raise ValueError 
		
		warehouse = db.Warehouse(warehouse_name)
		self.session.add(warehouse)
		try:
			self.session.commit()
			self.warehouses.append(warehouse)
			self.layoutChanged.emit() 
		except:
			self.session.rollback() 
			raise 


class FakeLineModel(BaseTable, QtCore.QAbstractTableModel):

	def __init__(self, session):
		super().__init__()
		self.session = session
		self._headerData = ['Description', 'Condition','Showing Condition','Spec', 'Qty.', 'Price', 'Subtotal', 'Tax', 'Total']   

		self.name = 'lines'
		self.lines = [] 
		
	
	def data(self, index, role=Qt.DisplayRole):
		pass 

	def delete(self, indexes):
		pass 

	def add(self):
		pass 

	def reset(self):
		self.layoutAboutToBeChanged.emit()
		self.lines = []
		self.layoutChanged.emit()
