from PyQt5.QtCore import Qt

from ui_journal_entry_form import Ui_Form
from PyQt5.QtWidgets import QWidget, QMessageBox

from utils import setCompleter, parse_date, today_date
from delegates import AccountDelegate

from db import session, JournalEntry
from db import AutoEnum
from models import JournalEntryLineModel
from utils import parse_date

class Form(Ui_Form, QWidget):

	def __init__(self, entry=None, parent_form=None):
		super().__init__()
		self.setupUi(self)
		self.parent_form = parent_form
		self.entry = entry or JournalEntry()
		self.model = JournalEntryLineModel(self.entry, self)
		self.view.setModel(self.model)
		self.view.setItemDelegate(AccountDelegate(self.view))
		self.view.resizeColumnsToContents()
		self.view.setColumnWidth(0, 450)
		session.add(self.entry)

		self.populate_form()
		self.set_handlers()

		setCompleter(self.type, JournalEntry.RELATED_TYPES)

	def set_handlers(self):
		self.save.clicked.connect(self.save_handler)
		self.add.clicked.connect(self.add_line)
		self.remove.clicked.connect(self.remove_line)

	def add_line(self):
		row = self.model.rowCount()
		self.model.insertRow(row)
		index = self.model.index(row, 0)
		self.view.setCurrentIndex(index)
		self.view.edit(index)
		self.set_balanced()

	def remove_line(self):
		index = self.view.currentIndex()
		if not index.isValid():
			return
		self.model.removeRow(index.row())
		self.set_balanced()

	def keyPressEvent(self, event) -> None:
		if self.view.hasFocus():
			if event.modifiers() & Qt.ControlModifier:
				if event.key() == Qt.Key_N:
					self.add_line()
				elif event.key() == Qt.Key_D:
					self.remove_line()
		else:
			super().keyPressEvent(event)

	def set_balanced(self):
		if self.model.balanced:
			self.balanced_text.setText('Yes')
			self.balanced_flag.setStyleSheet('background-color: green')
		else:
			self.balanced_text.setText('No')
			self.balanced_flag.setStyleSheet('background-color: red')

	def save_handler(self):
		try:
			self.populate_entry()
			session.commit()
			QMessageBox.information(self, 'Success', 'Entry saved successfully')
			self.close()
		except ValueError as e:
			QMessageBox.critical(self, 'Error', str(e))
			session.rollback()
			session.add(self.entry)

	def populate_form(self):
		try:
			self.id.setText(str(self.entry.id or '').zfill(6))
			if self.entry.id is None:
				self.date.setText(today_date())
				self.autogenerated.setText('No')
				self.autogenerated_flag.setStyleSheet('background-color: red')
			else:
				self.date.setText(self.entry.date.strftime('%d%m%Y'))

			self.description.setText(self.entry.description)
			self.type.setText(self.entry.related_type)

		except (AttributeError, TypeError):
			pass

		if self.entry.auto == AutoEnum.auto_no:
			self.autogenerated.setText('No')
			self.autogenerated_flag.setStyleSheet('background-color: red')
		elif self.entry.auto == AutoEnum.auto_yes:
			self.autogenerated.setText('Yes')
			self.autogenerated_flag.setStyleSheet('background-color: green')
		elif self.entry.auto == AutoEnum.auto_semi:
			self.autogenerated.setText('Semi')
			self.autogenerated_flag.setStyleSheet('background-color: orange')

		self.set_balanced()

	def populate_entry(self):
		self.entry.description = self.description.text()
		try:
			self.entry.date = parse_date(self.date.text())
		except ValueError:
			raise ValueError('Invalid date format')

		if self.type.text() not in JournalEntry.RELATED_TYPES:
			raise ValueError('Invalid type')

		self.entry.related_type = self.type.text()

		# self.entry.lines = self.model.lines

	def set_error_flag(self):
		lines = self.model.lines

	def closeEvent(self, event):
		session.rollback()
		event.accept()
		self.parent_form.set_mv('journal_entries_')
