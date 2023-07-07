# coding: utf8
import os
from itertools import chain, cycle

import db
from fpdf import FPDF

from db import SaleInvoice
from db import SaleProforma
from db import PurchaseProforma
from db import PurchaseInvoice
import utils
from importlib import reload

# CONSTANTS:

# TODO: Parameterize for different databases


from collections import defaultdict

d = defaultdict(list)

d['euromedia'].append(r'.\app\icons\docus_logo.png')
d['euromedia'].append(r'.\app\icons\sabadell_logo.png')
d['euromedia'].append(r'.\app\icons\wise_logo.png')

d['capital'].append(r'.\app\icons\docus_logo.png')
d['capital'].append(r'.\app\icons\deutsche_logo.png')
d['capital'].append(r'.\app\icons\wise_logo.png')

d['realstate'].append(r'.\app\icons\docus_logo.png')
d['realstate'].append(r'.\app\icons\deutsche_logo.png')
d['realstate'].append(r'.\app\icons\wise_logo.png')

d['mobify'].append(r'.\app\icons\docus_logo.png')
d['mobify'].append(r'.\app\icons\deutsche_logo.png')
d['mobify'].append(r'.\app\icons\wise_logo.png')


logos = d[os.environ['APP_DATABASE']]

# When working with database branch, no logos are found for testing:
if not logos:
    logos = d['euromedia']

name2db_map = {
    'Euromedia Investment Group, S.L.': 'euromedia',
    'AT Capital, Ltd': 'capital',
    'Euromedia Real Estate, S.L.': 'realstate',
    'Mobify Ltd': 'mobify',
}
''' Declare the same map above but with the values reverse'''
db2name_map = {v: k for k, v in name2db_map.items()}

db2email_map = {
    'euromedia': 'administracion@euromediagroup.es',
    'capital': 'administracion@atcapital.es',
    'realstate': 'admin@realstate.es',
    'mobify': 'admin@mobify.com'
}

db2rma_email_map = {
    'euromedia': 'rma@euromediagroup.es',
    'capital': 'rma@atcapital.com',
    'realstate': 'rma@realstate.com',
    'mobify': 'rma@mobify.com'
}

def get_conditions():
    return [
        f'1 - All good remain property of {db.db2name_map.get(os.environ["APP_DATABASE"], "x")} until payment is received in full.',

        f'2 - Goods will be released only after full amount is received by {db.db2name_map.get(os.environ["APP_DATABASE"], "x")}',
        f'{db.db2name_map.get(os.environ["APP_DATABASE"], "")} will not be liable of any delay incurred by airlines, freight',
        f'      companies or customs department.',
        f'4 - The used devices have 30 natural days functional warranty from the delivery date.',
        f'5 - The used devices have 72 hours grading warranty from delivery date.',
        f'6 - For Invoice Enquires: {db.db2name_map.get(os.environ["APP_DATABASE"], "x")}',
]

def get_rma_conditions():
    return [
        '                          RMA CONDITIONS               ',
        f'1 - For RMA Enquires: {db2rma_email_map.get(os.environ["APP_DATABASE"], "x")}',
        '2 - RMA requests will be answered within 48 hours from Monday to Friday.',
        '3 - Before return any device, you must have our approval for each one.',
        '4 - Approved devices must be sent back within 5 days.'
    ]


def get_logo_bank_1():
    return logos[1]


def get_logo_bank_2():
    return logos[2]

def get_logo():
    return logos[0]

BUYER_BASE = (21.99, 38.1)
SUPPLIER_BASE = (21.99, 78.08)
DELIVERY_ADDRESS_BASE = (127.5, 78.08)
TABLE_LEFT_INCRMENT = 25
TABLE_RIGHT_INCREMENT = 30
TABLE_DOWN_INCREMENT = 5
TABLE_START = (135.11, 35.75)
ITEM_POSITION = (15.07, 114.89)
DESC_POSITION = (70.13, 114.89)
QTY_POSITION = (135.00, 114.89)
UNIT_POSITION = (152.00, 114.89)
TAX_POSITION = (168.00, 114.89)
TOTAL_POSITION = (184.70, 114.89)
LINE_HEADER_START = (13.5, 118.77)
LINE_HEADER_END = (210 - 13.5, 118.77)
LINE_WIDTH = 183
INNER_LINE_START = (19.55, 123.3)
INNER_LINE_Y_INCREMENT = 5.52
INNER_LINE_X_INCREMENTS = cycle([12.55, 94.3, 16, 18, 16, 19])

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
BANK1_TEXT_X_POSITION = 55
BANK2_TEXT_X_POSITION = 153
RMA_START_X_POSITION = 125
BANK_TEXT_Y_CONDITION_RELATIVE_INCREMENT = 9

utils = reload(utils)

pdf = FPDF()
pdf.set_font('Arial', size=9)

import db

def text_exceeds(text, length=95):
    return pdf.get_string_width(text) > length


def get_space_position(text, length=95):
    positions = [position for position, char in enumerate(text) if char == ' ']
    for i in range(len(positions)):
        position_prev = positions[i]
        try:
            position = positions[i + 1]
        except IndexError:
            return position_prev
        if pdf.get_string_width(text[:position_prev]) < length < pdf.get_string_width(text[:position]):
            return position_prev


def dot_comma_number_repr(str_number):
    count = str_number.count(',')
    return str_number.replace('.', ',').replace(',', '.', count)


class LinePDFRepr:

    def __init__(self):
        self.number = ''

    def __iter__(self):
        return iter(map(str, (self.number, self.description, self.quantity, self.price, self.tax, self.total)))

    @classmethod
    def fake(cls, description, space_position):
        self = cls()
        self.description = description[:space_position]
        self.quantity = ''
        self.price = ''
        self.tax = ''
        self.total = ''
        return self


class PurchaseLinePDFRepr(LinePDFRepr):

    def __init__(self, line):

        super().__init__()

        self.description = line.description or \
                           utils.description_id_map.inverse.get(line.item_id)

        if line.condition:
            self.description += f', {line.condition}'
        if line.spec:
            self.description += f', {line.spec}'

        self.quantity = line.quantity
        self.total = '{:,.2f}'.format(round(line.price * line.quantity * ( 1 + line.tax /100), 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))

        self.tax = str(line.tax) + '%'

        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)


class SaleLinePDFRepr(LinePDFRepr):

    def __init__(self, lines):

        super().__init__()

        if len(lines) == 1 and {None} == {line.item_id for line in lines}: # check free line
            line = lines[0]
            self.description = line.description
            self.quantity = line.quantity
            self.price = line.price
            self.total = line.quantity * line.price
            self.total = '{:,.2f}'.format(round(self.price * self.quantity * (1 + line.tax/100), 2))
            self.price = '{:,.2f}'.format(round(self.price, 2))
            self.tax = str(line.tax) + '%'
            self.total = dot_comma_number_repr(self.total)
            self.price = dot_comma_number_repr(self.price)

        else:
            self.description = utils.build_description(lines)
            self.quantity = sum(line.quantity for line in lines)
            self.price = lines[0].price
            self.total = '{:,.2f}'.format(round(self.price * self.quantity * (1 + lines[0].tax /100) , 2))
            self.price = '{:,.2f}'.format(round(self.price, 2))
            self.tax = str(lines[0].tax) + '%'
            self.total = dot_comma_number_repr(self.total)
            self.price = dot_comma_number_repr(self.price)

            if not lines[0].showing_condition:
                diff_conditions = {line.condition for line in lines}
                if len(diff_conditions) > 1:
                    condition = 'Mix'
                else:
                    condition = lines[0].condition
            else:
                condition = lines[0].showing_condition

            self.description += ', ' + condition + ' Condt.'

            if not lines[0].ignore_spec:
                diff_specs = {line.spec for line in lines}
                if len(diff_specs) > 1:
                    spec = 'Mix'
                else:
                    spec = lines[0].spec

                self.description += ', ' + spec + ' Spec.'


class CreditLinePDFRepr(LinePDFRepr):

    def __init__(self, line):
        super().__init__()
        self.description = utils.description_id_map.inverse.get(line.item_id)
        self.description += f', {line.public_condition or line.condition} condt.'
        self.description += f', {line.spec} spec.'

        self.total = '{:,.2f}'.format(round(line.price * line.quantity * (1 + line.tax / 100), 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))
        self.tax = str(line.tax) + '%'
        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)

        self.quantity = line.quantity


class AdvancedSaleLinePDFRepr(LinePDFRepr):

    def __init__(self, line):
        super().__init__()
        self.description = line.free_description or \
                           line.mixed_description or utils.description_id_map.inverse.get(line.item_id)

        if line.condition or line.showing_condition:
            self.description += f', {line.showing_condition or line.condition} condt.'

        if line.spec and not line.ignore_spec:
            self.description += f', {line.spec} spec.'

        self.quantity = line.quantity

        self.tax = str(line.tax) + '%'

        self.total = '{:,.2f}'.format(round(line.price * line.quantity * ( 1 + line.tax /100), 2))
        self.price = '{:,.2f}'.format(round(line.price, 2))
        self.total = dot_comma_number_repr(self.total)
        self.price = dot_comma_number_repr(self.price)


class LinesPDFRepr:

    def __iter__(self):
        return iter([(line.number, line) for line in self.lines])

    def __len__(self):
        return len(self.lines)

    def add_counter(self):
        indexes = [i for i, line in enumerate(self.lines) if text_exceeds(line.description)]
        for index in indexes[::-1]:
            line = self.lines[index]
            space_position = get_space_position(line.description)
            self.lines.insert(index, LinePDFRepr.fake(line.description, space_position))
            line.description = line.description[space_position:].strip()

        start = 1
        prev = self.lines[0]
        for i, actual_line in enumerate(self.lines):
            if i == 0:
                actual_line.number = start
            else:
                if not (prev.price == '' and actual_line.price != ''):
                    start += 1
                    actual_line.number = start
            prev = actual_line


class SaleLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = [
            SaleLinePDFRepr([l for l in lines if l.mix_id == mix_id])
            for mix_id in list(dict.fromkeys([line.mix_id for line in lines]))
        ]
        self.add_counter()


class CreditLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(CreditLinePDFRepr, lines))
        self.add_counter()


class PurchaseLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(PurchaseLinePDFRepr, lines))
        self.add_counter()


class AdvancedLinesPDFRepr(LinesPDFRepr):

    def __init__(self, lines):
        self.lines = list(map(AdvancedSaleLinePDFRepr, lines))
        self.add_counter()


class MixedUPLinesPDFRepr(LinesPDFRepr):

    def __init__(self, objects: list):
        self.lines = []
        for object in objects:
            self.lines.extend(object.lines)
        self.add_counter()

class We:

    def __init__(self):
        self.fiscal_name = 'Euromedia Investment Group, S.L.'
        self.billing_line1 = 'Calle Camino Real Nº22'
        self.billing_line2 = 'Local Bajo Izq.'
        self.billing_city = 'Torrente'
        self.billing_postcode = '46900'
        self.billing_state = 'Valencia'
        self.billing_country = 'Spain'
        self.registered = 'Registered on 22/03/2016'
        self.fiscal_number = 'B98815608'
        self.vat = 'VAT Nº:ESB98815608'

        self.shipping_line1 = 'Calle G Nº22'
        self.shipping_line2 = 'Pol. Ind. Toll La Alberca'
        self.shipping_city = 'Torrente'
        self.shipping_postcode = '46900'
        self.shipping_state = 'Valencia'
        self.shipping_country = 'Spain'

        self.phone = '+34 633 333 973'

    @classmethod
    def from_actual_db(cls):
        s = 'TEST FAILED'
        o = cls()
        if os.environ["APP_DATABASE"].lower() == 'euromedia':
            return o
        elif os.environ["APP_DATABASE"].lower() == 'capital':
            s = 'CAPITALTEST'
        elif os.environ['APP_DATABASE'].lower() == 'mobify':
            s = 'MOBIFYTEST'
        elif os.environ['APP_DATABASE'].lower() == 'realstate':
            s = 'REALSTATETEST'

        o.fiscal_name = s
        o.billing_line1 = s
        o.billing_line2 = s
        o.billing_city = s
        o.billing_postcode = s
        o.billing_state = s
        o.billing_country = s
        o.registered = s
        o.fiscal_number = s
        o.vat = s

        o.shipping_line1 = s
        o.shipping_line2 = s
        o.shipping_city = s
        o.shipping_postcode = s
        o.shipping_state = s
        o.shipping_country = s
        o.phone = s

        return o


class TableData:

    def __init__(self, document):

        if isinstance(document, (SaleInvoice, PurchaseInvoice)):
            self.origin_proformas = document.origin_proformas
            proforma = document.proformas[0]
            self.Date = document.date.strftime('%d-%m-%Y')
            self.Document_No = document.doc_repr
            self.External_Doc = document.external
        else:
            proforma = document
            self.Date = proforma.date.strftime('%d-%m-%Y')

            if isinstance(document, SaleProforma):
                prefix = 'PI'
            else:
                prefix = 'PO'

            self.Document_No = prefix + proforma.doc_repr

            self.External_Doc = proforma.external

        self.Agent = proforma.agent.fiscal_name.split()[0]
        self.Incoterms = proforma.incoterm
        self.Currency = 'EUR' if proforma.eur_currency else 'USD'

    def __iter__(self):
        return iter(self.__dict__.items())


class TotalsData:

    def __init__(self, document):
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

    def __init__(self, document):
        self.last_condition_y_position = None
        global utils
        from importlib import reload
        utils = reload(utils)
        super().__init__()
        self.document = document
        self.resolve_header_and_lines_repr(document)
        self.we = We.from_actual_db()
        self.table_data = TableData(document)
        self.totals_data = TotalsData(document)


    def resolve_header_and_lines_repr(self, document):

        if isinstance(document, SaleProforma):
            self.we_buy = False
            self.doc_header = 'SALE ORDER'
            if document.lines:
                self.lines = SaleLinesPDFRepr(document.lines)
            elif document.advanced_lines:
                self.lines = AdvancedLinesPDFRepr(document.advanced_lines)
            elif document.credit_note_lines:
                self.lines = CreditLinesPDFRepr(document.credit_note_lines)

        elif isinstance(document, SaleInvoice):
            # TODO merge lines
            if len(document.proformas) > 1:
                lines_objects = []

                for proforma in document.proformas:
                    if proforma.lines:
                        lines_objects.append(SaleLinesPDFRepr(proforma.lines))
                    elif proforma.advanced_lines:
                        lines_objects.append(AdvancedLinesPDFRepr(proforma.advanced_lines))
                self.lines = MixedUPLinesPDFRepr(lines_objects)

            else:
                proforma = document.proformas[0]
                if proforma.lines:
                    self.lines = SaleLinesPDFRepr(proforma.lines)
                elif proforma.credit_note_lines:
                    self.lines = CreditLinesPDFRepr(proforma.credit_note_lines)
                elif proforma.advanced_lines:
                    self.lines = AdvancedLinesPDFRepr(proforma.advanced_lines)

            self.we_buy = False
            self.doc_header = 'COMMERCIAL INVOICE'

        elif isinstance(document, PurchaseProforma):
            self.we_buy = True
            self.doc_header = 'PURCHASE ORDER'
            self.lines = PurchaseLinesPDFRepr(document.lines)

        elif isinstance(document, PurchaseInvoice):
            self.we_buy = True
            self.doc_header = 'PURCHASE INVOICE'
            lines = [line for proforma in document.proformas for line in proforma.lines]
            self.lines = PurchaseLinesPDFRepr(lines)

    def header(self, print_lines_header=True):
        self.set_xy(18.75, 13.53)
        self.image(get_logo(), w=70, h=18.2)
        self.set_font('Arial', 'B', 18)
        self.set_xy(127.5, 13.35)
        self.cell(74, 17, self.doc_header, 1, 0, 'C')

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
        return CONDITIONS_Y_INCREMENT * len(get_conditions()) + 10

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

        # Add origin proformas if invoiced:
        if hasattr(self.table_data, 'origin_proformas'):
            self.y += 10
            self.set_font('Arial', 'B', size=10)
            self.cell(0, txt=f'From Proformas:')
            self.x = LEFT_MARGIN + 4
            self.y += Y_INCREMENT
            self.set_font('Arial', size=8)
            self.cell(0, txt=self.table_data.origin_proformas)

        self.x = LEFT_MARGIN
        self.y += 10
        self.set_font('Arial', 'B', size=10)

        self.cell(0, txt='Comment:')
        self.x = LEFT_MARGIN + 4
        self.y += Y_INCREMENT
        self.set_font('Arial', size=8)
        self.cell(0, txt=self.document.note or '')
        self.y += ADDITIONAL_TEXT_TERM_INCREMENT

    def print_vertical_line(self):

        x1 = x2 = VERTICAL_LINE_X_POSITION
        y2 = self.y
        y1 = y2 - VERTICAL_LINE_Y_INCREMENT

        self.line(x1, y1, x2, y2)

    def print_terms(self):
        self.x = LEFT_MARGIN
        self.y += 5

        if isinstance(self.document, (SaleProforma, PurchaseProforma)):
            name = 'Proforma'
        else:
            name = 'Factura'

        doc_type = self.document.type

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

        if isinstance(self.document, (SaleProforma, SaleInvoice)):
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
        for condition in get_conditions():
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

        for condition in get_rma_conditions():
            self.cell(0, txt=condition)
            self.x = RMA_START_X_POSITION
            self.y += CONDITIONS_BETWEEN_Y_INCREMENT

        self.print_bank()

    def print_bank(self):
        self.x = BANK1_LOGO_X_POSITION
        self.y = self.last_condition_y_position + BANK_LOGO_Y_INCREMENT
        self.image(get_logo_bank_1(), w=21.7, h=4.91)
        self.x = BANK2_LOGO_X_POSITION
        self.y = self.last_condition_y_position + BANK_LOGO_Y_INCREMENT
        self.image(get_logo_bank_2(), w=20.42, h=4.91)

        y_absolute_position = self.y - -3

        self.x = BANK1_TEXT_X_POSITION

        self.y = self.last_condition_y_position + BANK_TEXT_Y_CONDITION_RELATIVE_INCREMENT

        self.set_font('Arial', size=7, style='b')
        for t in [
            'Bank: Banco de Sabadell, S.A.',
            'Currency: EUR',
            'IBAN: ES58 0081 1296 7700 0132 0242',
            'SWIFT/BIC: BSABESBBXXX'
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
        partner = self.we if self.we_buy else self.document.partner_object
        x, y = BUYER_BASE
        self.print_helper(partner, x, y, header='Buyer:')

    def print_supplier(self):
        partner = self.document.partner_object if self.we_buy else self.we
        x, y = SUPPLIER_BASE
        self.print_helper(partner, x, y, header='Supplier:')

    def print_delivery_address(self):
        partner = self.we if self.we_buy else self.document.partner_object
        x, y = DELIVERY_ADDRESS_BASE
        # handling added feature multiple delivery addresses

        if isinstance(self.document, (SaleProforma, SaleInvoice)):

            self.set_xy(x, y)
            self.set_font('Arial', 'B', size=12)
            self.cell(0, txt='DELIVERY ADDRESS:')
            self.set_font('Arial', size=10)

            address = self.document.shipping_address
            for e in [
                partner.fiscal_name,
                address.line1,
                address.line2,
                ' '.join([address.zipcode, address.city, address.state]),
                address.country,
                'VAT Nº: ' + partner.fiscal_number
            ]:
                y += 4
                self.set_xy(x, y)
                self.cell(0, txt=e)

        else:
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

            if key == 'origin_proformas':
                continue

            text = key.replace('_', ' ') + ':'
            self.cell(w=TABLE_LEFT_INCRMENT, h=TABLE_DOWN_INCREMENT, border=True, align='R', txt=text)
            self.set_x(x + TABLE_LEFT_INCRMENT)
            self.cell(w=TABLE_RIGHT_INCREMENT, h=TABLE_DOWN_INCREMENT, align='C', border=True, txt=value or '')
            # Value can take None causing code in fpdf to raise TypeError. This solves the issue
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
                ('UP', UNIT_POSITION),
                ('VAT', TAX_POSITION),
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
        for line_number, line in self.lines:
            x = x_start
            for i, element in enumerate(line, 0):
                increment = next(INNER_LINE_X_INCREMENTS)
                try:
                    print_lines_header = line_number < lines_total
                except TypeError:
                    print_lines_header = False

                self.cell(increment, txt=element, align='R' if i >= 2 else 'L', caller=self,\
                          print_lines_header=print_lines_header)
                x += increment
                self.set_x(x)

            if line.price == '':
                self.y_start += INNER_LINE_Y_INCREMENT - 2
            else:
                self.y_start += INNER_LINE_Y_INCREMENT

            self.set_xy(x_start, self.y_start)


def build_document(document):
    pdf = PDF(document)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 10)
    pdf.add_page()
    pdf.print_body()
    pdf.print_footer()
    return pdf

