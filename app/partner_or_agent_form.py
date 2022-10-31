
from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_partner_or_agent_form import Ui_Dialog

from db import SaleInvoice, SaleProforma

from whatsapp import send_whatsapp
from utils import get_whatsapp_phone_number

from pdfbuilder import build_document
from whatsapp import send_whatsapp
from models import export_invoices_sales_excel

import os


class Dialog(Ui_Dialog, QDialog):

    def __init__(self, parent, proforma_or_invoice):
        super().__init__(parent)
        self.setupUi(self)
        self.proforma_or_invoice = proforma_or_invoice

        self.set_names(proforma_or_invoice)

        self.send.clicked.connect(self.send_clicked)

    def set_names(self, proforma_or_invoice):
        if isinstance(proforma_or_invoice, SaleInvoice):
            proforma = proforma_or_invoice.proformas[0]
        else:
            proforma = proforma_or_invoice

        self.partner.setText(proforma.partner_name)
        self.agent.setText(proforma.agent.fiscal_name)

    def send_clicked(self):
        excel_path = None
        try:
            phone = get_whatsapp_phone_number(
                self.proforma_or_invoice,
                partner=self.partner.isChecked()
            )

        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            return

        temp_dir = os.path.abspath(os.path.join(os.curdir, 'temp'))
        pdf_document = build_document(self.proforma_or_invoice)

        doc_repr = self.proforma_or_invoice.doc_repr
        pdf_path = os.path.join(temp_dir, doc_repr + '.pdf')

        pdf_document.output(pdf_path)

        if isinstance(self.proforma_or_invoice, SaleInvoice):
            excel_path = os.path.join(temp_dir, 'series ' + doc_repr + '.xlsx')
            export_invoices_sales_excel(self.proforma_or_invoice, excel_path)

        try:
            send_whatsapp(pdf_path, phone, excel=excel_path)

        except:
            raise
