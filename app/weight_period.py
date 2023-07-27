import os.path

import openpyxl

from collections import namedtuple

from datetime import datetime

from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_weight_period import Ui_Dialog


from utils import get_directory
from db import session

from sqlalchemy import text

Period = namedtuple('Period', ['start', 'end'])

query = """
	select
	    'Purchase' as Operation,
	    'Device' as Type,
	    count(items.id) as 'Count',
	    sum(items.weight) as 'Weight'
	from reception_series inner join items
	on items.id = reception_series.item_id
	where items.weight != 0
	  and date(reception_series.created_on) between :from and :to
	union all
	select
	    'Purchase' as Operation,
	    'Battery' as Type,
	    count(items.id) as 'Count',
	    coalesce(sum(items.battery_weight), 0) as ' Weight'
	from reception_series inner join items
	on items.id = reception_series.item_id
	where items.battery_weight != 0
	and date(reception_series.created_on) between :from and :to
	union all
	select
	    'Sale' as Operation,
	    'Device' as Type,
	    count(items.id) as 'Count',
	    sum(items.weight) as 'Weight'
	from expedition_series
	    inner join expedition_lines on expedition_lines.id=expedition_series.line_id
	    inner join items on items.id = expedition_lines.item_id
	    where items.weight != 0
	    and date(expedition_series.created_on) between :from and :to
	union all
	select
	    'Sale' as Operation,
	    'Battery' as Type,
	    count(items.id) as 'Count',
	    coalesce(sum(items.battery_weight),0) as 'Weight'
	from expedition_series
	    inner join expedition_lines on expedition_lines.id=expedition_series.line_id
	    inner join items on items.id = expedition_lines.item_id
	    where items.battery_weight != 0
	    and date(expedition_series.created_on) between :from and :to
	union all
	select
	    'RMA' as Operation,
	    'Device' as Type,
	    count(credit_note_lines.id) as 'Count',
	    coalesce(sum(items.weight), 0) as 'Weight'
	from credit_note_lines inner join items
	on items.id = credit_note_lines.item_id
	where items.weight != 0
	and date(credit_note_lines.created_on) between :from and :to
	union all
	select
	    'RMA' as Operation,
	    'Battery' as Type,
	    count(credit_note_lines.id) as 'Count',
	    coalesce(sum(items.battery_weight), 0) as 'Weight'
	from credit_note_lines inner join items
	on items.id = credit_note_lines.item_id
	where items.battery_weight != 0
	and date(credit_note_lines.created_on) between :from and :to
"""

class Form(Ui_Dialog, QDialog):

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setupUi(self)

		self.export_.clicked.connect(self.export_handler)

		self.decide_period()

	def decide_period(self):
		year = datetime.now().year
		month = datetime.now().month
		period = {
			1: Period(start=f'0101', end=f'3103'),
			2: Period(start='0101', end='3103'),
			3: Period(start='0101', end='3103'),
			4: Period(start='0101', end='3103'),
			5: Period(start='0101', end='3103'),
			6: Period(start='0101', end='3103'),
			7: Period(start='0104', end='3006'),
			8: Period(start='0104', end='3006'),
			9: Period(start='0104', end='3006'),
			10: Period(start='0107', end='3009'),
			11: Period(start='0107', end='3009'),
			12: Period(start='0107', end='3009'),
		}.get(month)
		
		self.start.setText(period.start + f'{year}')
		self.end.setText(period.end + f'{year}')

	def export_handler(self):
		directory = get_directory(self)

		if not directory:
			return
		filename = f'weights_{datetime.now().strftime("%Y-%m-%d")}.xlsx '
		file_path = os.path.join(directory, filename)

		try:

			from_ = datetime.strftime(datetime.strptime(self.start.text(), '%d%m%Y'), '%Y-%m-%d')
			to = datetime.strftime(datetime.strptime(self.end.text(), '%d%m%Y'), '%Y-%m-%d')

		except ValueError:
			QMessageBox.critical(self, 'Error', 'Invalid date format. Correct format 01012023')
			return

		self.save_data(file_path, from_, to)

		QMessageBox.information(self, 'Info', f'Saved to {file_path}')
		

	@staticmethod
	def save_data(file_path, from_, to):
		wb = openpyxl.Workbook()
		ws = wb.active
		ws.title = 'Weights'
		ws.append(('Operation', 'Type', 'Count', 'Weight'))

		for e in session.execute(text(query), params={'from': from_, 'to': to}):
			ws.append(tuple(e))

		wb.save(file_path)
		