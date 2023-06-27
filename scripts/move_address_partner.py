
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import Partner, ShippingAddress
from app.db import session

if __name__ == '__main__':

	for partner in session.query(Partner):
		address = ShippingAddress(
			partner_id=partner.id,
			line1=partner.shipping_line1,
			line2=partner.shipping_line2,
			city=partner.shipping_city,
			state=partner.shipping_state,
			zipcode=partner.shipping_postcode,
			country=partner.shipping_country
		)
		address.partner = partner
		session.add(address)

	session.commit()
