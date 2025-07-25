import sys, os 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


import typing
import collections
import functools
import itertools
import os
import re
import sys

from openpyxl import Workbook
from openpyxl.utils import escape
from app.db import session
import qs

_illegal_chars_re = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
_illegal_windows_chars = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

def norm_filename(name: str) -> str:
    if not isinstance(name, str):
        name = str(name)
    name = name.strip()
    name = _illegal_windows_chars.sub("_", name)
    return re.sub(r"[. ]+$", "", name)[:255]

def clean_excel_str(value: str) -> str:
    if not isinstance(value, str):
        return value
    return _illegal_chars_re.sub("", value)

def norm(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_*\-]", "", s).lower().strip()

def build_blocks(tree: dict[str, dict[str, set[tuple]]]):
    SALES_LEN = 9
    PURCHASES_LEN = 8

    for serie in tree:
        pr = tree[serie]['purchases']
        sr = tree[serie]['sales']
        if not sr:
            continue


        for p, s in itertools.zip_longest(pr, sorted(sr, key=lambda x: x[3])):
            p = p if p else (0,) * PURCHASES_LEN
            s = s if s else (0,) * SALES_LEN

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

@functools.lru_cache
def get_purchases():
    return session.execute(qs.purchq)

@functools.lru_cache
def get_sales(partner_id: int):
    return session.execute(qs.salesq.format(partner_id=partner_id))

def gen_rows(partner_id: int):
    sales = list(map(tuple, get_sales(partner_id)))
    purchases = list(map(tuple, get_purchases()))

    tree = collections.defaultdict(lambda: collections.defaultdict(set))
    for p in purchases:
        tree[norm(p[0])]['purchases'].add(p)
    for s in sales:
        tree[norm(s[0])]['sales'].add(s)

    yield from build_blocks(tree)

def write_report(rows, partner, infix):
    partner_dir = norm_filename(partner)
    out_dir = os.path.join("out", infix, partner_dir)
    os.makedirs(out_dir, exist_ok=True)
    print('Writing report to:', out_dir)

    wb = Workbook()
    ws = wb.active

    purchase_headers = ['Serie', 'Tipo', 'Numero', 'Fecha', 'Proveedor', 'Documento Externo', 'Cantidad', 'Precio']
    sale_headers = ['Serie', 'Tipo', 'Numero', 'Fecha', 'Cliente', 'NIF', 'Articulo', 'Cantidad', 'Precio']
    ws.append(purchase_headers + sale_headers)

    for row in sorted(filter(lambda r: r[9] and r[10], rows), key=lambda r: (r[9], r[10])):
        ws.append([clean_excel_str(cell) for cell in row])

    wb.save(os.path.join(out_dir, "harvest.xlsx"))

def read_partners():
    return session.execute(qs.partners)

def main():
    infix = sys.argv[1]
    for pid, pname in read_partners():
        print(f"Processing partner: {pname} ({pid})")
        write_report(gen_rows(pid), partner=pname, infix=infix)

        break

if __name__ == "__main__":

    # MODIFY SYS PATH TO FIND THE DB SESSION HANDLE 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)


    main()
