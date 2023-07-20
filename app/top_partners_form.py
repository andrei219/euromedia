

from ui_top_partners_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

import math

from datetime import datetime

import utils

import db

from pdfbuilder import dot_comma_number_repr

from top_partners_pdf_builder import build_document


class AtomicRegister:

    __slots__ = ('partner', 'subtotal', 'tax', 'total')

    def __init__(self, invoice):
        self.partner = invoice.partner_name
        self.subtotal = invoice.subtotal
        self.tax = invoice.tax
        self.total = invoice.total_debt

        # if not all(p.rate == 1 for p in invoice.payments):
        #     base, rated_base = 0, 0
        #     for p in invoice.payments:
        #         base += p.amount
        #         rated_base += p.amount / p.rate
        #
        #     if base != 0 and math.isclose(base, invoice.total_debt):
        #         avg_rate = base / rated_base
        #         self.total = self.total / avg_rate

    def __str__(self):
        return f"AtomicRegister({self.partner}, {self.subtotal}, {self.tax}, {self.total})"


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

        self.exclude_rma = form.exclude_rma.isChecked()

        self.sale = True if form.sale.isChecked() else False


class Register:

    def __init__(self, key, group):
        self.partner = key
        self.subtotal = sum(e.subtotal for e in group)
        self.tax = sum(e.tax for e in group)
        self.total = sum(e.total for e in group)

    def format(self):

        self.subtotal = dot_comma_number_repr('{:,.2f}'.format(self.subtotal))
        self.tax = dot_comma_number_repr('{:,.2f}'.format(self.tax))
        self.total = dot_comma_number_repr('{:,.2f}'.format(self.total))

    def __str__(self):
        return f"{self.rank:10}{self.partner:40}{self.subtotal:20}{self.tax:20}{self.total:20}"


from itertools import groupby


def get_query(filters):
    orm_invoice = db.SaleInvoice if filters.sale else db.PurchaseInvoice
    orm_proforma = db.SaleProforma if filters.sale else db.PurchaseProforma

    print(orm_invoice)

    query = db.session.query(orm_invoice).join(orm_proforma).where(
        orm_invoice.date <= filters.to,
        orm_invoice.date >= filters.from_
    )

    if filters.partner_id:
        query = query.where(orm_proforma.partner_id == filters.partner_id)

    return query


class PDFContent:

    def __init__(self, filters):

        self.from_ = filters.from_
        self.to = filters.to
        self.exclude_rma = filters.exclude_rma
        self.created_on = datetime.now()
        self.registers = []

        atomic_registers = []

        for invoice in get_query(filters):
            if self.exclude_rma and invoice.total_debt < 0:
                continue
            else:
                atomic_registers.append(AtomicRegister(invoice))

        atomic_registers = sorted(atomic_registers, key=lambda r:r.partner)

        for key, group in groupby(atomic_registers, key=lambda r:r.partner):
            self.registers.append(Register(key, list(group)))

        self.registers.sort(key=lambda reg: reg.total, reverse=True)

        for i, element in enumerate(self.registers, start=1):
            setattr(element, 'rank', str(i))

        for e in self.registers:
            e.format()

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        utils.setCompleter(self.partner, tuple(utils.partner_id_map.keys()) + ('All', ))

        self._init_from_to_fields()

        self._export.clicked.connect(self.export_handler)
        self.view.clicked.connect(self.view_handler)



    def _init_from_to_fields(self):
        self.to.setText(datetime.today().strftime('%d%m%Y'))
        self._from.setText(f'0101{datetime.now().year}')

    def _build_report(self):
        try:
            return build_document(PDFContent(Filters(self)))

        except ValueError as ex:
            raise

    def export_handler(self):
        from utils import get_file_path

        file_path = get_file_path(self, pdf_filter=True)

        if not file_path:
            return

        try:
            pdf_document = self._build_report()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', 'Error building the report')
        else:
            pdf_document.output(file_path)
            QMessageBox.information(self, 'Information', 'Report built and exported successfully')

    def view_handler(self):
        try:
            pdf_document = self._build_report()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', 'Error building the report')
        else:
            filename = 'top_partners_report.pdf'
            pdf_document.output(filename)
            import subprocess
            subprocess.Popen((filename,), shell=True)


