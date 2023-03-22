

from ui_journal_entry_form import Ui_Form
from PyQt5.QtWidgets import QWidget


from utils import setCompleter

from db import Account, session


class Form(Ui_Form, QWidget):

	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.save.clicked.connect(self.save_handler)

	def save_handler(self):
		print('save clicked')

