
from fpdf import FPDF

from datetime import datetime

TITLE = 90, 10

EUROMEDIA = 10, 40
FROM = 10, 48
TO = 10, 56

GENERATED = 120, 40

TABLE_X = 8
TABLE_Y = 70
DATE = 20
PARTNER = 30
AGENT = 80
FINANCIAL = 90

TABLE_INNER_START = 10, 80

ROW_INCREMENT = 5

class PDF(FPDF):

    def __init__(self, content):
        super().__init__()
        self.content = content

    def print_header(self):
        self.x, self.y = TITLE
        self.set_font('Arial',  'B', 18)
        self.cell(0, txt='Issued Invoices')

        self.set_font('Arial', size=10)
        self.x, self.y = EUROMEDIA
        self.cell(0, txt='Company: Euromedia Investment Group, S.L.')

        self.x, self.y = FROM
        self.cell(0, txt=f'From: {self.content.from_.strftime("%d/%m/%Y")}')

        self.x, self.y = TO
        self.cell(0, txt=f'To: {self.content.to.strftime("%d/%m/%Y")}')

        self.x, self.y = GENERATED
        self.set_font('Arial', 'B', size=10)
        self.cell(0, txt=f"Generated at: {datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")

        self.set_font('Arial', 'B', size=6)


    def print_footer(self):
        pass

    def print_body(self):
        self.set_font('Courier', '', size=6)
        x, y = TABLE_INNER_START
        for register in self.content.registers:
            self.text(x, y, str(register))
            y += ROW_INCREMENT




def build_document(content):
    pdf = PDF(content)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 10)
    pdf.add_page()
    pdf.print_header()
    pdf.print_body()
    pdf.print_footer()
    return pdf
