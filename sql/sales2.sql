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
where prt.id is not null

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
where prt.id is not null;