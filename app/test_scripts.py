

from models import AppliedCreditNotesModel
from models import WhereCreditNotesModel
from db import SaleInvoice, session


if __name__ == '__main__':

    invoice = session.query(SaleInvoice).\
        where(SaleInvoice.id == 159).one()

    model = AppliedCreditNotesModel(invoice) 

    print('*' * 100)
    credit = session.query(SaleInvoice).\
        where(SaleInvoice.id == 199).one()

    model = WhereCreditNotesModel(credit)
