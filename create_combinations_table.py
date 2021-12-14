

import openpyxl
import itertools

wb = openpyxl.Workbook()
ws = wb.active

ws.append(['MPN', 'Manufacturer', 'Category', 'Model', 'Capacity', 'Color'])

for tuple in [
    tuple 
    for tuple in itertools.product(['Si', 'No'], repeat=6)
    if tuple[1] == 'Si' and tuple[2] == 'Si'
]:
    ws.append(tuple)


wb.save('combinations.xlsx')


