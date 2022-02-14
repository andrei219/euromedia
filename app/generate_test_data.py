
import db 


import random, string

import openpyxl

items = db.session.query(db.Item).all() 

conditions = db.session.query(db.Condition).all() 
conditions = [c.description for c in conditions if c != 'Mix']

specs = db.session.query(db.Spec).all() 
specs = [s.description for s in specs if s != 'Mix']


def get_random_serie():
    ser = ''.join(str(random.randint(1, 9)) for i in range(15)) 
    return ser

rows = [] 
for i in range(100 ):
    item = random.choice(items)
    serie=None
    quantity = 5 
    if item.has_serie:
        serie = '*' + get_random_serie() + '*'
        quantity = 1

    row = (
        item.id, item.clean_repr, random.choice(conditions), 
        random.choice(specs), serie or '', quantity
    )
    
    rows.append(row)

distinct_ids = {item.id for item in db.session.query(db.Item).all()}
generated_ids = {row[0] for row in rows}


def grouped(rows):
    from itertools import groupby

    key = lambda r:(r[0], r[1], r[2])
    rows = sorted(rows, key=key)

    for k, g in groupby(rows, key=key):
        for e in g:
            yield e


if generated_ids == distinct_ids:
    print('building file')
    print('grouping..')

    wb = openpyxl.Workbook()
    ws = wb.active

    for row in grouped(rows):
        ws.append(row) 

    from openpyxl.styles import Font
    for row in ws.iter_rows():
        row[4].font = Font(name= 'IDAHC39M Code 39 Barcode')
    wb.save('..\data.xlsx')
else:
    print('Not building file...')