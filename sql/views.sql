
drop view if EXISTS purchase_payments_rate;
drop view if EXISTS sale_payments_rate;

create view sale_payments_rate as
select 
    `proforma_id`
    ,`amount`/amount_converted as `rate`
    from (
     select 
        proforma_id
        ,sum(`amount`) as amount
        ,sum(`amount` * `rate`) as amount_converted
    from `sale_payments` sp
    group by proforma_id
) as tmp;

create View purchase_payments_rate as
select 
    `proforma_id`
    ,`amount`/amount_converted as `rate`
    from (
        select 
            proforma_id
            ,sum(`amount`) as amount
            ,sum(`amount` * `rate`) as amount_converted
        from `purchase_payments` pp
        group by proforma_id
    ) as tmp;

COMMIT;