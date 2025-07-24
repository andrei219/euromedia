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