-- Active: 1726845028798@@127.0.0.1@3306@euromedia

with payments as (
    select 
        proforma_id
        ,sum(`amount`) as amount
        ,sum(`amount` * `rate`) as amount_converted
    from `purchase_payments` 
    group by proforma_id
)
select *
from payments;

# canceladas fuera, 
select *
from `purchase_payments` 
where proforma_id = 1234s