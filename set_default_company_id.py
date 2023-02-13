

from app.db import Base
from app.db import session

''' Assert that all tables minus the company table have a company_id field. '''
def assert_company_id_present():
	for table in Base.metadata.tables.values():
		if 'company_id' not in table.columns and table.name != 'companies':
			raise Exception('Table %s is missing a company_id field' % table.name)


''' Update all fields company_id to 1 from all tables. '''
def set_default_company_id():
	for table in Base.metadata.tables.values():
		if 'company_id' in table.columns:
			session.execute(table.update().values(company_id=1))


''' Assert all company_id fields from all tables store the value 1. '''
def assert_company_id_is_one():
	for table in Base.metadata.tables.values():
		if 'company_id' in table.columns:
			for row in session.execute(table.select()):
				if row.company_id != 1:
					raise Exception('Table %s has a company_id field that is not 1' % table.name)


if __name__ == '__main__':
	assert_company_id_present()
	set_default_company_id()
	assert_company_id_is_one()
	print('Success!')

