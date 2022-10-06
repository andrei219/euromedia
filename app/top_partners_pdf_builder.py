from fpdf import FPDF

from datetime import datetime

TITLE = 80, 10

EUROMEDIA = 10, 30
FROM = 10, 38
TO = 10, 46

GENERATED = 120, 30


CURRENCY = 120, 42

TABLE_X = 10
TABLE_Y = 60
DATE = 26
RANK = 17
PARTNER = 32
SUBTOTAL = 83
TAX = 110
TOTAL = 135

LINE = 10, 62, 200, 62

TABLE_INNER_START = 18, 67

ROW_INCREMENT = 4

MAX_LINES = 53

X_TOTALS = 80


class PDF(FPDF):

    def __init__(self, content):
        super().__init__()
        self.content = content

    def header(self, print_lines_header=True):
        self.x, self.y = TITLE
        self.set_font('Arial',  'B', 18)
        self.cell(0, txt='TOP PARTNERS')

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

        self.x, self.y = CURRENCY
        self.cell(0, txt='Currency: EUR')


        self.set_font('Arial', 'B', size=6)

        self.text(RANK, TABLE_Y, 'Rank')
        self.text(PARTNER, TABLE_Y, "Partner")
        self.text(SUBTOTAL, TABLE_Y, "Excl. VAT")
        self.text(TAX, TABLE_Y, "VAT")
        self.text(TOTAL, TABLE_Y, "Total")

        self.line(*LINE)

    def print_body(self):

        self.set_font('Courier', '', size=6)
        x, y = TABLE_INNER_START
        counter = 0
        for register in self.content.registers:
            self.text(x, y, str(register))
            y += ROW_INCREMENT
            counter += 1
            if counter % MAX_LINES == 0:
                self.add_page()
                x, y = TABLE_INNER_START

        self.line(10, y, 200, y)

        x = X_TOTALS
        y += ROW_INCREMENT




def build_document(content):
    pdf = PDF(content)
    pdf.set_auto_page_break(True)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.print_body()
    return pdf
