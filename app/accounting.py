import sys
import functools

from db import Account, session, BankAccount, Partner
from accountchart import ACCOUNTS

# These accounts will be fathers for objects of our system.
# Partners from spain will be children of CUSTOMER_EUR_CODE
# Partners from outside spain will be children of CUSTOMER_EXT_CODE
# Partners from spain will be children of SUPPLIER_EUR_CODE
# Partners from outside spain will be children of SUPPLIER_EXT_CODE
# Bank accounts will be children of BANK_EUR_CODE
# Cash accounts will be children of CASH_EUR_CODE

SUPPLIER_EUR_CODE = '4000'
SUPPLIER_EXT_CODE = '4004'

CUSTOMER_EUR_CODE = '4300'
CUSTOMER_EXT_CODE = '4304'

CASH_EUR_CODE = '570'
CASH_EXT_CODE = '571'
BANK_EUR_CODE = '572'
BANK_EXT_CODE = '573'

def commit(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		func(*args, **kwargs)
		session.commit()
	return wrapper


@commit
def save_accounts(accounts, parent=None):
	for group, accounts in accounts.items():
		try:
			account = Account(code=group, name=accounts['name'], parent=parent)
			session.add(account)
			save_accounts(accounts['children'], parent=account)
		except (KeyError, TypeError):
			continue

@commit
def create_our_bank_accounts():

	for name, iban in [
		('Santander', 'ES0022'),
		('Bankinter', 'ES0024'),
		('BBVA', 'ES0016'),
		('Caixa', 'ES0081'),
		('Bankia', 'ES2038'),
		('ING', 'ES0075'),
		('Open Bank', '2100'),
		('Wise', 'BE0034'),
		('ChinaBank', 'CH0023'),
		('Sabadell', '0083'),
		('Bankia', '2038'),
	]:
		bank_account = BankAccount(name=name, iban=iban)
		session.add(bank_account)

@commit
def include_partners_into_account_chart():
	partners = session.query(Partner).all()

	# Include partners into customers accounts
	for partner in partners:
		CODE = CUSTOMER_EUR_CODE if partner.billing_country == 'Spain' else CUSTOMER_EXT_CODE
		parent_account = session.query(Account).filter(Account.code == CODE).one()
		code = CODE + f'.{str(partner.id).zfill(4)}'
		session.add(
			Account(
				code=code, name=partner.fiscal_name,
				parent=parent_account,
				related_type='partner',
				related_id=partner.id
			)
		)

	# Include partners into suppliers accounts
	for partner in partners:
		CODE = SUPPLIER_EUR_CODE if partner.billing_country == 'Spain' else SUPPLIER_EXT_CODE
		parent_account = session.query(Account).filter(Account.code == CODE).one()
		code = CODE + f'.{str(partner.id).zfill(4)}'
		session.add(
			Account(
				code=code, name=partner.fiscal_name,
				parent=parent_account,
				related_type='partner',
				related_id=partner.id
			)
		)

@commit
def include_bank_accounts_into_account_chart():
	bank_accounts = session.query(BankAccount).all()

	for bank_account in bank_accounts:
		CODE = BANK_EUR_CODE if bank_account.iban.startswith('ES') else BANK_EXT_CODE
		parent_account = session.query(Account).filter(Account.code == CODE).one()
		code = CODE + f'.{str(bank_account.id).zfill(4)}'
		session.add(
			Account(
				code=code, name=bank_account.name,
				parent=parent_account,
				related_type='bank_account',
				related_id=bank_account.id
			)
		)

if __name__ == '__main__':

	if sys.argv[1] == 'create_accounts':
		save_accounts(ACCOUNTS)

	elif sys.argv[1] == 'create_bank_accounts':
		create_our_bank_accounts()
	elif sys.argv[1] == 'include_partners':
		include_partners_into_account_chart()
	elif sys.argv[1] == 'include_bank_accounts':
		include_bank_accounts_into_account_chart()
	elif sys.argv[1] == 'create_all':
		save_accounts(ACCOUNTS)
		create_our_bank_accounts()
		include_partners_into_account_chart()
		include_bank_accounts_into_account_chart()




