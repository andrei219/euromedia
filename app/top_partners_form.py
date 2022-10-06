


from ui_top_partners_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog


from datetime import datetime

import utils

import db

from collections import namedtuple


AtomRegister = namedtuple('AtomRegister','partner subtotal tax total')


class Filters:

    def __init__(self, form):
        try:
            self.from_ = utils.parse_date(form._from.text())
        except ValueError:
            raise ValueError('From date format is incorrect. ddmmyyyy')

        try:
            self.to = utils.parse_date(form.to.text())
        except ValueError:
            raise ValueError('To date format is incorrect. ddmmyyyy')

        try:
            self.partner_id = utils.partner_id_map[form.partner.text()]
        except KeyError:
            self.partner_id = None

        self.sale = True if form.sale.isChecked() else False


class Register:

    __slots__ = ('rank', 'partner', 'subtotal', 'tax', 'total')


class Totals:

    pass


def get_query(filters):
    orm_invoice = db.SaleInvoice if filters.sale else db.PurchaseInvoice
    orm_proforma = db.SaleProforma if filters.sale else db.PurchaseProforma

    query = db.session.query(orm_invoice).join(orm_proforma).where(
        orm_invoice.date <= filters.to,
        orm_invoice.date >= filters.from_
    )

    if filters.partner_id:
        query = query.where(orm_proforma.partner_id == filters.partner_id)

    return query

class PDFContent:

    __slots__ = ('from_', 'to', 'registers', 'created_on', 'totals')

    def __init__(self, filters):

        self.from_ = filters.from_
        self.to = filters.to
        self.created_on = datetime.now()
        self.registers = []

        for invoice in get_query(filters):

            print(invoice)

    def print(self):
        pass


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        utils.setCompleter(self.partner, tuple(utils.partner_id_map.keys()) + ('All', ))

        self._export.clicked.connect(self.export_handler)
        self.view.clicked.connect(self.view_handler)


    def export_handler(self):
        print('export')


    def view_handler(self):

        PDFContent(Filters(self))


