
from app.db import SaleProforma, session
from datetime import datetime

if __name__ == '__main__':

	for sale in session.query(SaleProforma):
		for line in sale.credit_note_lines:
			line.created_on = datetime.fromordinal(sale.date.toordinal())

	session.commit()
