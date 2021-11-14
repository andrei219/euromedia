
# Python standad library 
import os 
import re 
import base64
from datetime import datetime 

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


countries = list(dict(countries_for_language("en")).values())


def mymap(db_class):
	return {o.fiscal_name:o.id for o in db.session.query(db_class.fiscal_name, db_class.id).\
		where(db_class.active == True)}

def complete_descriptions(descriptions):

	d = set() 
	for ds in descriptions:
		manufacturer, category, model, *_ = ds.split(' ')
		d.add(' '.join([manufacturer, category, model, \
			'Mixed GB', 'Mixed Color']))
	for ds in descriptions:
		index = ds.index('GB') + 2 
		ds = ds[0:index] + ' Mixed Color'
		d.add(ds)
	
	for ds in descriptions:
		manufacturer, category, model, capacity, gb, color = ds.split(' ')
		d.add(' '.join([manufacturer, category, model, 'Mixed GB', color]))
	
	return d.union(descriptions)

description_id_map = bidict({str(item):item.id for item in db.session.query(db.Item)})
descriptions = complete_descriptions(description_id_map.keys())

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


def refresh():
    db.refresh_session()

    global descriptions, description_id_map, specs, \
        conditions, partner_id_map, agent_id_map, courier_id_map, warehouse_id_map

    description_id_map = bidict({str(item):item.id for item in db.session.query(db.Item)})
    descriptions = complete_descriptions(description_id_map.keys())

    specs = {s.description for s in db.session.query(db.Spec)}
    conditions = {c.description for c in db.session.query(db.Condition)}

    partner_id_map =mymap(db.Partner)
    agent_id_map =mymap(db.Agent)

    courier_id_map = {c.description:c.id for c in db.session.query(db.Courier)}
    warehouse_id_map = {w.description:w.id for w in db.session.query(db.Warehouse)}





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
        for e in description_id_map.inverse[line.item_id].split():
            if e.isdigit():
                capacities.add(e)
                break
    
    if len(capacities) == 1:
        capacity = capacities.pop() + 'GB'
    else:
        capacity = 'Mixed GB'
    
    colors = set()
    for line in lines:
        color = description_id_map.inverse[line.item_id].split()[-1]
        colors.add(color) 

    if len(colors) == 1:
        color = colors.pop()
    else:
        color = 'Mixed Color'
    
    line = lines[0]
    description = description_id_map.inverse[line.item_id] 
    manufacturer, category, model , *_ = description.split() 
    return ' '.join([
        manufacturer, category, model, 
        capacity, color 
    ])