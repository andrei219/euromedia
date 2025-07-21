# coding: utf-8

partners = "select distinct id, fiscal_name from partners"

partners = """
    select distinct p.id, p.fiscal_name
    from partners p
    inner join sale_proformas sp on p.id = sp.partner_id
"""
salesq ="""

 select 
    es.serie AS SERIE,
    si.TYPE as TIPO_VENTA,
    si.number as NUMERO_VENTA,
    si.date as FECHA_VENTA,
    prt.fiscal_name as CLIENTE,
    prt.`fiscal_number` as CLIENTE_NIF,
    CONCAT_WS(' ',
        IFNULL(i.mpn, ''),
        IFNULL(i.manufacturer, ''),
        IFNULL(i.category, ''),
        IFNULL(i.model, ''),
        IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
        IFNULL(i.color, '')
    ) as ARTICULO,
    1 as CANTIDAD,
    spl.price as PRECIO_VENTA
    from expedition_series es
    inner join expedition_lines el 
        on es.line_id = el.id
    inner join items i 
        on el.item_id = i.id
    inner join expeditions e 
        on el.expedition_id = e.id
    inner join sale_proformas sp
        on e.proforma_id = sp.id
    
    inner join ( -- build sale lines al and spl 
       select 
            sl.proforma_id,
            sl.item_id,
            sl.`condition`,
            sl.`spec`,
            sl.price
        from sale_proforma_lines sl
        union 
        select 
            al.proforma_id,
            al.item_id,
            al.`condition`,
            al.`spec`,
            al.price
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
    where `prt`.`id` = {partner_id}
union 
select 
    cnl.`sn` AS SERIE,
    si.TYPE as TIPO_VENTA,
    si.number as NUMERO_VENTA,
    si.date as FECHA_VENTA,
    prt.fiscal_name as CLIENTE,
    prt.`fiscal_number` as CLIENTE_NIF,
    CONCAT_WS(' ',
        IFNULL(i.mpn, ''),
        IFNULL(i.manufacturer, ''),
        IFNULL(i.category, ''),
        IFNULL(i.model, ''),
        IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
        IFNULL(i.color, '')
    ) as ARTICULO,
    1 as CANTIDAD,
    cnl.price as PRECIO_VENTA
from `credit_note_lines` cnl 
inner join `sale_invoices` si

    on `cnl`.`invoice_id` = `si`.`id`
inner join `sale_proformas` sp
    on `cnl`.`proforma_id` = `sp`.`id`
inner join `partners` prt
    on `prt`.`id` = `sp`.`partner_id`
inner join `items` i
    on `cnl`.`item_id` = `i`.`id`
where `prt`.id = {partner_id};

"""

purchq = """
SELECT 
    rs.`serie` 
    ,pi.`type` 
    ,pi.`number` 
    ,pi.`date` 
    ,prt.`fiscal_name` 
    ,prt.`fiscal_number`
 
    ,1 
    ,ppp.`price`
FROM `reception_series` rs 
inner join `reception_lines` rl 
    on rs.line_id = rl.id 
inner join `receptions` r 
    on rl.reception_id = r.id
inner join `purchase_proformas` pp
    on r.`proforma_id` = pp.id
inner join `purchase_proforma_lines` ppp
    on 
        ppp.proforma_id = pp.id and 
        COALESCE(ppp.item_id, -1) = COALESCE(rl.item_id, -1) and
        COALESCE(ppp.description, -1) = COALESCE(rl.description, -1) and
        ppp.condition = rl.condition and
        ppp.spec = rl.spec
left join items i 
    on ppp.item_id = i.id 

inner join `purchase_invoices` pi 
    on pp.`invoice_id` = pi.id
inner join `partners` prt 
    on pp.partner_id = prt.id
"""
