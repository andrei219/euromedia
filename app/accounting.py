import sys

from db import Account, session, BankAccount
from accountchart import ACCOUNTS

def save_accounts(accounts, parent=None):
	for group, accounts in accounts.items():
		try:
			account = Account(code=group, name=accounts['name'], parent=parent)
			session.add(account)
			save_accounts(accounts['children'], parent=account)
		except (KeyError, TypeError):
			continue

def create_our_bank_accounts():

	for name, iban in [
		('Santander', '0022'),
		('Bankinter', '0024'),
		('BBVA', '0016'),
		('Caixa', '0081'),
		('Bankia', '2038'),
		('ING', '0075'),
		('Openbank', '2100'),
		('Sabadell', '0083'),
		('Bankia', '2038'),
	]:
		bank_account = BankAccount(name=name, iban=iban)
		session.add(bank_account)
		session.commit()


if __name__ == '__main__':

	if sys.argv[1] == 'create_accounts':
		save_accounts(ACCOUNTS)
	elif sys.argv[1] == 'create_bank_accounts':
		create_our_bank_accounts()

	session.commit()

