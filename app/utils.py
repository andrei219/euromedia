
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
SERIE_NOT_MIXED, SERIE_MIXED, NO_SERIE = 0, 1, 2 



def mix_candidate(dirty_description):
    mpn, man, cat, mod, cap, col, has_serie = dirty_description.split('|')
    return all((
        mpn == '?', 
        man != '?', 
        cat != '?', 
        mod != '?', 
        cap != '?', 
        col != '?', 
        has_serie == 'y'
    ))

sub_dirty_map = bidict({k[2:-2]:dirty_map[k] for k in dirty_map \
        if mix_candidate(k)})


def stock_type(stock):
    # Este check me permite sobrecargar el metodo, 
    # acepta item_id o stockEntry
    
    if isinstance(stock, int):
        id = stock
    else:
        id = stock.item_id
    
    # BRANCH ORDER IS IMPORTANT
    if dirty_map.inverse[id].endswith('n'):
        return NO_SERIE
    if id in dirty_map.inverse and not id in sub_dirty_map.inverse:
        return SERIE_NOT_MIXED
    elif id in sub_dirty_map.inverse:
        return SERIE_MIXED 

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
            if  all((
                mpn == '?', 
                man != '?', 
                cat != '?', 
                mod != '?', 
                cap != '?', 
                col != '?', 
                has_serie == 'y'
            )):
                descriptions.update(
                    {
                        ' '.join((man, cat, mod, 'Mixed GB', col)),
                        ' '.join((man, cat, mod, 'Mixed GB', 'Mixed Color')), 
                        ' '.join((man, cat, mod, cap, 'Mixed Color'))
                    }
                )
    return descriptions



@functools.cache
def mixed_to_clean_description(mixed_description):
    clean_descriptions = [] 
    if mixed_description.count('Mixed') == 2:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, _, _ = dirty_desc.split('|')
            if ' '.join((man, cat, mod, 'Mixed GB', 'Mixed Color')) == mixed_description:
                clean_descriptions.append(
                    description_id_map.inverse[sub_dirty_map[dirty_desc]]
                )

    elif 'Mixed GB' in mixed_description:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, _, col = dirty_desc.split('|')
            if ' '.join((man, cat, mod, 'Mixed GB', col)) == mixed_description:
                clean_descriptions.append(
                    description_id_map.inverse[sub_dirty_map[dirty_desc]]
                )

    elif 'Mixed Color' in mixed_description:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, cap, _  = dirty_desc.split('|') 
            if ' '.join((man, cat, mod, cap, 'Mixed Color')) == mixed_description:
                clean_descriptions.append(
                    description_id_map.inverse[sub_dirty_map[dirty_desc]]
                )


    return clean_descriptions


descriptions = complete_descriptions(description_id_map, dirty_map) 


@functools.cache
def get_itemids_from_mixed_description(mixed_description):
    # Cuando calculamos todo el stock, 
    # este metodo recibe none 
    if not mixed_description: return None
    ids = [] 
    if mixed_description.count('Mixed') == 2:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, _, _ = dirty_desc.split('|')
            if ' '.join((man, cat, mod, 'Mixed GB', 'Mixed Color')) == mixed_description:
                ids.append(sub_dirty_map[dirty_desc])

    elif 'Mixed GB' in mixed_description:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, _, col = dirty_desc.split('|')
            if ' '.join((man, cat, mod, 'Mixed GB', col)) == mixed_description:
                ids.append(sub_dirty_map[dirty_desc])

    elif 'Mixed Color' in mixed_description:
        for dirty_desc in sub_dirty_map:
            man, cat, mod, cap, _  = dirty_desc.split('|') 
            if ' '.join((man, cat, mod, cap, 'Mixed Color')) == mixed_description:
                ids.append(sub_dirty_map[dirty_desc])

    return ids


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

# Remove Nones from iterable values
# Remove entries with empty iterables after previous operation
def washDict(d:dict):
    for k in d:
        d[k] = list(filter(None, d[k]))
    k = list(d.keys()) 
    # keep a new reference to keys, otherwhise, dict size would change while iterating
    # which causes error. 
    for _k in k:
        if not d[_k]:
            del d[_k]
    return d


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

    print(text, ok)
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
    model = QStringListModel()
    model.setStringList(data)
    completer = QCompleter()
    completer.setFilterMode(Qt.MatchContains)
    completer.setCaseSensitivity(False)
    completer.setModel(model)
    field.setCompleter(completer)



def build_description(lines):
    capacities = set() 
    for line in lines:
        for e in sub_dirty_map.inverse[line.item_id].split('|'):
            if e.isdigit():
                capacities.add(e)
                break
    
    if len(capacities) == 1:
        capacity = capacities.pop() + 'GB'
    else:
        capacity = 'Mixed GB'
    
    colors = set()
    for line in lines:
        color = sub_dirty_map.inverse[line.item_id].split('|')[-1]
        colors.add(color) 

    if len(colors) == 1:
        color = colors.pop()
    else:
        color = 'Mixed Color'
    
    line = lines[0]
    description = sub_dirty_map.inverse[line.item_id] 
    manufacturer, category, model , *_ = description.split('|') 
    return ' '.join([
        manufacturer, category, model, 
        capacity, color 
    ])
 

if __name__ == '__main__':

    for d in complete_descriptions(description_id_map, dirty_map):
        if 'Mix' in d:
            print(' ', d)
            for clean in mixed_to_clean_description(d):
                print('\t', clean)
