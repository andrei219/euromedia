

from app.db import (
	WarehouseChange,
	Warehouse,
	ReceptionLine,
	PurchaseProformaLine,
	PurchaseProforma,
	ReceptionSerie,
	session,
	Imei
)


def get_purchase_line(id):
	return session.query(PurchaseProformaLine).where(PurchaseProformaLine.id == id).one()

def get_reception_line(id):
	return session.query(ReceptionLine).where(ReceptionLine.id == id).one()

def get_serie(s):
	return session.query(ReceptionSerie).where(ReceptionSerie.serie == s).first()

def get_purchase(id=None):
	if id is None:
		return session.query(PurchaseProforma).first()
	else:
		return session.query(PurchaseProforma).where(PurchaseProforma.id == id).one()

if __name__ == '__main__':

	purchase_line, reception_line, reception_serie = \
		get_purchase_line(id=1), get_reception_line(id=1), get_serie('353294074598196')

	purchase_line.condition = reception_line.condition = reception_serie.condition = 'C'
	purchase_line.spec = reception_line.spec = reception_serie.spec = 'US'

	purchase_line, reception_line, reception_serie \
		= get_purchase_line(id=2), get_reception_line(id=2), get_serie('355440076402816')

	purchase_line.condition = reception_line.condition = reception_serie.condition = 'A-'
	purchase_line.spec = reception_line.spec = reception_serie.spec = 'US'

	purchase = get_purchase()
	purchase.warehouse_id = 2

	session.commit()

	before = session.query(Warehouse.description).where(Warehouse.id == 1).scalar()
	after = session.query(Warehouse.description).where(Warehouse.id == 2).scalar()

	change = WarehouseChange(sn='356980069970237', before=before, after=after)

	session.add(change)

	session.commit()






