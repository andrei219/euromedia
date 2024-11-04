from ui_itemized_invoices_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from issued_invoices_pdf_builder import build_document, PDF
from datetime import datetime

import utils
import db

import typing as tp


class FilterValidationError(Exception):
    pass 

sql = """
    select 
    prt.fiscal_name, 
    si.TYPE, 
    si.number, 
    si.date, 
    CONCAT_WS(' ',
        IFNULL(i.mpn, ''),
        IFNULL(i.manufacturer, ''),
        IFNULL(i.category, ''),
        IFNULL(i.model, ''),
        IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
        IFNULL(i.color, '')
    ) as clean_repr,
    spl.condition, 
    spl.spec, 
    es.serie, 
    spl.price
    from expedition_series es 
    inner join expedition_lines el on es.line_id = el.id
    inner join items i on el.item_id = i.id
    inner join expeditions e on el.expedition_id = e.id
    inner join sale_proformas sp on sp.id = e.proforma_id
    inner join sale_proforma_lines spl on spl.proforma_id=sp.id
    inner join partners prt on prt.id = sp.partner_id 
    inner join sale_invoices si on si.id = sp.sale_invoice_id
"""


def update_query(bsae_sql: str, filters: dict):
    pass 


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        utils.setCompleter(self.agent, tuple(utils.agent_id_map.keys()) + ('All',))
        utils.setCompleter(self.partner, tuple(utils.partner_id_map.keys()) + ('All', ))

        self._export.clicked.connect(self.export_handler)
        self.series_all.toggled.connect(self.all_checked)

    def all_checked(self, checked):
        for serie in range(1, 7):
            getattr(self, 'serie_' + str(serie)).setChecked(checked)
    
    def update_query(base_sql: str, filters: dict):
        return base_sql 
    

    def parse_filters(self): 
        filters = {}
        _from = self._from.text()
        to = self.to.text()
        if not all((_from, to)):
            raise FilterValidationError('From and to dates are required')
        filters['period'] = (_from, to)



    def get_query(self, filters: dict[str, tp.Any]) -> str:
        sql = """
            select 
            prt.fiscal_name, 
            si.TYPE, 
            si.number, 
            si.date, 
            CONCAT_WS(' ',
                IFNULL(i.mpn, ''),
                IFNULL(i.manufacturer, ''),
                IFNULL(i.category, ''),
                IFNULL(i.model, ''),
                IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
                IFNULL(i.color, '')
            ) as clean_repr,
            spl.condition, 
            spl.spec, 
            es.serie, 
            spl.price
            from expedition_series es 
            inner join expedition_lines el on es.line_id = el.id
            inner join items i on el.item_id = i.id
            inner join expeditions e on el.expedition_id = e.id
            inner join sale_proformas sp on sp.id = e.proforma_id
            inner join sale_proforma_lines spl on spl.proforma_id=sp.id
            inner join partners prt on prt.id = sp.partner_id 
            inner join sale_invoices si on si.id = sp.sale_invoice_id
        """ 

        _from, to = filters.get('period')




    def export_handler(self):
        
        QMessageBox.information(self, 'Information', 'Not implemented yet. Working on it ...')
        return 
        
        try:
            filters = self.parse_filters()
        except FilterValidationError as e:
            QMessageBox.critical(self, 'Error', str(e))
            return

        sql = self.get_query(filters=self.parse_filters())

        data = db.session.execute(sql).fetchall()