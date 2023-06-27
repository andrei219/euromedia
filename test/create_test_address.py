
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.db import Partner, ShippingAddress, session
from faker import Faker

if __name__ == '__main__':
	partner: Partner
	faker = Faker()
	for partner in session.query(Partner):
		for i in range(4):

			while True:
				country = faker.country()
				if len(country) <= 50:
					break

			partner.shipping_addresses.append(
				ShippingAddress(
					line1=faker.street_address(),
					line2=faker.secondary_address(),
					city=faker.city(),
					state=faker.state(),
					zipcode=faker.postcode(),
					country=country
				)
			)

	session.commit()

