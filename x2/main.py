"""
    Target:
        start with sales
        join wit purchase 
         
    tables of interest:
        F_FAC - facturas emitidas 
        F_FRE - facturas recibidas
        F_LFA - lineas facturas emitidas
        F_LFR - lineas facturas recibidas
       
        related to series 
        F_SLC [E] numeros de serie 
        F_SLF [E] numeros de serie
        F_SLR [E] numeros de serie - sospecho recibidas 

        
        F_FRE <- F_LFR <- F_SLR
        F_FAC <- F_LFA <- F_SLF


        We need to join data sets via the serie.
        the datasets are sales, and purchases. 
        
        sales can be found in the relations:
            F_FAC <- F_LFA <- F_SLF
        purchases can be found in the relations:
            F_FRE <- F_LFR <- F_SLR

        Relations with attributes:
            F_SLF (TIPSLF, CODSLF, POSSLF, NSESLF)
            F_LFA (TIPLFA, CODLFA,
"""

    
"""
    FINAL HEADER:
        FACTURA, 
        FECHA 
        CIENTE
        NIF 
        SERIE
        DEWSCRIPTION
        CANTIDAD
        PRECIO
        PROVEEDOR
        NIF
        FACTURA
        PRECIO COMPRA 

"""

import typing 

from openpyxl import Workbook, load_workbook
import qs 
import re 
import itertools 

import collections

import sys 
import os 

from openpyxl.utils import escape
import re

import functools


_illegal_chars_re = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


_illegal_windows_chars = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


# MODIFY SYS PATH TO FIND THE DB SESSION HANDLE 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


from app.db import session 


def norm_filename(name: str) -> str:
    """Sanitize string for safe use as a Windows filename."""
    if not isinstance(name, str):
        name = str(name)

    name = name.strip()
    name = _illegal_windows_chars.sub("_", name)
    
    # Remove trailing periods/spaces (not allowed in Windows)
    name = re.sub(r"[. ]+$", "", name)
    
    # Optional: truncate to max Windows filename length (255 characters)
    return name[:255]



def clean_excel_str(value: str) -> str:
    if not isinstance(value, str):
        return value
    
    return _illegal_chars_re.sub("", value)


def norm(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_*\-]", "", s).lower().strip()


def precur(iterable):
    prefixes = [] 
    for item in iterable:
        prefixes.append(item)
        yield tuple(prefixes), item
        

purchase_headers = [
    'Serie', 'Tipo', 'Numero', 'Fecha', 'Proveedor', 'Documento Externo', 'Cantidad', 'Precio'
]
sale_headers = [
    'Serie', 'Tipo', 'Numero', 'Fecha', 'Cliente', 'NIF', 'Articulo', 'Cantidad', 'Precio'
]

headers = purchase_headers + sale_headers

def write_report(rows, year, client, infix):
    client_dir = norm_filename(client)

    out_dir = os.path.join("out", infix, client_dir, str(year))

    print('Writing report to: ', out_dir)

    os.makedirs(out_dir, exist_ok=True)

    # Create new workbook and worksheet
    wb = Workbook()
    ws = wb.active


    purchase_headers = [
        'Serie', 'Tipo', 'Numero', 'Fecha', 'Proveedor', 'Documento Externo', 'Cantidad', 'Precio'
    ]
    sale_headers = [
        'Serie', 'Tipo', 'Numero', 'Fecha', 'Cliente', 'NIF', 'Articulo', 'Cantidad', 'Precio'
    ]

    headers = purchase_headers + sale_headers

    ws.append(headers)

    # Write rows, cleaning cell values
    for row in sorted(filter(lambda r: r[9] and r[10], rows), key=lambda r: (r[9], r[10])):
        ws.append([clean_excel_str(cell) for cell in row])

    # Save file
    filename = os.path.join(out_dir, "harvest.xlsx")
    wb.save(filename)



def build_blocks(tree: dict[str, dict[str, set[tuple]]]):
    
    SALES_LEN=9
    PURCHASES_LEN=8
    for serie in tree:

        pr = tree[serie]['purchases']
        sr = tree[serie]['sales']

        if not len(sr) >= 1:
            continue

        

        for p, s in itertools.zip_longest(pr, sorted(sr, key=lambda x: x[3])):
            if p is None:
                p = (0,) * PURCHASES_LEN
            if s is None:
                s = (0,) * SALES_LEN


            if p[6] is not None and p[7] is not None:
                p_sign = (p[6] > 0) - (p[6] < 0)
                p = p[:6] + (p_sign, p_sign * p[7])
            else:
                p = p[:6] + (None, None)

            if s[7] is not None and s[8] is not None:
                s_sign = (s[7] > 0) - (s[7] < 0)
                s = s[:7] + (s_sign, s_sign * s[8])
            else:
                s = s[:7] + (None, None)

            yield p + s

# 9, 10 combinados 

@functools.lru_cache
def get_purchase():
    return list(db.Connection(year=year).execute(db.purchq))

@functools.lru_cache
def get_purchases(prevyears:tuple):
    return [get_purchase(year) for year in prevyears]


@functools.lru_cache
def get_sales(client_id:int):
    return db.Connection(year=year).execute(db.salesq.format(client=client_id))

def gen_rows(prevyears:tuple, year:int, client_id:int):
   
    sales: list = get_sales(client_id, year)
    prevpur: list[list] = get_purchases(prevyears)

    # Build tree for fast access
    tree = collections.defaultdict(lambda: collections.defaultdict(set))
    
    for p in map(tuple, itertools.chain(*prevpur)):
        tree[norm(p[0])]['purchases'].add(p)

    for s in map(tuple, sales): 
        tree[norm(s[0])]['sales'].add(s)
    

    yield from build_blocks(tree)


def test_write_report(rows, year):

    for row in rows:
        pass # run the thing


ENV: dict = {
    'test': {
        'write_report': write_report, 
        'years': [2020, 2021]
    }, 
    'live': {
        'write_report': write_report,
        'years': [2018, 2019, 2020, 2021, 2022]
    }, 
    'first': {
        'write_report': write_report,
        'years': [2018, 2019]
    }
}

class Environ:
    def __init__(self, env):
        self.env = env
    def __getattr__(self, name):
        return ENV[self.env][name]


def read_clients(): 
    return session.execute(qs.clients)


def main():
    environ =  Environ(env=sys.argv[1]) 
    infix = sys.argv[2]

    for cid, cname in read_clients(current):
        # print(prev, current, cid, cname)

        environ.write_report(
            gen_rows(prev, current, cid), 
            year=current, 
            client=cname, 
            infix=infix
        )


if __name__ == "__main__":
    for cid, cname in read_clients():
        print(f"Processing client ........... {cname} ({cid})")




