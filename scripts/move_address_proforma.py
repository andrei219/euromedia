

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SaleProforma, session

if __name__ == '__main__':

	for p in session.query(SaleProforma):
		p.shipping_address = p.partner.shipping_addresses[0]

	session.commit()
