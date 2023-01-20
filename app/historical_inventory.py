import datetime
import os
from collections import Counter
import utils

from openpyxl import load_workbook
from sqlalchemy import func

from db import session, ReceptionSerie, ExpeditionSerie, \
	CreditNoteLine, Imei, ConditionChange, SpecChange, \
	WarehouseChange, PurchaseProforma, Reception, ReceptionLine

class Changes:

	def __init__(self, cls):
		self.changes = {r.sn: r.after for r in session.query(cls)}

	def __getitem__(self, serie):
		return self.changes[serie]


def find_attributes_and_return_inventory_register(serie):
	condition_changes = Changes(ConditionChange)
	spec_changes = Changes(SpecChange)
	warehouse_changes = Changes(WarehouseChange)

	last_input = (
		session.query(ReceptionSerie).
		where(ReceptionSerie.serie == serie).
		order_by(ReceptionSerie.id.desc()).
		first()
	)

	try:
		condition = condition_changes[serie]
	except KeyError:
		condition = last_input.condition

	try:
		spec = spec_changes[serie]
	except KeyError:
		spec = last_input.spec

	try:
		warehouse_name = warehouse_changes[serie]
		warehouse_id = utils.warehouse_id_map[warehouse_name]

	except KeyError:
		warehouse_id = (
			session.query(PurchaseProforma.warehouse_id).
			join(Reception).join(ReceptionLine).join(ReceptionSerie).
			where(ReceptionSerie.serie == serie).scalar()
		)

	return serie, condition, spec, warehouse_id

class Rmas:

	def __init__(self, cutoff_date):
		self.vectors = Counter(
			{
				r.serie: r.qnt for r in
				session.query(
					func.lower(CreditNoteLine.sn).label('serie'), func.count(CreditNoteLine.id).label('qnt')
				).where(func.date(CreditNoteLine.created_on) <= cutoff_date).group_by(CreditNoteLine.sn)
			}
		)

	def __iter__(self):
		return iter(self.vectors)

	def __getitem__(self, item):
		return self.vectors[item]

class Inputs:

	def __init__(self, cutoff_date):
		self.vectors = Counter(
			{
				r.serie: r.qnt for r in
				session.query(
					func.lower(ReceptionSerie.serie).label('serie'), func.count(ReceptionSerie.id).label('qnt')
				).where(func.date(ReceptionSerie.created_on) <= cutoff_date).group_by(
					ReceptionSerie.serie
				)
			}
		)

	def __isub__(self, other):
		self.vectors.subtract(other.vectors)
		return self

	def __iter__(self):
		return iter(self.vectors)

	def __getitem__(self, item):
		return self.vectors[item]

class Outputs:

	def __init__(self, cutoff_date):
		self.vectors = Counter(
			{
				r.serie: r.qnt for r in
				session.query(
					func.lower(ExpeditionSerie.serie).label('serie'), func.count(ExpeditionSerie.id).label('qnt')
				).where(func.date(ExpeditionSerie.created_on) <= cutoff_date).group_by(
					ExpeditionSerie.serie
				)
			}
		)

	def __isub__(self, rmas):
		self.vectors.subtract(rmas.vectors)
		return self

	def __iter__(self):
		return iter(self.vectors)

	def __getitem__(self, item):
		return self.vectors[item]


class HistoricalInventory:

	def __init__(self, cutoff_date):
		inputs, outputs, rmas = Inputs(cutoff_date), Outputs(cutoff_date), Rmas(cutoff_date)
		outputs -= rmas
		inputs -= outputs
		self.series = {serie: qnt for serie, qnt in inputs.vectors.items() if qnt == 1}

		self.inventory = {
			find_attributes_and_return_inventory_register(s) for i, s in enumerate(self.series) if i < 30
		}

	def __len__(self):
		return len(self.series)

	def __iter__(self):
		return iter(self.series)


class Inventory30Dec:

	IMEI_COLUMN = 'D'
	CONDITION_COLUMN = 'B'
	SPEC_COLUMN = 'C'

	def __init__(self):
		base_dir = r'C:\Users\Andrei\Desktop\Updated Prices'
		self.series = set()
		for file in os.listdir(base_dir):
			filepath = os.path.join(base_dir, file)
			self.series.union(self.get_from_workbook(filepath))

	def get_from_workbook(self, filepath):

		workbook = load_workbook(filepath)

		sheet = workbook.active
		s = set()
		for row in sheet.iter_rows(values_only=True):
			try:
				serie = row[ord(self.TARGET_COLUMN) - ord('A')]
				s.add(serie.lower())
			except AttributeError:
				pass

		return s

def test():
	today = datetime.date.today()
	history = HistoricalInventory(today).series
	inventory = set(r.imei for r in session.query(func.lower(Imei.imei).label('imei')))

	print('Len(inventory)=', len(inventory))
	print('Len(HistoricalInventory)=', len(history))
	print('Len(Inventory - HistoricalInventory)=', len(inventory - history))
	print('Len(HistoricalInventory - Inventory)=', len(history - inventory))
	print('Len(History & Inventory)=', len(history & inventory))
	print('Historical inventory is equal to inventory = ', history == inventory)

	for e in inventory - history:
		print('Sample from inventory - history=', e)
		break


if __name__ == '__main__':
	history = HistoricalInventory(datetime.date(2022, 12, 30)).inventory

	for elm in history:
		print(elm)


