
from app.db import *
from datetime import date

from sqlalchemy import or_

_from = date(2022, 7, 1)
to = date(2022, 12, 19)

def get_mean(Line, Parent):
    lines = (
        session.query(Line).join(Parent).
        where(Parent.date >= _from, Parent.date <= to).
        where(Parent.cancelled == False).
        where(or_(Line.description.contains('Mixed'), Line.item_id != None)).all()
    )

    return sum(line.quantity * line.price for line in lines) / sum(line.quantity for line in lines)


if __name__ == '__main__':

    print('Compras: ', get_mean(PurchaseProformaLine, PurchaseProforma))
    print(' Ventas: ', get_mean(SaleProformaLine, SaleProforma))

