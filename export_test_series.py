

from app.db import *

import openpyxl



if __name__ == '__main__':

    if __name__ == '__main__':
        series = session.query(ExpeditionSerie.serie)\
            .join(ExpeditionLine).join(Expedition)\
            .join(SaleProforma).join(Partner).\
            where(Partner.id == 19).limit(25).all()

        wb = openpyxl.Workbook()

        ws = wb.active

        for serie in series:
            ws.append((serie.serie, ))

        wb.save('test.xlsx')