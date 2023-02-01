from app.db import WhIncomingRma, session, SaleInvoice

from sqlalchemy.exc import NoResultFound

counter = 0

def invert_relationship():
    global counter
    for order in session.query(WhIncomingRma):
        counter += 1
        try:
            invoice = session.query(SaleInvoice)\
                .where(SaleInvoice.id == order.sale_invoice_id).one()
            invoice.wh_incoming_rma_id = order.id
        except NoResultFound:
            pass



if __name__ == '__main__':
    invert_relationship()

    session.commit()