
from PyQt5.QtWidgets import QDialog

from ui_partner_or_agent_form import Ui_Dialog

from db import SaleInvoice, SaleProforma

from whatsapp import send_whatsapp


def get_names(proforma_or_invoice):

    if isinstance(proforma_or_invoice, SaleInvoice):
        proforma = proforma_or_invoice.proformas[0]
        return proforma.partner_name, proforma.agent.fiscal_name

    elif isinstance(proforma_or_invoice, SaleProforma):
        return proforma_or_invoice.partner_name, proforma_or_invoice.agent.fiscal_name


class Dialog(Ui_Dialog, QDialog):

    def __init__(self, parent, proforma_or_invoice):
        super().__init__(parent)
        self.setupUi(self)

        partner, agent = get_names(proforma_or_invoice)

        self.partner.setText(partner)
        self.agent.setText(agent)


