
use euromedia; 
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
inner join sale_invoices si on si.id = sp.sale_invoice_id; 
-- where si.`date` BETWEEN :start_date AND :end_date; 


DESCRIBE sale_proformas; 