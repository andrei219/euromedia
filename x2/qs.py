# coding: utf-8


ss = "SELECT DISTINCT F_SLF.NSESLF AS SERIE FROM F_SLF"


clients = """
    SELECT DISTINCT
        F_FAC.CLIFAC AS CID, 
        F_FAC.CNOFAC AS CNAME
    FROM 
        F_SLF, F_LFA, F_FAC
    WHERE 
        F_LFA.TIPLFA = F_SLF.TIPSLF AND
        F_LFA.CODLFA = F_SLF.CODSLF AND
        F_LFA.POSLFA = F_SLF.POSSLF AND
        F_FAC.TIPFAC = F_LFA.TIPLFA AND
        F_FAC.CODFAC = F_LFA.CODLFA;
"""

salesq = """
SELECT 
    F_SLF.NSESLF AS SERIE,
    F_FAC.TIPFAC AS TIPO_VENTA,
    F_FAC.CODFAC AS NUMERO_VENTA,
    F_FAC.FECFAC AS FECHA_VENTA,
    F_FAC.CNOFAC AS CLIENTE,
    F_FAC.CNIFAC AS CLIENTE_NIF,
    F_LFA.DESLFA AS ARTICULO,
    F_LFA.CANLFA AS CANTIDAD,
    F_LFA.PRELFA AS PRECIO_VENTA
FROM 
    F_SLF, F_LFA, F_FAC
WHERE 
    F_LFA.TIPLFA = F_SLF.TIPSLF AND
    F_LFA.CODLFA = F_SLF.CODSLF AND
    F_LFA.POSLFA = F_SLF.POSSLF AND
    F_FAC.TIPFAC = F_LFA.TIPLFA AND
    F_FAC.CODFAC = F_LFA.CODLFA AND 
    F_FAC.CLIFAC = {client}
"""

purchq ="""
SELECT 
    F_SLR.NSESLR AS SERIE,
    F_FRE.TIPFRE AS TIPO_COMPRA,
    F_FRE.CODFRE AS NUMERO_COMPRA,
    F_FRE.FECFRE AS FECHA_COMPRA,
    F_FRE.PNOFRE AS PROVEEDOR,
    F_FRE.FACFRE AS DOCUMENTO_PROVEEDOR,
    F_LFR.CANLFR AS CANTIDAD,
    F_LFR.PRELFR AS PRECIO_COMPRA
FROM 
    F_SLR, F_LFR, F_FRE
WHERE 
    F_LFR.TIPLFR = F_SLR.TIPSLR AND
    F_LFR.CODLFR = F_SLR.CODSLR AND
    F_LFR.POSLFR = F_SLR.POSSLR AND
    F_FRE.TIPFRE = F_LFR.TIPLFR AND
    F_FRE.CODFRE = F_LFR.CODLFR
"""



clients = "select distinct id, fiscal_name from partners"


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
    '1' as CANTIDAD,
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
    '1' as CANTIDAD,
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

"""

purchq = """
"""

