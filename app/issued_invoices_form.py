
from ui_issued_invoices_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from issued_invoices_pdf_builder import build_document
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


class PDFContent:

    __slots__ = ('from_', 'to', 'registers', 'created_on')

    def __init__(self, filters: Filters):
        self.from_ = filters.from_
        self.to = filters.to
        self.created_on = datetime.now()

        self.registers = [
            (
                invoice.doc_repr,
                invoice.date.strftime('%d/%m/%Y'),
                invoice.partner_name, invoice.agent,
                invoice.financial_status_string,
                invoice.subtotal,
                invoice.tax,
                invoice.total_debt,
                'EUR' if invoice.proformas[0].eur_currency else 'USD'
            )

            for invoice in self._build_query(filters)
        ]

        for register in self.registers:
            print(register)

    def _build_query(self, filters):
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
        # subprocess bla bla bla
        pdf_document = self._build_report()



    def export_handler(self):

        # Ask filename with pdf filters

        file_path = utils.get_file_path(self, capdf_filter=True)

        print(file_path)

        # pdf_document = self._build_report()


    def _build_report(self):
        try:
            return build_document(PDFContent(Filters(self)))
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))












