import os
from openpyxl import load_workbook

from models import do_cost_price


from itertools import dropwhile


IMEI_COLUMN, COST_COLUMN = 4, 9


def process_workbook(filename, column_i, column_j):
    wb = load_workbook(filename)
    sheet = wb.active
    for i, row in enumerate(dropwhile(lambda row: row[0] == 'Description', sheet.iter_rows(values_only=True)), 1):
        value = row[column_i-1]  # column numbering starts at 1, not 0
        result = do_cost_price(value).peuro
        sheet.cell(row=i, column=column_j - 1).value = result

    wb.save(filename)

if __name__ == '__main__':
    directory = r'C:\Users\Andrei\Dropbox\Temporary\Coste Almacenes\Updated Prices'
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx'):
            process_workbook(os.path.join(directory, filename), column_i=IMEI_COLUMN, column_j=COST_COLUMN)
