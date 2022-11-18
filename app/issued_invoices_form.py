
from ui_issued_invoices_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from issued_invoices_pdf_builder import build_document, PDF
from datetime import datetime

import utils
import db


class Filters:

    def __init__(self, form):
        # Getting data for predicates for query
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

        try:
            self.agent_id = utils.agent_id_map[form.agent.text()]
        except KeyError:
            self.agent_id = None

        for radioname in ('financial_all', 'paid', 'notpaid'):
            if getattr(form, radioname).isChecked():
                self.financial = radioname
                break

        self.series = [
            serie for serie in range(1, 7)
            if getattr(form, 'serie_' + str(serie)).isChecked()
        ]

    def __repr__(self):
        return str(self.__dict__.values())


from pdfbuilder import dot_comma_number_repr


class Register:

    def __init__(self, invoice):
        self.doc_repr = invoice.doc_repr
        self.date = invoice.date.strftime('%d/%m/%Y')
        self.partner = invoice.partner_name
        self.agent = invoice.agent
        self.financial = invoice.financial_status_string

        if self.financial is None:
            self.financial = 'Not Found'
        self.subtotal = dot_comma_number_repr('{:,.2f}'.format(invoice.subtotal))
        self.tax = dot_comma_number_repr('{:,.2f}'.format(invoice.tax))
        self.debt = dot_comma_number_repr('{:,.2f}'.format(invoice.total_debt))
        self.currency = 'EUR' if invoice.proformas[0].eur_currency else 'USD'

    def __str__(self):
        return f"{self.doc_repr:12}{self.date:14}{self.partner:40}{self.agent:14}{self.financial:16}{self.subtotal:14}{self.tax:10}{self.debt:14}{self.currency:10}"


class Totals:

    __slots = ('eur_subtotal', 'eur_tax', 'eur_total', 'dollar_subtotal', 'dollar_tax', 'dollar_total')

    def __init__(self):
        self._eur_subtotal = 0
        self._eur_tax = 0
        self._eur_total = 0
        self._dollar_subtotal = 0
        self._dollar_tax = 0
        self._dollar_total = 0

    def format(self):
        self._eur_subtotal = dot_comma_number_repr('{:,.2f}'.format(self._eur_subtotal))
        self._eur_tax = dot_comma_number_repr('{:,.2f}'.format(self._eur_tax))
        self._eur_total = dot_comma_number_repr('{:,.2f}'.format(self._eur_total))
        self._dollar_subtotal = dot_comma_number_repr('{:,.2f}'.format(self._dollar_subtotal))
        self._dollar_total = dot_comma_number_repr('{:,.2f}'.format(self._dollar_total))
        self._dollar_tax = dot_comma_number_repr('{:,.2f}'.format(self._dollar_tax))

    @property
    def eur_subtotal(self):
        return f'{"Total EUR(excl. VAT):":>30}{self._eur_subtotal:>20}'

    @property
    def eur_tax(self):
        return f'{"Total EUR VAT:":>30}{self._eur_tax:>20}'

    @property
    def eur_total(self):
        return f'{"Total EUR:":>30}{self._eur_total:>20}'

    @property
    def dollar_total(self):
        return f'{"Total USD:":>30}{self._dollar_total:>20}'

    @property
    def dollar_tax(self):
        return f'{"Total USD VAT:":>30}{self._dollar_tax:>20}'

    @property
    def dollar_subtotal(self):
        return f'{"Total USD(excl. VAT):":>30}{self._dollar_subtotal:>20}'

    def __iter__(self):
        return iter((self.eur_subtotal, self.eur_tax, self.eur_total,
                     self.dollar_subtotal, self.dollar_tax, self.dollar_total))

def getquery(filters):
    query = db.session.query(db.SaleInvoice).join(db.SaleProforma).\
        join(db.Partner).join(db.Agent)\
        .where(
            db.SaleInvoice.date <= filters.to,
            db.SaleInvoice.date >= filters.from_,
    )

    if filters.series:
        query = query.where(db.SaleInvoice.type.in_(filters.series))

    if filters.agent_id:
        query = query.where(db.SaleProforma.agent_id == filters.agent_id)

    if filters.partner_id:
        query = query.where(db.SaleProforma.partner_id == filters.partner_id)

    return query


class PDFContent:

    __slots__ = ('from_', 'to', 'registers', 'created_on', 'totals')

    def __init__(self, filters: Filters):
        self.from_ = filters.from_
        self.to = filters.to
        self.created_on = datetime.now()

        self.registers = []
        self.totals = Totals()

        for invoice in getquery(filters):
            self.registers.append(Register(invoice))
            prefix = '_eur_' if invoice.proformas[0].eur_currency else '_dollar_'
            setattr(self.totals, prefix + 'tax', getattr(self.totals, prefix + 'tax') + invoice.tax)
            setattr(self.totals, prefix + 'total', getattr(self.totals, prefix + 'total') + invoice.total_debt)
            setattr(self.totals, prefix + 'subtotal', getattr(self.totals, prefix + 'subtotal') + invoice.subtotal)

        self.totals.format()


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        utils.setCompleter(self.agent, tuple(utils.agent_id_map.keys()) + ('All',))
        utils.setCompleter(self.partner, tuple(utils.partner_id_map.keys()) + ('All', ))

        self.view.clicked.connect(self.view_handler)
        self._export.clicked.connect(self.export_handler)
        self.series_all.toggled.connect(self.all_checked)

    def all_checked(self, checked):
        for serie in range(1, 7):
            getattr(self, 'serie_' + str(serie)).setChecked(checked)

    def view_handler(self):
        try:
            pdf_document = self._build_report()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', 'Error building the report')
        else:
            filename = 'report.pdf'
            pdf_document.output(filename)
            import subprocess
            subprocess.Popen((filename,), shell=True)

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

    def _build_report(self):
        try:

            return build_document(PDFContent(Filters(self)))

        except ValueError as ex:
            raise












