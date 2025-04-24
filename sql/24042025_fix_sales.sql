# leaf1
# delete proforma advanced lines 
delete from `advanced_lines` al
where `al`.`proforma_id` = (
    select id FROM `sale_proformas`
    where `sale_proformas`.`sale_invoice_id` = (
        select id from `sale_invoices` si 
        where si.`type`=2 and si.`number`=128 and YEAR(si.`date`)='2025'
    )
)

# leaf 2
delete from `sale_proformas` sp
where `sp`.`sale_invoice_id` = (
    select id from `sale_invoices` si 
    where si.`type`=2 and si.`number`=128 and YEAR(si.`date`)='2025'
);


# pointed object 
delete from `sale_invoices` si
where si.`type`=2 and si.`number`=128 and YEAR(si.`date`)='2025';



update `sale_invoices` si
set si.`number`=128
where si.`type`=2 and si.`number`=129 and YEAR(si.`date`)='2025';


COMMIT;
