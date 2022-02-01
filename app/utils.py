
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

def mymap(db_class):
	return {o.fiscal_name:o.id for o in db.session.query(db_class.fiscal_name, db_class.id).\
		where(db_class.active == True)}


countries = list(dict(countries_for_language("en")).values())
dirty_map = bidict({item.dirty_repr:item.id for item in db.session.query(db.Item)})
description_id_map = bidict({item.clean_repr:item.id for item in db.session.query(db.Item)})

# Build this map at import time
# the new map will be man|cat|mod|cap|col -> item_id 

#STOCK TYPES:

CAP_COL, ONLY_COL, ONLY_CAP = 0, 1, 2

def stock_type(stock):
    # Este check me permite sobrecargar el metodo, 
    # acepta item_id o stockEntry
    id = stock if isinstance(stock, int) else stock.item_id 
    *_, cap, col, _ = dirty_map.inverse[id] 
    if cap != '?' and col != '?':
        return CAP_COL
    elif cap == '?' and col != '?':
        return ONLY_COL
    elif cap != '?' and col == '?':
        return ONLY_CAP
    else:
        return -1 # No mixing available 
    

specs = {s.description for s in db.session.query(db.Spec.description)}
conditions = {c.description for c in db.session.query(db.Condition.description)}
partner_id_map =mymap(db.Partner)
agent_id_map =mymap(db.Agent)

courier_id_map = {
	c.description:c.id 
	for c in db.session.query(db.Courier.id, db.Courier.description)
}
warehouse_id_map = {
	w.description:w.id 
	for w in db.session.query(db.Warehouse.description, db.Warehouse.id)
}

def complete_descriptions(clean_map, dirty_map):
    descriptions = set()
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
    if not mixed_description:return
    ids = [] 
    if mixed_description.count('Mixed') == 2:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, *_ = dirty_desc.split('|')
            if mpn == '?':mpn = '' 
            if ' '.join((mpn, man, cat, mod, 'Mixed GB', 'Mixed Color')).strip() == mixed_description:
                ids.append(dirty_map[dirty_desc])
    
    elif 'Mixed GB' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, _, col, _ = dirty_desc.split('|')
            if mpn == '?':mpn = '' 
            if ' '.join((mpn, man, cat, mod, 'Mixed GB', col)).strip() == mixed_description:
                ids.append(dirty_map[dirty_desc])

    elif 'Mixed Color' in mixed_description:
        for dirty_desc in dirty_map:
            mpn, man, cat, mod, cap, col, _  = dirty_desc.split('|') 
            if mpn == '?':mpn = '' 
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

def has_serie(clean_repr):
    id = description_id_map[clean_repr]
    dirty_repr = dirty_map.inverse[id]
    return dirty_repr.endswith('y')

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
    defualt_path = None
    filter = "Pdf Files (*.pdf)"
    basepath = os.getenv('HOMEPATH')
    if basepath:
        defualt_path = os.path.join(basepath, filename)
    return QFileDialog.getSaveFileName(parent, "Save File", defualt_path, filter=filter)

def askFilePath(parent):
    defualt_path = None
    filter = "Pdf Files (*.pdf)"
    return QFileDialog.getOpenFileName(parent, "Open File", defualt_path, filter=filter)


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
    return QFileDialog.getExistingDirectory(parent, 'Get direcotry', 'Z:')

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
    print('set completer init:', field.objectName())
    model = QStringListModel()
    model.setStringList(data)
    completer = field.completer()
    if completer is not None:
        print('completer is not None')
        completer.setModel(model)
    else:
        model = QStringListModel()
        model.setStringList(data)
        completer = QCompleter()
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(False)
        completer.setModel(model)
        field.setCompleter(completer)
    

def build_description(lines):

    line = lines[0] 

    if stock_type(line.item_id) == CAP_COL:
        capacities = set() 
        for line in lines:
            capacities.add(
                dirty_map.inverse[line.item_id].split('|')[-3]
            )

        if len(capacities) == 1: 
            capacity = capacities.pop() + ' GB'
        else:
            capacity = 'Mixed GB'
        
        colors = set()
        for line in lines:
            color = dirty_map.inverse[line.item_id].split('|')[-2]
            colors.add(color) 

        if len(colors) == 1:
            color = colors.pop()
        else:
            color = 'Mixed Color'
        
        line = lines[0]
        description = dirty_map.inverse[line.item_id] 
        _, manufacturer, category, model , *_ = description.split('|') 
        return ' '.join([
            manufacturer, category, model, 
            capacity, color 
        ])
    
    elif stock_type(line.item_id) == ONLY_COL:
        
        colors = set()
        for line in lines:
            color = dirty_map.inverse[line.item_id].split('|')[-2]
            colors.add(color) 

        if len(colors) == 1:
            color = colors.pop()
        else:
            color = 'Mixed Color'
        
        description = dirty_map.inverse[line.item_id] 
        _, manufacturer, category, model, *_ = description.split('|') 
        return ' '.join((
            manufacturer, category, model, color
        ))

 
if __name__ == '__main__':

    for description in complete_descriptions(description_id_map, dirty_map):
        if 'Mix' in description:
            print(description)
            for d in mixed_to_clean_descriptions(description):
                print('\t', d)
