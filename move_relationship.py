
from app.db import SaleInvoice, session
from app.db import ManyManySales

import pyVies.api

def move_credit_relationship():

    """
    Move relationship sale-sale one-many to an external table
    which will allow the opposite sense, many-one and together,
    a many-many relationship  will be possible.
    """

    for sale in session.query(SaleInvoice).where(SaleInvoice.parent_id != None):

        mm = ManyManySales(sale.parent_id, sale.id, sale.total_debt)
        # mm.sale_id = sale.parent_id
        # mm.credit_id = sale.id
        # mm.fraction = sale.total_debt

        session.add(mm)

    session.commit()


if __name__ == '__main__':

    move_credit_relationship()
