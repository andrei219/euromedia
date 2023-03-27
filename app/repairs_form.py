

from ui_repairs_form import Ui_Form
from PyQt5.QtWidgets import QDialog

from db import session
from models i

class Form(Ui_Form, QDialog):

	def __init__(self):
		super().__init__()
		self.setupUi(self)

	def save_handler(self):
		print('save')

	def exit_handler(self):
		session.rollback()
		self.close()

	def add_handler(self):
		print('add')

	def remove_handler(self):
		print('remove')