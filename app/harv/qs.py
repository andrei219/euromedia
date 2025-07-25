# coding: utf-8

partners = "select distinct id, fiscal_name from partners"

partners = """
    select distinct p.id, p.fiscal_name
    from partners p
    inner join sale_proformas sp on p.id = sp.partner_id
"""

salesq ="""

with
items_cte as (
    select
        i.id as item_id,
        concat_ws(' ',
            ifnull(i.mpn, ''),
            ifnull(i.manufacturer, ''),
            ifnull(i.category, ''),
            ifnull(i.model, ''),
            if(i.capacity is not null, concat(i.capacity, ' gb'), ''),
            ifnull(i.color, '')
        ) as articulo
    from items i
),
sale_payments_rate as (
    select
        t.proforma_id,
        t.amount / t.amount_converted as rate
    from (
        select
            proforma_id,
            sum(amount) as amount,
            sum(amount * rate) as amount_converted
        from sale_payments
        group by proforma_id
    ) as t
) select 
    es.serie,
    si.type,
    si.number,
    si.date,
    prt.fiscal_name,
    prt.fiscal_number,
    ic.articulo,
    1 as cantidad,
    spl.price * coalesce(spr.rate, 1) as precio_venta
from expedition_series es
inner join expedition_lines el 
    on es.line_id = el.id
inner join items_cte ic
    on ic.item_id = el.item_id
inner join expeditions e 
    on el.expedition_id = e.id
inner join sale_proformas sp
    on e.proforma_id = sp.id
inner join (
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
    on spl.proforma_id = sp.id
    and spl.item_id = el.item_id
    and spl.`condition` = el.`condition`
    and spl.`spec` = el.`spec`
inner join partners prt 
    on prt.id = sp.partner_id
inner join sale_invoices si 
    on si.id = sp.sale_invoice_id
left join sale_payments_rate spr
    on spr.proforma_id = sp.id
where prt.id = {partner_id}
union
select 
    cnl.sn,
    si.type,
    si.number,
    si.date,
    prt.fiscal_name,
    prt.fiscal_number,
    ic.articulo,
    1 as cantidad,
    cnl.price * coalesce(spr.rate, 1) as precio_venta
from credit_note_lines cnl
inner join sale_invoices si
    on cnl.invoice_id = si.id
inner join sale_proformas sp
    on cnl.proforma_id = sp.id
inner join partners prt
    on prt.id = sp.partner_id
inner join items_cte ic
    on cnl.item_id = ic.item_id
left join sale_payments_rate spr
    on spr.proforma_id = sp.id
where prt.id = {partner_id};

"""

purchq = """
SELECT 
    rs.`serie` 
    ,pi.`type` 
    ,pi.`number` 
    ,pi.`date` 
    ,prt.`fiscal_name` 
    ,pp.`external`
    ,1 
    ,ppp.`price` * COALESCE(ppr.rate, 1)
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
left join (
    
    select 
    `proforma_id`
    ,`amount`/amount_converted as `rate`
    from (
        select 
            proforma_id
            ,sum(`amount`) as amount
            ,sum(`amount` * `rate`) as amount_converted
        from `purchase_payments` 
        group by proforma_id
    ) as ppr
)  ppr on ppr.proforma_id = pp.id
"""
