

from ui_repairs_form import Ui_Form
from PyQt5.QtWidgets import QDialog, QMessageBox

from db import session
from models import RepairsModel
from delegates import RepairDelegate


class Form(Ui_Form, QDialog):

	def __init__(self, parent=None):
		super().__init__()
		self.setupUi(self)

		self.model = RepairsModel()
		self.view.setModel(self.model)
		self.view.setItemDelegate(RepairDelegate(parent=self))

		self.set_handlers()

	def set_handlers(self):
		self.save.clicked.connect(self.save_handler)
		self.exit.clicked.connect(self.exit_handler)
		self.add.clicked.connect(self.add_handler)
		self.remove.clicked.connect(self.remove_handler)

	def save_handler(self):
		if self.model.valid:
			self.model.save()
			self.close()
		else:
			QMessageBox.warning(self, 'Warning', 'Please fill all required fields')



	def exit_handler(self):
		session.rollback()
		self.close()

	def add_handler(self):
		print('add')

	def remove_handler(self):
		print('remove')