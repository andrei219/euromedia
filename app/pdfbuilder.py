# coding: utf8

from itertools import chain, cycle

from fpdf import FPDF

from db import SaleInvoice
from db import SaleProforma
from db import PurchaseProforma
from db import SaleProforma

# CONSTANTS:

LOGO_RELATIVE_PATH = r'.\app\icons\docus_logo.png'
LOGO_BANK_1 = r'.\app\icons\deutsche_logo.png'
LOGO_BANK_2 = r'.\app\icons\wise_logo.png'

BUYER_BASE = (21.99, 38.1)
SUPPLIER_BASE = (21.99, 78.08)
DELIVERY_ADDRESS_BASE = (127.5, 78.08)
TABLE_LEFT_INCRMENT = 25
TABLE_RIGHT_INCREMENT = 30
TABLE_DOWN_INCREMENT = 5
TABLE_START = (135.11, 35.75)
ITEM_POSITION = (15.07, 114.89)
DESC_POSITION = (70.13, 114.89)
QTY_POSITION = (140.24, 114.89)
UNIT_POSITION = (153.56, 114.89)
TOTAL_POSITION = (182.68, 114.89)
LINE_HEADER_START = (13.5, 118.77)
LINE_HEADER_END = (210 - 13.5, 118.77)
LINE_WIDTH = 183
INNER_LINE_START = (19.55, 123.3)
INNER_LINE_Y_INCREMENT = 5.52
INNER_LINE_X_INCREMENTS = cycle([12.55, 100.14, 13.73, 24.83, 25.21])

TOTAL_EXCL_VAT_X_POSITION = 130.89
X_INCREMENT = 30
Y_INCREMENT = 4.61
LAST_Y_INCREMENT = 9
TOTALS_ADDITIONAL_Y_INCREMENT = 181.68 - 168.6
ADDITIONAL_TERMS_Y_INCREMENT = 195.09 - 181.68
CLOSING_LINE_TOTALS_Y_INCREMENT = 5
LAST_TOTAL_ADDITIONAL_Y_INCREMENT = 15
LEFT_MARGIN = 13.5
ADDITIONAL_TEXT_TERM_INCREMENT = 10

CONDITIONS_BETWEEN_Y_INCREMENT = 2.5
CONDITIONS_Y_INCREMENT = 2.5
VERTICAL_LINE_X_POSITION = 120
VERTICAL_LINE_Y_INCREMENT = 20
BANK1_LOGO_X_POSITION = 27
BANK2_LOGO_X_POSITION = 128
BANK_LOGO_Y_INCREMENT = 10
BANK_TEXT_Y_INCREMENT = 2.5
BANK1_TEXT_X_POSITION = 64
BANK2_TEXT_X_POSITION = 153
RMA_START_X_POSITION = 125
BANK_TEXT_Y_CONDITION_RELATIVE_INCREMENT = 9

import utils
from importlib import reload

utils = reload(utils)


# Deberiamos hacer una superclase que contenga attsetters 
# que implemente esta conversion
# asi no tendriamos que llamar 10 VECES la misma funcion
# pero no estamos pa mas dolores de cabeza
def dot_comma_number_repr(str_number):
    count = str_number.count(',')
    return str_number.replace('.', ',').replace(',', '.', count)


class LinePDFRepr:

    def __iter__(self):
        return iter(map(str, (self.description, self.quantity, self.price, self.total)))


class PurchaseLinePDFRepr(LinePDFRepr):

    def __init__(self, line):

        self.description = line.description or \
                           utils.description_id_map.inverse.get(line.item_id)

        if line.condition:
            self.description += f', {line.condition}'
        if line.spec:
            self.description += f', {line.spec}'

        self.quantity = line.quantity
        self.total = '{:,.2f}'.format(round(line.price * line.quantity, 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))
        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)


class SaleLinePDFRepr(LinePDFRepr):

    def __init__(self, lines):
        if len(lines) == 1 and {None} == {line.item_id for line in lines}:
            line = lines[0]
            self.description = line.description
            self.quantity = line.quantity
            self.price = line.price
            self.total = line.quantity * line.price
            self.total = '{:,.2f}'.format(round(self.price * self.quantity, 2))
            self.price = '{:,.2f}'.format(round(self.price, 2))
            self.total = dot_comma_number_repr(self.total)
            self.price = dot_comma_number_repr(self.price)

        else:
            self.description = utils.build_description(lines)
            self.quantity = sum(line.quantity for line in lines)
            self.price = lines[0].price
            self.total = '{:,.2f}'.format(round(self.price * self.quantity, 2))
            self.price = '{:,.2f}'.format(round(self.price, 2))
            self.total = dot_comma_number_repr(self.total)
            self.price = dot_comma_number_repr(self.price)

            showing_condition = lines[0].showing_condition
            condition = showing_condition or lines[0].condition
            condition += ' Cond.'

            # if len({line.condition for line in lines}) > 1:
            #     condition = 'Mix Cond.'

            self.description += ', ' + condition

            if not lines[0].ignore_spec:
                diff_specs = {line.spec for line in lines}
                if len(diff_specs) > 1:
                    spec = 'Mix'
                else:
                    spec = lines[0].spec

                self.description += ', ' + spec + ' Spec.'


class CreditLinePDFRepr(LinePDFRepr):

    def __init__(self, line):
        self.description = utils.description_id_map.inverse.get(line.item_id)
        self.description += f', {line.condition} condt.'
        self.description += f', {line.spec} spec.'

        self.total = '{:,.2f}'.format(round(line.price * line.quantity, 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))
        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)

        self.quantity = line.quantity


class AdvancedSaleLinePDFRepr(LinePDFRepr):

    def __init__(self, line):
        self.description = line.free_description or \
                           line.mixed_description or utils.description_id_map.inverse.get(line.item_id)

        if line.condition or line.showing_condition:
            self.description += f', {line.showing_condition or line.condition} condt.'

        if line.spec and not line.ignore_spec:
            self.description += f', {line.spec} spec.'

        self.quantity = line.quantity

        self.total = '{:,.2f}'.format(round(line.price * line.quantity, 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))
        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)


class LinesPDFRepr:

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        return len(self.lines)


class SaleLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = [
            SaleLinePDFRepr([l for l in lines if l.mix_id == mix_id])
            for mix_id in list(dict.fromkeys([line.mix_id for line in lines]))
        ]

class CreditLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(CreditLinePDFRepr, lines))

class PurchaseLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(PurchaseLinePDFRepr, lines))


class AdvancedLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(AdvancedSaleLinePDFRepr, lines))


class We:
    def __init__(self):
        self.fiscal_name = 'Euromedia Investment Group, S.L.'
        self.billing_line1 = 'Calle Camino Real Nº22'
        self.billing_line2 = 'Local Bajo Izq.'
        self.billing_city = 'Torrente'
        self.billing_postcode = '46900'
        self.billing_state = 'Valencia'
        self.billing_country = 'Spain'
        self.registerd = 'Registered on 22/03/2016'
        self.fiscal_number = 'B98815608'
        self.vat = 'VAT Nº:ESB98815608'

        self.shipping_line1 = 'Calle Camino Real Nº22'
        self.shipping_line2 = 'Local Bajo Izq.'
        self.shipping_city = 'Torrente'
        self.shipping_postcode = '46900'
        self.shipping_state = 'Valencia'
        self.shipping_country = 'Spain'

        self.phone = '+34 633 333 973'


class TableData:

    def __init__(self, document, *, is_invoice):
        self.Date = document.invoice.date.strftime('%d-%m-%Y') \
            if is_invoice else document.date.strftime('%d-%m-%Y')
        self.PO = str(document.invoice.type) + '-' + str(document.invoice.number). \
            zfill(6) if is_invoice else str(document.type) + '-' + str(document.number).zfill(6)
        self.Agent = document.agent.fiscal_name.split()[0]
        self.Incoterms = document.incoterm
        # self.Delivery_Date = document.invoice.eta.strftime('%d-%m-%Y') if is_invoice \
        #     else document.eta.strftime('%d-%m-%Y')

        self.External_Doc = document.external

        self.Currency = 'EUR' if document.eur_currency else \
            'USD '

    def __iter__(self):
        return iter(self.__dict__.items())


class TotalsData:

    def __init__(self, document):
        try:
            lines = document.advanced_lines or document.lines
        except AttributeError:
            lines = document.lines
        #
        # self.Total_excl_VAT = sum(line.price * line.quantity for line in lines)
        # self.Total_VAT = sum(line.quantity * line.price * line.tax / 100 for line in lines)
        # self.Total = '{:,.2f}'.format(round(self.Total_excl_VAT + self.Total_VAT, 2))

        self.Total_excl_VAT = document.subtotal
        self.Total_VAT = document.tax
        self.Total = '{:,.2f}'.format(round(self.Total_excl_VAT + self.Total_VAT, 2))


        self.Total_excl_VAT = '{:,.2f}'.format(round(self.Total_excl_VAT, 2))
        self.Total_VAT = '{:,.2f}'.format(round(self.Total_VAT, 2))

        self.Total = dot_comma_number_repr(self.Total)
        self.Total_excl_VAT = dot_comma_number_repr(self.Total_excl_VAT)
        self.Total_VAT = dot_comma_number_repr(self.Total_VAT)

        # self.Shipping = dot_comma_number_repr(self.Shipping)

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__.items())


class PDF(FPDF):

    def __init__(self, document, *, is_invoice):
        self.last_condition_y_position = None
        global utils
        from importlib import reload
        utils = reload(utils)
        super().__init__()
        self.is_invoice = is_invoice
        self.document = document
        self.resolve_header_and_lines_repr(document, is_invoice)
        self.we = We()
        self.table_data = TableData(document, is_invoice=is_invoice)
        self.totals_data = TotalsData(document)

        self.conditions = [
            '1 - All good remain property of Euromedia Investment Group, S.L. until payment is received in full.',
            '2 - Goods will be released only after full amount is received by Euromedia Investment Group, S.L.',
            '3 - Euromedia Investment Group, S.L. will not be liable of any delay incurred by airlines, freight',
            '      companies or customs department.',
            '4 - The used devices have 30 natural days functional warranty from the delivery date.',
            '5 - The used devices have 72 hours grading warranty from delivery date.',
            '6 - For Invoice Enquires: administracion@euromediagroup.es'
        ]

        self.rma_conditions = [
            '                          RMA CONDITIONS               ',
            '1 - For RMA Enquires: rma@euromediagroup.es',
            '2 - RMA requests will be answered within 48 hours from Monday to Friday.',
            '3 - Before return any device, you must have our approval for each one.',
            '4 - Approved devices must be sent back within 5 days.'
        ]

    def resolve_header_and_lines_repr(self, document, is_invoice):
        from db import SaleProforma, PurchaseProforma
        if type(document) == SaleProforma:
            self.we_buy = False

            if document.lines:
                self.lines = SaleLinesPDFRepr(document.lines)
            elif document.advanced_lines:
                self.lines = AdvancedLinesPDFRepr(document.advanced_lines)
            elif document.credit_note_lines:
                self.lines = CreditLinesPDFRepr(document.credit_note_lines)

            if not is_invoice:
                self.doc_header = 'SALE ORDER'
            else:
                self.doc_header = 'SALE INVOICE'

        elif type(document) == PurchaseProforma:
            self.lines = PurchaseLinesPDFRepr(document.lines)
            self.we_buy = True
            if not is_invoice:
                self.doc_header = 'PURCHASE ORDER'
            else:
                self.doc_header = 'PURCHASE INVOICE'

    def header(self, print_lines_header=True):
        self.set_xy(18.75, 13.53)
        self.image(LOGO_RELATIVE_PATH, w=70, h=18.2)
        self.set_font('Arial', 'B', 18)
        self.set_xy(127.5, 13.35)
        self.cell(68, 17, self.doc_header, 1, 0, 'C')

        self.print_buyer()
        self.print_supplier()
        self.print_delivery_address()
        self.print_table()
        self.print_desc_header(print_lines_header=print_lines_header)
        # After printing header, restore y 
        self.set_y(INNER_LINE_START[1])

    @property
    def totals_y_increment(self):
        return CLOSING_LINE_TOTALS_Y_INCREMENT + \
               Y_INCREMENT * (len(self.totals_data) - 1) + \
               LAST_Y_INCREMENT + LAST_TOTAL_ADDITIONAL_Y_INCREMENT

    @property
    def totals_additionals_y_increment(self):
        return TOTALS_ADDITIONAL_Y_INCREMENT + ADDITIONAL_TERMS_Y_INCREMENT

    @property
    def terms_y_increment(self):
        return Y_INCREMENT * 6 + 40

    @property
    def conditions_y_increment(self):
        return CONDITIONS_Y_INCREMENT * len(self.conditions) + 10

    def print_totals(self, with_line=True):

        if with_line:
            self.print_line()
            self.y = self.y + CLOSING_LINE_TOTALS_Y_INCREMENT

        len_items = len(self.totals_data)
        first = True
        for i, item in enumerate(self.totals_data):
            self.set_x(TOTAL_EXCL_VAT_X_POSITION)
            key, value = item
            if len_items - 1 == i:
                self.set_font('Arial', 'B', size=12)
            else:
                self.set_font('Arial', size=10)
            text = key.replace('_', ' ') + ':'
            if first:
                first = False
                spliited = text.split()
                text = spliited[0] + ' ' + spliited[1] + '. ' + spliited[2]
            self.cell(w=X_INCREMENT, h=Y_INCREMENT, align='R', txt=text)
            self.cell(w=X_INCREMENT, h=Y_INCREMENT, align='R', txt=str(value))

            if len_items - i == 2:
                self.set_y(self.get_y() + LAST_Y_INCREMENT)
            else:
                self.set_y(self.get_y() + Y_INCREMENT)

        self.y = self.y + LAST_TOTAL_ADDITIONAL_Y_INCREMENT
        self.x = LEFT_MARGIN

    def print_additional(self):
        self.y += 10
        self.set_font('Arial', 'B', size=10)

        self.cell(0, txt='Comment:')
        self.x = LEFT_MARGIN + 4
        self.y += Y_INCREMENT
        self.set_font('Arial', size=8)
        self.cell(0, txt=self.document.note)
        self.y += ADDITIONAL_TEXT_TERM_INCREMENT

    def print_vertical_line(self):

        x1 = x2 = VERTICAL_LINE_X_POSITION
        y2 = self.y
        y1 = y2 - VERTICAL_LINE_Y_INCREMENT

        self.line(x1, y1, x2, y2)

    def print_terms(self):
        self.x = LEFT_MARGIN
        self.y += 5

        name, doc_type = None, None

        if type(self.document) == SaleProforma and self.is_invoice:
            name = 'Factura'
            doc_type = self.document.invoice.type
        elif type(self.document) == SaleProforma and not self.is_invoice:
            name = 'Proforma'
            doc_type = self.document.type
        elif type(self.document) == PurchaseProforma and not self.is_invoice:
            name = 'Proforma'
            doc_type = self.document.type
        elif type(self.document) == PurchaseProforma and self.is_invoice:
            name = 'Factura'
            doc_type = self.document.invoice.type

        title = 'General Terms and Conditions:'

        terms_dictionary = {
            1: [],
            2: [
                f'{name} sin IVA por Inversión del Sujeto Pasivo.',
                'Art. 84.1.2º Ley 37/1992 del IVA.'
            ],
            3: [
                'Good for Export, VAT Exempt.'
            ],
            4: [
                'VAT Exempt, Intro-EU Community Supply.'
            ],
            5: [
                f'{name} sujeta al Régimen Especial de Bienes Usados (R.E.B.U.).'
            ],
            6: [
                'VAT Terms: Goods sold on the Margin VAT Scheme.'
            ]
        }

        terms = terms_dictionary[doc_type]
        self.set_font('Arial', style='B', size=10)
        self.cell(0, txt=title)
        self.x = LEFT_MARGIN + 4
        self.y += Y_INCREMENT
        self.set_font('Arial', size=8)
        for term in terms:
            self.cell(0, txt=term)
            self.x = LEFT_MARGIN + 4
            self.y += Y_INCREMENT

        if type(self.document) == SaleProforma:
            self.print_conditions()

    def print_line(self):
        x1, x2 = 13.5, 210 - 13.5
        y1 = y2 = self.y
        self.line(x1, y1, x2, y2)

    def print_conditions(self):
        self.x = LEFT_MARGIN
        self.y += CONDITIONS_Y_INCREMENT

        self.x = LEFT_MARGIN + 4
        self.y += Y_INCREMENT
        self.set_font('Arial', size=6)
        for condition in self.conditions:
            self.cell(0, txt=condition)
            self.x = LEFT_MARGIN + 4
            self.y += CONDITIONS_BETWEEN_Y_INCREMENT

        self.last_condition_y_position = self.y

        self.print_vertical_line()

        self.x = RMA_START_X_POSITION
        self.y = self.y - VERTICAL_LINE_Y_INCREMENT
        self.set_font('Arial', size=7, style='b')
        self.cell(0, txt='                               RMA CONDITIONS               ')
        self.set_font('Arial', size=6)
        self.y += 2

        for condition in self.rma_conditions:
            self.cell(0, txt=condition)
            self.x = RMA_START_X_POSITION
            self.y += CONDITIONS_BETWEEN_Y_INCREMENT

        self.print_bank()

    def print_bank(self):
        self.x = BANK1_LOGO_X_POSITION
        self.y = self.last_condition_y_position + BANK_LOGO_Y_INCREMENT
        self.image(LOGO_BANK_1, w=32.3, h=4.91)
        self.x = BANK2_LOGO_X_POSITION
        self.y = self.last_condition_y_position + BANK_LOGO_Y_INCREMENT
        self.image(LOGO_BANK_2, w=20.42, h=4.91)

        y_absolute_position = self.y - -3

        self.x = BANK1_TEXT_X_POSITION

        self.y = self.last_condition_y_position + BANK_TEXT_Y_CONDITION_RELATIVE_INCREMENT

        self.set_font('Arial', size=7, style='b')
        for t in [
            'Bank: Deutsche Bank, S.A.E.',
            'Currency: EUR',
            'IBAN: ES63 0019 0511 4840 1017 6011',
            'SWIFT/BIC: DEUTESBBXXX'
        ]:
            self.x = BANK1_TEXT_X_POSITION
            self.cell(0, txt=t)
            self.y += BANK_TEXT_Y_INCREMENT

        self.y = self.last_condition_y_position + BANK_TEXT_Y_CONDITION_RELATIVE_INCREMENT

        for t in [
            'Bank: Wise',
            'Currency: USD',
            'Account Nº: 8310622371',
            'SWIFT/BIC: CMFGUS33'
        ]:
            self.x = BANK2_TEXT_X_POSITION
            self.cell(0, txt=t)
            self.y += BANK_TEXT_Y_INCREMENT

    def print_footer(self):

        if self.y + self.totals_y_increment < self.page_break_trigger:
            self.print_totals()
            if self.y + self.totals_additionals_y_increment < self.page_break_trigger:
                self.print_additional()

                if self.y + self.terms_y_increment < self.page_break_trigger:
                    self.print_terms()

                else:
                    self.add_page(print_lines_header=False)
                    self.print_terms()
            else:
                self.add_page(print_lines_header=False)
                self.print_additional()
                self.print_terms()

        else:
            self.add_page(print_lines_header=False)
            self.print_totals(with_line=False)
            self.print_additional()
            self.print_terms()

    def print_buyer(self):
        partner = self.we if self.we_buy else self.document.partner
        x, y = BUYER_BASE
        self.print_helper(partner, x, y, header='Buyer:')

    def print_supplier(self):
        partner = self.document.partner if self.we_buy else self.we
        x, y = SUPPLIER_BASE
        self.print_helper(partner, x, y, header='Supplier:')

    def print_delivery_address(self):
        partner = self.we if self.we_buy else self.document.partner
        x, y = DELIVERY_ADDRESS_BASE
        self.print_helper(partner, x, y, header='DELIVERY ADDRESS:')

    def print_helper(self, partner, x, y, *, header):
        self.set_xy(x, y)
        self.set_font('Arial', 'B', size=12)
        self.cell(0, txt=header)
        self.set_font('Arial', size=10)

        if header == 'DELIVERY ADDRESS:':
            prefix = 'shipping_'
        else:
            prefix = 'billing_'
        for element in [
            partner.fiscal_name,
            getattr(partner, prefix + 'line1'),
            getattr(partner, prefix + 'line2'),
            # getattr(partner, prefix + 'line3'),
            ' '.join([getattr(partner, prefix + 'postcode'), getattr(partner, prefix + 'city'),
                      getattr(partner, prefix + 'state')]),

            getattr(partner, prefix + 'country'),
            'VAT Nº: ' + partner.fiscal_number
        ]:
            y += 4
            self.set_xy(x, y)
            self.cell(0, txt=element)

    def print_table(self):
        x, y = TABLE_START
        self.set_xy(x, y)
        for key, value in chain(self.table_data, [('Page', str(self.page_no()) + ' of {nb}')]):
            text = key.replace('_', ' ') + ':'
            self.cell(w=TABLE_LEFT_INCRMENT, h=TABLE_DOWN_INCREMENT, border=True, align='R', txt=text)
            self.set_x(x + TABLE_LEFT_INCRMENT)
            self.cell(w=TABLE_RIGHT_INCREMENT, h=TABLE_DOWN_INCREMENT, align='C', border=True, txt=value)
            y += TABLE_DOWN_INCREMENT
            self.set_xy(x, y)

    def print_desc_header(self, print_lines_header=False):
        self.header_printed = False
        if print_lines_header:
            self.header_printed = True
            for text, position in [
                ('Item #', ITEM_POSITION),
                ('Description', DESC_POSITION),
                ('Qty.', QTY_POSITION),
                ('Unit Price', UNIT_POSITION),
                ('Total', TOTAL_POSITION)
            ]:
                self.set_xy(*position)
                self.cell(0, txt=text)

        self.set_xy(*LINE_HEADER_START)
        self.line(*LINE_HEADER_START, *LINE_HEADER_END)

    def print_body(self):
        self.append_lines()

    def append_lines(self):
        x_start, self.y_start = INNER_LINE_START
        print_lines_header = False
        self.set_xy(x_start, self.y_start)
        lines_total = len(self.lines)
        self.set_font('Arial', size=9)
        for line_number, line in enumerate(self.lines):
            x = x_start
            for i, element in enumerate(chain([str(line_number + 1)], line), 0):
                increment = next(INNER_LINE_X_INCREMENTS)
                print_lines_header = line_number < lines_total
                self.cell(increment, txt=element, align='R' if i >= 2 else 'L', caller=self, \
                          print_lines_header=print_lines_header)
                x += increment
                self.set_x(x)

            self.y_start += INNER_LINE_Y_INCREMENT
            self.set_xy(x_start, self.y_start)


def build_document(document, *, is_invoice):
    pdf = PDF(document, is_invoice=is_invoice)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 10)
    pdf.add_page()
    pdf.print_body()
    pdf.print_footer()
    return pdf


if __name__ == '__main__':
    from db import SaleProforma, session, PurchaseProforma

    sale = session.query(SaleProforma).first()
    purchase = session.query(PurchaseProforma).first()

    pdf = build_document(sale, is_invoice=False)

    pdf.output('test.pdf')

    # from itertools import product

    # for doc, is_invoice in product(
    #     [purchase, sale], 
    #     [False ,True]
    # ):     
    #     build_document(doc, is_invoice=is_invoice)
