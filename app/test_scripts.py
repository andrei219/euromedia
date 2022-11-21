

from models import AppliedCreditNotesModel
from models import WhereCreditNotesModel
from db import SaleInvoice, session
import db
from db import func

query_credit = db.session.query(
        db.SaleInvoice.id,
        db.CreditNoteLine.price * db.CreditNoteLine.quantity * (1 + db.CreditNoteLine.tax/100)
    ).join(
        db.SaleProforma, db.SaleProforma.sale_invoice_id == db.SaleInvoice.id
    ).join(
        db.CreditNoteLine, db.SaleProforma.id == db.CreditNoteLine.proforma_id
    )

query_many = db.session.query(db.ManyManySales.credit_id, func.sum(db.ManyManySales.fraction).label('applied'))\
            .group_by(db.ManyManySales.credit_id)




if __name__ == '__main__':


    invoice = session.query(SaleInvoice).\
        where(SaleInvoice.id == 159).one()

    model = AppliedCreditNotesModel(invoice) 

    print('*' * 100)
    credit = session.query(SaleInvoice).\
        where(SaleInvoice.id == 199).one()

    model = WhereCreditNotesModel(credit)

