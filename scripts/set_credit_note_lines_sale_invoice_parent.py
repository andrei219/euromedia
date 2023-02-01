

from app.db import SaleProforma, session


def set_relationship():
	query = (
		session.query(SaleProforma).where(SaleProforma.warehouse_id == None)
	)
	for proforma in query:
		invoice_id = proforma.sale_invoice_id
		for line in proforma.credit_note_lines:
			line.invoice_id = invoice_id

	session.commit()


if __name__ == '__main__':

	set_relationship()


