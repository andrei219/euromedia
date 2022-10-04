import re

from app.db import (
    PurchaseInvoice,
    PurchaseProforma,
    SaleInvoice,
    SaleProforma,
    session,
    ExpeditionSerie,
    ExpeditionLine,
    Expedition
)


def extract_doc_repr(invoice_text):
    from re import search
    return invoice_text[slice(*re.search(r'[1-6]\-0*\d+\Z', invoice_text).span())]


def build_and_print_tables(sale_invoices):

    print(f"{'Date':25} {'NºDoc':25}{'Partner':50}{'Qty':25}{'Agent':25}")
    print('_' * 140)
    for sale in sale_invoices:
        print(f"{sale.date.strftime('%d/%m/%Y'):25}{sale.doc_repr:25}{sale.partner_name:50}{str(sale.device_count):25}{sale.agent:25}")



if __name__ == '__main__':

    sales = set()

    print('*' * 50)
    print(' ' * 20, 'CLUMSY TRACE')
    print('*' * 50)

    while True:

        doc_number = input('Enter purchase invoice number: ')

        try:
            splitted = extract_doc_repr(doc_number).split('-')
            type, number = splitted[0], splitted[1]

            for proforma in session.query(PurchaseProforma).join(PurchaseInvoice).where(
                PurchaseInvoice.type == type,
                PurchaseInvoice.number == number
            ):
                for line in proforma.reception.lines:
                    for serie in line.series:
                        sale_invoice = session.query(SaleInvoice).join(SaleProforma).\
                            join(Expedition).join(ExpeditionLine).join(ExpeditionSerie).where(ExpeditionSerie.serie == serie.serie).first()

                    sales.add(sale_invoice)

            build_and_print_tables(sales)


        except AttributeError:
            print("I couldn't understand that doc number. Try Again.")
            raise

