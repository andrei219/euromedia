
# Python standad library 
import os 
import re 
import base64
from datetime import datetime   
import functools

# QtFramework stuff:
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QFileDialog, QLineEdit


# Miscelaneous
from country_list import countries_for_language
from schwifty import IBAN, BIC

# Sqalchemy 
from sqlalchemy.sql import select, func


import db 
from bidict import bidict



EXCEL_FILTER = 'Archivos excel (*.xlsx)'
PDF_FILETR = "Pdf Files (*.pdf)"


def mymap(db_class):
	return {o.fiscal_name:o.id for o in db.session.query(db_class.fiscal_name, db_class.id).\
		where(db_class.active == True)}


countries = list(dict(countries_for_language("en")).values())
dirty_map = bidict({item.dirty_repr:item.id for item in db.session.query(db.Item)})
description_id_map = bidict({item.clean_repr:item.id for item in db.session.query(db.Item)})

# Build this map at import time
# the new map will be man|cat|mod|cap|col -> item_id 

#STOCK TYPES:
ONLY_COL, ONLY_CAP, CAP_COL = 1, 2, 3

def stock_type(stock):
    id = stock if isinstance(stock, int) else stock.item_id 
    mpn, *_, cap, col, _ = dirty_map.inverse[id].split('|')
    if mpn != '?':
        return -1 
    if cap != '?' and col != '?':
        return CAP_COL
    elif cap == '?' and col != '?':
        return ONLY_COL
    elif cap != '?' and col == '?':
        return ONLY_CAP
    else:
        return -1 # No mixing available 
    
def is_object_presisted(object):
    from sqlalchemy import inspect
    inspector = inspect(object)
    return inspector.persistent

def mixing_compatible(o, p):

    if o.item_id == p.item_id:
        return True
    # First stocks must be same type and != -1 
    if stock_type(o) == -1 or stock_type(p) == -1:
        return False
    if stock_type(o) != stock_type(o):
        return False
    
     

    # Once stock is same type, we are interested in base 

    d1, d2 = dirty_map.inverse[o.item_id], dirty_map.inverse[p.item_id]
    
    man1, cat1, mod1, *_ = d1.split('|')
    man2, cat2, mod2, *_ = d2.split('|')
    
    return all((man1 == man2, cat1 == cat2, mod1 == mod2))


specs = {s.description for s in db.session.query(db.Spec.description)}
conditions = {c.description for c in db.session.query(db.Condition.description)}
partner_id_map =mymap(db.Partner)
agent_id_map =mymap(db.Agent)

courier_id_map = bidict({
	c.description:c.id 
	for c in db.session.query(db.Courier.id, db.Courier.description)
}) 
warehouse_id_map = bidict({
	w.description:w.id 
	for w in db.session.query(db.Warehouse.description, db.Warehouse.id)
})


import uuid
def valid_uuid(string):
    try:
        uuid.UUID(string)
        return True 
    except ValueError:
        return False 

def complete_descriptions(clean_map, dirty_map):
    descriptions = set()
    descriptions.update(clean_map.keys())
    descriptions.update(clean_map.keys())
    for dirty_repr in dirty_map:
        mpn, man, cat, mod, cap, col, has_serie = dirty_repr.split('|')
        if mpn != '?': continue 
        else: mpn = ''
        if cap != '?' and col != '?':
            descriptions.update({
                ' '.join((mpn, man, cat, mod, 'Mixed GB', 'Mixed Color')).strip(), 
                ' '.join((mpn, man, cat, mod, 'Mixed GB', col)).strip(), 
                ' '.join((mpn, man, cat, mod, cap, 'Mixed Color')).strip()
            })
        elif col != '?' and cap == '?':
            descriptions.add(' '.join((mpn, man, cat, mod, 'Mixed Color')).strip())
        elif cap != '?' and col == '?':
            descriptions.add(' '.join((mpn, man, cat, mod, 'Mixed GB')).strip()) 
    
    return descriptions


@functools.cache
def mixed_to_clean_descriptions(mixed_description):
    clean_descriptions = [] 
    if mixed_description.count('Mixed') == 2:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, *_ = dirty_desc.split('|')
            if mpn != '?': continue 
            else: mpn = ''
            if ' '.join((mpn, man, cat, mod, 'Mixed GB', 'Mixed Color')).strip() == mixed_description:
                clean_descriptions.append(
                    description_id_map.inverse[dirty_map[dirty_desc]]
                )
    elif 'Mixed GB' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, _, col, _ = dirty_desc.split('|')
            if mpn != '?': continue 
            else: mpn = ''
            col = col if col != '?' else ''
            if ' '.join((mpn, man, cat, mod, 'Mixed GB', col)).strip() == mixed_description:
                clean_descriptions.append(
                    description_id_map.inverse[dirty_map[dirty_desc]]
                )
    
    elif 'Mixed Color' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, cap, col, _  = dirty_desc.split('|') 
            if mpn != '?': continue 
            else: mpn = ''
            
            if cap != '?' and col != '?':
                if ' '.join((mpn, man, cat, mod, cap, 'Mixed Color')).strip() == mixed_description:
                    clean_descriptions.append(
                        description_id_map.inverse[dirty_map[dirty_desc]]
                    )
            
            elif cap == '?' and col != '?':
                if ' '.join((mpn, man, cat, mod, 'Mixed Color')).strip() == mixed_description:
                    clean_descriptions.append(
                        description_id_map.inverse[dirty_map[dirty_desc]]
                    )

    return clean_descriptions


descriptions = complete_descriptions(description_id_map, dirty_map) 


@functools.cache
def get_itemids_from_mixed_description(mixed_description):
    if not mixed_description:
        return
    ids = [] 
    if mixed_description.count('Mixed') == 2:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, *_ = dirty_desc.split('|')
            # if mpn == '?':mpn = '' 
            if mpn != '?':continue 
            else:mpn = ''

            if ' '.join((mpn, man, cat, mod, 'Mixed GB', 'Mixed Color')).strip() == mixed_description:
                ids.append(dirty_map[dirty_desc])
    
    elif 'Mixed GB' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, _, col, _ = dirty_desc.split('|')
            if mpn != '?':continue 
            else:mpn = ''
            col = col if col != '?' else ''
            if ' '.join((mpn, man, cat, mod, 'Mixed GB', col)).strip() == mixed_description:
                ids.append(dirty_map[dirty_desc])

    elif 'Mixed Color' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, cap, col, _  = dirty_desc.split('|') 
            if mpn != '?':continue 
            else: mpn = '' 
            if cap != '?' and col != '?':
                if ' '.join((mpn, man, cat, mod, cap, 'Mixed Color')).strip() == mixed_description:
                    ids.append(dirty_map[dirty_desc])
            
            elif cap == '?' and col != '?':
                if ' '.join((mpn, man, cat, mod, 'Mixed Color')).strip() == mixed_description:
                    ids.append(dirty_map[dirty_desc])
    return ids 


def compute_available_descriptions(available_item_ids):
    cmap = bidict({k:v for k, v in description_id_map.items() if v in available_item_ids})
    dmap = bidict({k:v for k, v in dirty_map.items() if v in available_item_ids})
    return complete_descriptions(cmap, dmap)


def has_serie(line):
    try:
        id = description_id_map[line.item.clean_repr]
        dirty_repr = dirty_map.inverse[id]
        return dirty_repr.endswith('y')
    except AttributeError: # line.item is None
        ids = get_itemids_from_mixed_description(line.description)
        return all((
            dirty_map.inverse[id].endswith('y')
            for id in get_itemids_from_mixed_description(line.description)
        ))

def get_items_ids_by_keyword(keyword):
    return [description_id_map[k] for k in description_id_map if keyword in k.lower()]


def validSwift(bic):
    try:
        BIC(bic)
    except ValueError:
        return False
    return True


def validIban(iban):
    try:
        IBAN(iban)
    except ValueError:
        return False
    return True


# Let the user pass a string or an IBAN object 
# If the iban is not valid, do nothing
def swiftFromIban(iban):
    if isinstance(iban, BIC) and iban.bic:
        return str(iban.bic)
    elif isinstance(iban, str):
        try:
            return str(IBAN(iban).bic) 
        except ValueError:
            pass 

def base64Pdf(abspath):
    with open(abspath, "rb") as fd:
        return base64.b64encode(fd.read()) 

def writeBase64Pdf(abspath, base64pdf):
    with open(abspath, "wb") as fd:
        fd.write(base64.b64decode(base64pdf))

def askSaveFile(parent, filename):
    return QFileDialog.getSaveFileName(parent, "Save File", get_desktop(), filter=PDF_FILETR)

def askFilePath(parent):
    return QFileDialog.getOpenFileName(parent, "Open File", get_desktop(), filter=PDF_FILETR)



from PyQt5.QtWidgets import QTableView

def setCommonViewConfig(view):
    view.setSelectionBehavior(QTableView.SelectRows)
    view.setSelectionMode(QTableView.SingleSelection)
    
    view.setSortingEnabled(True)
    
    view.setAlternatingRowColors(True)

    view.setEditTriggers(QTableView.NoEditTriggers)


def getPassword(parent):
    text, ok = QInputDialog.getText(parent, 'Password', 'password: ',  QLineEdit.Password)
    if text and ok:
        return text

def getTracking(parent, proforma):
    type_num = str(proforma.type) + '-' + str(proforma.number).zfill(6)
    text, ok = QInputDialog.getText(
        parent, 
        'Tracking', f'Enter tracking number for {type_num}:'
    )
    return text, ok

def getNote(parent, proforma):
    type_num = str(proforma.type) + '-' + str(proforma.number).zfill(6)
    text, ok = QInputDialog.getText(parent, 'Warehouse', 'Enter a warning for the warehouse order')
    return ok, text

def get_directory(parent):
    return QFileDialog.getExistingDirectory(parent, 'Get directory', get_desktop())

def get_file_path(parent):
    file_path , _ = QFileDialog.getSaveFileName(
            parent, 
            'Save File', 
            get_desktop(), 
            filter=EXCEL_FILTER
        )
    return file_path

def get_open_file_path(parent):
    filepath, _ = QFileDialog.getOpenFileName(
        parent, 
        'Open file', 
        get_desktop(), 
        filter=EXCEL_FILTER
    )
    return filepath
    


def get_desktop():
    import os 
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    if not desktop:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Escritorio')
    return desktop or ''

def parse_date(string):
    if len(string) != 8:
        raise ValueError
    day, month, year = int(string[0:2]), int(string[2:4]), int(string[4:8]) 
    return datetime(year, month, day)

def today_date():
    return datetime.now().strftime('%d%m%Y')

from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QCompleter

def setCompleter(field, data):
    completer = field.completer()
    if completer is not None:
        completer.model().setStringList(data)
    else:
        completer = QCompleter()
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(False)
        model = QStringListModel(data)
        completer.setModel(model)
        field.setCompleter(completer)

def build_description(lines):


    # Si tiene mpn devuelve tal cual.
    # Toda la generalizacion que he ganado por un lado la estoy perdiendo
    # en este otro, pero bueno, esto es menos grave, 
    # toca la parte de representacion
    # no a la parte de gestion del inventario

    line = lines[0] 

    capacities = {dirty_map.inverse[line.item_id].split('|')[-3]\
            for line in lines}

    colors = {dirty_map.inverse[line.item_id].split('|')[-2]\
            for line in lines}

    if stock_type(line.item_id) == CAP_COL:

        if len(capacities) == 1: 
            capacity = capacities.pop() + ' GB' 
        else:
            capacity = 'Mixed GB'

        if len(colors) == 1:
            color = colors.pop()
        else:
            color = 'Mixed Color'
        
        _, manufacturer, category, model, *_ = dirty_map.inverse[line.item_id].split('|') 
        return ' '.join([manufacturer, category, model, capacity, color ])
    
    elif stock_type(line.item_id) == ONLY_COL:

        if len(colors) == 1:
            color = colors.pop()
        else:
            color = 'Mixed Color'
        
        _, manufacturer, category, model, *_ = dirty_map.inverse[line.item_id].split('|') 
        return ' '.join((manufacturer, category, model, color))

    elif stock_type(line.item_id) == ONLY_CAP:
        capacities = {dirty_map.inverse[line.item_id].split('|')[-3]\
            for line in lines}
        
        _, man, cat, mod, *_ = dirty_map.inverse[line.item_id].split('|')
        
        if len(capacities) == 1:
            capacity = capacities.pop() + 'GB'
        else :
            capacity = 'Mixed GB'     
        return ' '.join((man, cat, mod, capacity))

    elif stock_type(line) == -1:
        return description_id_map.inverse[lines[0].item_id]


if __name__ == '__main__':


    for d in descriptions:
        print(d)

