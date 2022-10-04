import re

from app.db import (
    PurchaseInvoice,
    PurchaseProforma,
    SaleInvoice,
    SaleProforma,
    session,
    ExpeditionSerie,
    ReceptionSerie,
    ExpeditionLine,
    Expedition,
    exists,
    Imei
)


def extract_doc_repr(invoice_text):
    from re import search
    return invoice_text[slice(*re.search(r'[1-6]\-0*\d+\Z', invoice_text).span())]


def build_and_print_tables(sale_invoices):
    total = 0
    print(f"{'Date':25} {'NºDoc':25}{'Partner':50}{'Qty':25}{'Agent':25}")
    print('_' * 140)
    for sale, count in sale_invoices.items():
        total += count
        print(f"{sale.date.strftime('%d/%m/%Y'):25}{sale.doc_repr:25}{sale.partner_name:50}{str(count):25}{sale.agent:25}")

    print(f'Total : ', total)


if __name__ == '__main__':

    sales = dict()

    print('*' * 50)
    print(' ' * 18, 'CLUMSY TRACE')
    print('*' * 50)


    doc_number = input('Enter purchase invoice number: ')


    splitted = extract_doc_repr(doc_number).split('-')

    type, number = splitted[0], splitted[1]

    sales = dict()

    for proforma in session.query(PurchaseProforma).join(PurchaseInvoice).where(
        PurchaseInvoice.type == type,
        PurchaseInvoice.number == number
    ):
        series = set(serie.serie for line in proforma.reception.lines for serie in line.series)

        print(f"Total purchased: ", len(series))

        for line in proforma.reception.lines:
            for serie in line.series:
                exp_series = session.query(ExpeditionSerie).where(ExpeditionSerie.serie == serie.serie).all()
                for e in exp_series:
                    sale_invoice = e.line.expedition.proforma.invoice
                    if sale_invoice not in sales:
                        sales[sale_invoice] = sale_invoice.get_device_count(series)

        build_and_print_tables(sales)

    query = session.query(ExpeditionSerie).join(ReceptionSerie, ReceptionSerie.serie == ExpeditionSerie.serie)


