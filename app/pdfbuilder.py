
# coding: utf8

from fpdf import FPDF
from copy import deepcopy
from itertools import chain, product

# CONSTANTS: 
LOGO_RELATIVE_PATH = r'.\app\icons\warehouse.png'

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
TOTAL_POSITION =(182.68, 114.89)
LINE_HEADER_START = (13.5, 118.77)
LINE_WIDTH = 183
INNER_LINE_START = (19.55, 123.3)
INNER_LINE_Y_INCREMENT = 5.52
INNER_LINE_X_INCREMENTS = [12.55, 100.14, 13.73, 24.83, 25.21]

from models import description_id_map

class PurcahseLinePDFRepr:
    def __init__(self, line):
        self.description = description_id_map.inverse.get(line.item_id)
        if not self.description:
            self.description = line.description

        else:
            if line.condition:
                self.description += f', {line.condition} condt.'
            if line.spec:
                self.description += f', {line.spec} spec'
        
        self.quantity = str(line.quantity)
        self.price = str(line.price)
        self.total = str(line.price * line.quantity)

    def __iter__(self):
        return iter((self.description, self.quantity, self.price, self.total))

class SaleLinesPDFRepr:
    
    def __init__(self, lines):
        self.lines = lines

    def __iter__(self):
        return iter(  [('A', 'B', 'C', 'D') for i in range(10)]      )
    
class PurchaseLinesPDFRepr:
    
    def __init__(self, lines):
        self.lines = lines 
    
    def __iter__(self):
        return iter(map(PurcahseLinePDFRepr, self.lines)) 


class We:
    def __init__(self):
        self.fiscal_name = 'Euromedia Investment Group, S.L.'
        self.billing_line1 = 'Calle Camino Real, Nº22, Bajo Izq'
        self.billing_line2 = '46900 Torrente'
        self.billing_line3 = 'Valencia'
        self.billing_country = 'Spain'
        self.registerd = 'Registered on 22/03/2016'
        self.fiscal_number = 'B98815608'
        self.vat = 'VAT Nº:ESB98815608'
        self.shipping_line1 = 'Calle Camino Real, Nº22, Bajo Izq'
        self.shipping_line2 = '46900 Torrente'
        self.shipping_line3 = 'Valencia'
        self.shipping_country = 'Spain'
        self.phone = '+34 633 333 973'


class TableData:

    def __init__(self, document, *, is_invoice):
        self.Date = str(document.invoice.date) if is_invoice else str(document.date) 
        self.PO = str(document.invoice.type) + str(document.invoice.number).\
            zfill(6) if is_invoice else str(document.type) + str(document.number).zfill(6)
        self.Agent = document.agent.fiscal_name
        self.Incoterms = document.incoterm
        self.Delivery_Date = str(document.invoice.eta) if is_invoice \
            else str(document.eta) 
        self.Currency = 'EUR' if document.eur_currency else \
            'USD '
        
    def __iter__(self):
        return iter(self.__dict__.items())

class PDF(FPDF):

    def __init__(self, document, *, is_invoice):
        super().__init__()
        self.document = document
        self.resolve_header_and_lines_repr(document, is_invoice) 
        self.we = We() 
        self.table_data = TableData(document, is_invoice=is_invoice)

    def resolve_header_and_lines_repr(self, document, is_invoice):
        from db import SaleProforma, PurchaseProforma
        if type(document) == SaleProforma:
            self.we_buy = False
            self.lines = SaleLinesPDFRepr(document.lines)
            if not is_invoice :
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

    def header(self):
        self.set_xy(18.75, 13.53)
        self.image(LOGO_RELATIVE_PATH)
        self.set_font('Arial', 'B', 18)
        self.set_xy(127.5, 13.35)
        self.cell(68, 17, self.doc_header , 1, 0, 'C')
                
        self.print_buyer() 
        self.print_supplier()
        self.print_delivery_address()
        self.print_table()
        self.print_desc_header() 


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
            getattr(partner, prefix + 'line3'), 
            getattr(partner, prefix + 'country'), 
            'CIF Nº:' + partner.fiscal_number 
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

    def print_desc_header(self):
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
        self.cell(LINE_WIDTH, border=True)
        
    def print_body(self):
        self.append_lines() 

    def append_lines(self):
        x_start, y_start = INNER_LINE_START
        self.set_xy(x_start, y_start)
        for line_number, line in enumerate(self.lines, 1):
            increments = deepcopy(INNER_LINE_X_INCREMENTS)
            x = x_start
            for i, element in enumerate(chain([str(line_number)], line), 0):
                increment = increments.pop(0)
                self.cell(increment, txt=element, align='R' if i>=2 else 'L') 
                x += increment
                self.set_x(x)
            y_start += INNER_LINE_Y_INCREMENT
            self.set_xy(x_start, y_start)


names = ['A', 'B', 'C', 'D']

def build_document(document, *, is_invoice):
    pdf = PDF(document, is_invoice=is_invoice)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.print_body()
    name = names.pop() 
    name +=  '.pdf'
    pdf.output(name, 'F')

if __name__ == '__main__':

    from db import SaleProforma, session, PurchaseProforma

    sale = session.query(SaleProforma).first()
    purchase = session.query(PurchaseProforma).first()

    from itertools import product

    for doc, is_invoice in product(
        [sale, purchase], 
        [True, False]
    ):  
        build_document(doc, is_invoice=is_invoice)
    
    