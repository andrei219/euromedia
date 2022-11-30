
from pyVies import api

import db, utils


if __name__ == '__main__':

    v = api.Vies()
    counter = 0
    for number, name, country in db.session.query(
        db.Partner.fiscal_number,
        db.Partner.trading_name,
        db.Partner.billing_country
    ):
        country_code = utils.get_country_code(country)
        if country_code != 'Not found':
            if number.startswith(country_code):
                print(number, name, country)
                counter +=1




