
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

from db import Courier, Warehouse, Agent, Item
from db import engine, Session

# Sqalchemy 
from sqlalchemy.sql import select, func

countries = list(dict(countries_for_language("en")).values())

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
    text, ok = QInputDialog.getText(parent, 'Tracking', f'Enter tracking number for {type_num}:')
    if text and ok:
        return text 

def getNote(parent, proforma):
    type_num = str(proforma.type) + '-' + str(proforma.number).zfill(6)
    text, ok = QInputDialog.getText(parent, 'Warehouse', 'Enter a warning for the warehouse order')
    if text and ok:
        return text


def build_description(item:Item):
    return ' '.join([item.manufacturer, item.category, item.model, item.capacity, 'GB', \
        item.color])


def parse_date(string):
    if len(string) != 8:
        raise ValueError
    day, month, year = int(string[0:2]), int(string[2:4]), int(string[4:8]) 
    return datetime(year, month, day)


def today_date():
    return datetime.now().strftime('%d%m%Y')



def buildMapsAndCombos(self):
    self.courier_name_to_courier_map = {courier.description:courier for courier in self.session.\
        query(Courier)}

    self.agentname_to_agent_map = {agent.fiscal_name:agent for agent in self.session.\
        query(Agent).where(Agent.active == True)}
    
    self.warehouse_name_to_warehouse_map = {warehouse.description:warehouse for warehouse in \
        self.session.query(Warehouse)}

    self.taxname_to_tax_map = {tax.quantity:tax for tax in self.session.query(Tax)}

    self.courier_combobox.addItems(self.courier_name_to_courier_map.keys())
    self.agent_combobox.addItems(self.agentname_to_agent_map.keys())
    self.warehouse_combobox.addItems(self.warehouse_name_to_warehouse_map.keys())
    self.tax_combobox.addItems([str(v) for v in self.taxname_to_tax_map.keys()]) 