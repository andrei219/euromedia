import os 

from ui_itemized_invoices_form import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox

from issued_invoices_pdf_builder import build_document, PDF
from datetime import datetime

import utils
import db

import typing as tp
from collections.abc import Iterable

import abc 

import openpyxl
import itertools as it 


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

HEADER = ('Partner', 'Type', 'Number', 'Date', 'Item', 'Condition', 'Spec', 'Serie', 'Price')

class Writer(tp.Protocol): 
    def dump(self, data: tp.Iterable[tp.Tuple]): ...
class ExcelWriter: 
    def dump(self, path:str, data: tp.Iterable[tp.Tuple]) -> None:
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        for row in data:
            sheet.append(row)
        try:
            workbook.save(path)
        except (PermissionError, Exception):
            raise 

class StdoutWriter: 
    def dump(self, path: str, data: tp.Iterable[tp.Tuple]):
        for row in data:
            print(row)

# writer_factory = lambda: StdoutWriter() if os.getenv('APP_DEBUG') == 'true' else ExcelWriter()

writer_factory = lambda: ExcelWriter()

class Form(Ui_Dialog, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)

        utils.setCompleter(self.agent, tuple(utils.agent_id_map.keys()) + ('All',))
        utils.setCompleter(self.partner, tuple(utils.partner_id_map.keys()) + ('All', ))

        self._export.clicked.connect(self.export_handler)
        self.series_all.toggled.connect(self.all_checked)

        if os.getenv('APP_DEBUG') == 'true': 
            self._from.setText("01012024") 
        else:
            self._from.setText(f"01{utils.today_date()[2:]}")
    
        self.to.setText(utils.today_date())



    def all_checked(self, checked):
        for serie in range(1, 7):
            getattr(self, 'serie_' + str(serie)).setChecked(checked)
    

    def parse_period(self) -> tp.Tuple[datetime, datetime]:
        _from = self._from.text()
        to = self.to.text()
        if not all((_from, to)):
            mss = '' 
            if not _from:
                mss += 'From date is required. '
            if not to:
                mss += 'To date is required. '
            raise FilterValidationError(mss)
        try:
            _from = utils.parse_date(_from)
        except ValueError:
            raise FilterValidationError('From date format is incorrect. ddmmyyyy')
        try:
            to = utils.parse_date(to)
        except ValueError:
            raise FilterValidationError('To date format is incorrect. ddmmyyyy')

        if _from > to:
            raise FilterValidationError('From date is after To date')

        return _from, to 

    def build_filters(self): 
        return {
            'period': self.parse_period(),
            'partner_id': utils.partner_id_map.get(self.partner.text(), None),
            'agent_id': utils.agent_id_map.get(self.agent.text(), None),
            'series': [
                i 
                for i in range(1, 7)
                if getattr(self, f'serie_{i}').isChecked()
            ]
        } 

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
            inner join expedition_lines el 
                on es.line_id = el.id
            inner join items i 
                on el.item_id = i.id
            inner join expeditions e 
                on el.expedition_id = e.id
            inner join sale_proformas sp
                on e.proforma_id = sp.id
            inner join ( -- build sale lines from both types: advanced and normal 
                select 
                    proforma_id,
                    item_id,
                    `condition`,
                    `spec`,
                    price
                from sale_proforma_lines sl
                union 
                select 
                    proforma_id,
                    item_id,
                    `condition`,
                    `spec`,
                    price
                from advanced_lines al 
            ) spl
                on spl.proforma_id=sp.id
                and spl.`item_id` = el.`item_id`
                and spl.`condition` = el.`condition`
                and spl.`spec` = el.`spec`
            inner join partners prt 
                on prt.id = sp.partner_id
            inner join sale_invoices si 
                on si.id = sp.sale_invoice_id
        """
        _from, to = filters.get('period')

        mysql_from_promoted = f"{_from.year}-{_from.month}-{_from.day}"
        mysql_to_promoted = f"{to.year}-{to.month}-{to.day}"

        sql += f" where si.date between '{mysql_from_promoted}' and '{mysql_to_promoted}'"

        parnter_id = filters.get('partner_id', None)
        if parnter_id is not None:
            sql += f" and sp.partner_id = {parnter_id}"

        agent_id = filters.get('agent_id', None)
        if agent_id is not None:
            sql += f" and sp.agent_id = {agent_id}"

        series = filters.get('series', None)
        if series is not None and len(series) > 0:
            sql += f" and si.type in ({','.join(map(str, series))})"

        return sql

    def export_handler(self):
        try:
            sql = self.get_query(filters=self.build_filters()) 
        except FilterValidationError as ex:
            QMessageBox.critical(self, 'Validation Error', str(ex))
            return
    
        try:
            # be lazy:
            data = map(tuple, it.chain((HEADER, ), db.session.execute(sql))) 
        except Exception as ex: 
            QMessageBox.critical(self, 'Database Error', str(ex))
            db.session.rollback()
            return
        
        try:
            filepath = utils.get_file_path(self)
        except Exception as ex:
            QMessageBox.critical(self, 'File Error', str(ex))
            return

        writer = writer_factory()
        try:
            writer.dump(filepath, map(tuple, data)) 
        except Exception as ex:
            QMessageBox.critical(self, 'File Error', str(ex))
            return

        QMessageBox.information(self, 'Success', 'Data exported successfully')