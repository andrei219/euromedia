

from ui_discount_form import Ui_Form
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt

from db import session
from models import DiscountModel
from delegates import RepairDelegate


class Form(Ui_Form, QDialog):

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setupUi(self)

		self.model = DiscountModel()
		self.view.setModel(self.model)

		self.view.setColumnWidth(1, 300)
		self.view.setColumnWidth(2, 300)

		self.set_handlers()

	def set_handlers(self):
		self.save.clicked.connect(self.save_handler)
		self.exit.clicked.connect(self.exit_handler)
		self.add.clicked.connect(self.add_handler)
		self.remove.clicked.connect(self.remove_handler)

	def save_handler(self):
		if self.model.valid:
			session.commit()
			QMessageBox.information(self, 'Success', 'Data saved successfully')
			self.close()
		else:
			QMessageBox.warning(self, 'Warning', 'Please fill all required fields')

	def exit_handler(self):
		session.rollback()
		self.close()

	def keyPressEvent(self, event) -> None:
		if self.view.hasFocus():
			if event.modifiers() & Qt.ControlModifier:
				if event.key() == Qt.Key_N:
					self.add_handler()
				elif event.key() == Qt.Key_D:
					self.remove_handler()
		super().keyPressEvent(event)

	def add_handler(self):
		row = self.model.rowCount()
		self.model.insertRow(row)
		index = self.model.index(row, 0)
		self.view.setCurrentIndex(index)
		self.view.edit(index)

	def remove_handler(self):
		index = self.view.currentIndex()
		if not index.isValid():
			return
		self.model.removeRow(index.row())

