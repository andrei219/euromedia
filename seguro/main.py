
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session # ORM namespace
from sqlalchemy import func

import openpyxl

from app.db import engine

from datetime import datetime, timedelta

""" Generator for dates from 01/06/2022 to now """

class DateGenerator:

	__start = datetime(2022, 6, 1).date()
	__end = datetime.now().date()
	__step = timedelta(days=1)

	def __iter__(self):
		while self.__start <= self.__end:
			yield self.__start
			self.__start += self.__step

def main():
	wb = openpyxl.Workbook()  # Create a workbook
	ws = wb.active  # Get the active worksheet

	with Session(engine) as session:
		for date in DateGenerator():
			r = session.query(func.get_stock_value(date))
			ws.append((date, r.scalar()))

	wb.save('time series stock value.xlsx')   # Save the workbook


if __name__ == '__main__':
	import time
	start = time.time()
	main()
	end = time.time()
	print(f'Time elapsed: {end - start}')

