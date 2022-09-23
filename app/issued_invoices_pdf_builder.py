
from fpdf import FPDF

class PDF(FPDF):

    def __init__(self, content):
        pass


def build_document(content):
    pdf = PDF(content)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 10)
    pdf.add_page()
    pdf.print_body()
    pdf.print_footer()
    return pdf
