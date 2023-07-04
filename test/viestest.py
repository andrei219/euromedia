import sys
import os
import time
import pycountry

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyVies.api as vies

from app.db import Partner
from app.db import session


def get_country_code(name):
	return {
		country.name: country.alpha_2
		for country in pycountry.countries
	}.get(name, 'Not found')


def vies_checker(p: Partner):
	number: str = p.fiscal_number
	country: str = p.billing_country
	code = get_country_code(country)

	if number.startswith(code):
		try:
			request = vies.Vies().request(vat_number=number)
		except (vies.ViesValidationError, vies.ViesError) as ex:
			print(country, number, ':', str(ex))
		else:
			print(f'{country} {number} request.valid={request.valid}')
		return True
	else:
		return False

if __name__ == '__main__':
	for partner in session.query(Partner):
		was_hit = vies_checker(partner)
		if was_hit:
			time.sleep(3)
