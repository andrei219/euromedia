import operator
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from collections import namedtuple
from datetime import date
from app.models import OutputModel
from app.utils import parse_date
import pandas as pd


# This script will generate a report for any month from May 2022 to the current month
# The report will be saved in the reports folder
# The report will be a xlsx file with the following columns:
# Description, Condition, Spec, Quantity sold, Cost Price, Sale Price

Period = namedtuple('Period', ['start', 'end'])


periods = {
	'Mayo 2022': Period(start=date(2022, 5, 1), end=date(2022, 5, 31)),
	'Junio 2022': Period(start=date(2022, 6, 1), end=date(2022, 6, 30)),
	'Julio 2022': Period(start=date(2022, 7, 1), end=date(2022, 7, 31)),
	'Agosto 2022': Period(start=date(2022, 8, 1), end=date(2022, 8, 31)),
	'Septiembre 2022': Period(start=date(2022, 9, 1), end=date(2022, 9, 30)),
	'Octubre 2022': Period(start=date(2022, 10, 1), end=date(2022, 10, 31)),
	'Noviembre 2022': Period(start=date(2022, 11, 1), end=date(2022, 11, 30)),
	'Diciembre 2022': Period(start=date(2022, 12, 1), end=date(2022, 12, 31)),
}

directory_path = r'C:\Users\Andrei\Desktop\Reports'

def main():
	for month, period in periods.items():
		model = OutputModel.by_period(_from=period.start, to=period.end, exclude_at_capital=True)
		print(f'Model for month: {month} loaded')
		getter = operator.attrgetter('sitem', 'scond', 'sspec', 'peuro', 'seuro')
		data = []
		for r in model._registers:
			try:
				row = list(getter(r))
				row.insert(3, 1)

				row[-1] = float(row[-1])
				row[-2] = float(row[-2])
				data.append(row)
			except (ValueError, AttributeError):
				continue

		frame = pd.DataFrame(
			data=data,
			columns=['Product', 'Condition', 'Spec', 'Quantity', 'Cost Price', 'Sale Price']
		)

		group_by_columns = ['Product', 'Condition', 'Spec']
		agg_columns = {
			'Quantity': 'sum',
			'Cost Price': 'mean',
			'Sale Price': 'mean'
		}
		grouped_frame = frame.groupby(group_by_columns).agg(agg_columns)
		grouped_frame = grouped_frame.reset_index()
		grouped_frame['Profit'] = grouped_frame['Sale Price'] - grouped_frame['Cost Price']

		grouped_frame = grouped_frame.rename(
			columns={
				'Quantity': 'Quantity Sold',
				'Cost Price': 'Average Cost Price',
				'Sale Price': 'Average Sale Price',
			}
		)

		grouped_frame.to_excel(os.path.join(directory_path, f'{month}.xlsx'), index=False)
		print(f'Report for month: {month} generated successfully')
		print('-' * 100)


def pandas_test():
	data = [
		['Product 1', 'Condition 1', 'Spec 1', 1, 10, 20],
		['Product 1', 'Condition 1', 'Spec 1', 1, 10, 20],
		['Product 2', 'Condition 1', 'Spec 1', 1, 12, 14],
		['Product 1', 'Condition 1', 'Spec 1', 1, 10, 20],
		['Product 1', 'Condition 1', 'Spec 1', 1, 10, 20],
		['Product 2', 'Condition 1', 'Spec 1', 1, 12, 15],
	]

	result = [
		['Product 1', 'Condition 1', 'Spec 1', 4, 10, 20],
		['Product 2', 'Condition 1', 'Spec 1', 2, 12, 14.5],
	]

	frame = pd.DataFrame(
		data=data,
		columns=['Product', 'Condition', 'Spec', 'Quantity', 'Cost Price', 'Sale Price']
	)

	group_by_columns = ['Product', 'Condition', 'Spec']
	agg_columns = {
		'Quantity': 'sum',
		'Cost Price': 'mean',
		'Sale Price': 'mean'
	}

	grouped_frame = frame.groupby(group_by_columns).agg(agg_columns)
	grouped_frame['Profit'] = grouped_frame['Sale Price'] - grouped_frame['Cost Price']

	print(grouped_frame)

if __name__ == '__main__':

	main()
