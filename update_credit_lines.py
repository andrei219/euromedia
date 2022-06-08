

from app.db import *

if __name__ == '__main__':
    clines = session.query(CreditNoteLine).all()
    for cline in clines:
        whorder = cline.proforma.invoice.wh_incoming_rma
        for whline in whorder.lines:
            print(whline)
