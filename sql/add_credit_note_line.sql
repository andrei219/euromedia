-- Active: 1717667420056@@192.168.1.78@3306@euromedia

select    
    sp.`id` as proforma_id, si.id as `invoice_id`
from `sale_proformas` sp 
INNER join 
`sale_invoices` si 
on
    sp.`sale_invoice_id` = si.id 
where 
    si.type=2 and `si`.`number`=163 and YEAR(`si`.`date`) = 2025;


insert into `items`
(mpn, `manufacturer`, `category`, `model`, `capacity`, `color`, `has_serie`, `weight`, `battery_weight`)
VALUES
("", "", "Portes", "", "", "", 0, 0, 0);

commit; 

select * from `items` where `category`='Portes';

insert into `credit_note_lines` (
    `proforma_id`, `invoice_id`, `item_id`, `condition`, `public_condition`, `spec`, `quantity`, `price`, `tax`, `sn`, `created_on`
) values (
    5043, 3576, 1157, ' ', ' ', ' ', 1, -60, 21, ' ', now()  
); 


COMMIT;
