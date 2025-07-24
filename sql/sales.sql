select 
    es.serie ,
    si.TYPE ,
    si.number,
    si.date ,
    prt.fiscal_name,
    prt.`fiscal_number`,
    CONCAT_WS(' ',
        IFNULL(i.mpn, ''),
        IFNULL(i.manufacturer, ''),
        IFNULL(i.category, ''),
        IFNULL(i.model, ''),
        IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
        IFNULL(i.color, '')
    ),
    1 as CANTIDAD,
    spl.price * coalesce(spr.rate, 1)
    
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
    left join (
        select 
            `proforma_id`,
            `amount`/amount_converted as `rate`
        from (
            select 
                proforma_id,
                sum(`amount`) as amount,
                sum(`amount` * `rate`) as amount_converted
            from `sale_payments`
            group by proforma_id
        ) spr
        on spr.proforma_id = sp.id
    where `prt`.`id` = 22
union 
select 
    cnl.`sn` ,
    si.TYPE ,
    si.number ,
    si.date  ,
    prt.fiscal_name,
    prt.`fiscal_number`,
    CONCAT_WS(' ',
        IFNULL(i.mpn, ''),
        IFNULL(i.manufacturer, ''),
        IFNULL(i.category, ''),
        IFNULL(i.model, ''),
        IF(i.capacity IS NOT NULL, CONCAT(i.capacity, ' GB'), ''),
        IFNULL(i.color, '')
    ),
    1,
    cnl.price * COALESCE(spr.rate, 1)
from `credit_note_lines` cnl 
inner join `sale_invoices` si

    on `cnl`.`invoice_id` = `si`.`id`
inner join `sale_proformas` sp
    on `cnl`.`proforma_id` = `sp`.`id`
inner join `partners` prt
    on `prt`.`id` = `sp`.`partner_id`
inner join `items` i
    on `cnl`.`item_id` = `i`.`id`
left join (
    select 
        `proforma_id`,
        `amount`/amount_converted as `rate`
    from (
        select 
            proforma_id,
            sum(`amount`) as amount,
            sum(`amount` * `rate`) as amount_converted
        from `sale_payments`
        group by proforma_id
    ) spr
) `spr`
    on `spr`.`proforma_id` = `sp`.`id`
where `prt`.`id` = 22;

