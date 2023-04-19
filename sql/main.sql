
use euromedia;

drop temporary table if exists temp_items; # id, clean_repr

CREATE TEMPORARY TABLE if not exists temp_items AS
SELECT
    id,
    CONCAT_WS(' ',
        IFNULL(mpn, ''),
        IFNULL(manufacturer, ''),
        IFNULL(category, ''),
        IFNULL(model, ''),
        IF(capacity IS NOT NULL, CONCAT(capacity, ' GB'), ''),
        IFNULL(color, '')
    ) AS clean_repr
FROM items;


drop temporary table if exists temp_purchase_partners; # proforma_id, partner_name
drop temporary table if exists temp_purchase_expenses_eur; # proforma_id, sum(expenses.amount)
drop temporary table if exists temp_purchase_expenses_cur; # proforma_id, expenses in lines
drop temporary table if exists temp_purchase_payments; # proforma_id, total_paid, total_paid_rated, average
drop temporary table if exists temp_purchase_devices; # proforma_id, devices
drop temporary table if exists temp_purchase_debt; # proforma_id, total_debt
drop temporary table if exists temp_purchase_repr; # proforma_id, doc_repr, date
drop temporary table if exists temp_purchase_series; # proforma_id, serie, clean_repr, condition, spec, price
drop temporary table if exists left_side_base;

# Delete trash:
delete from purchase_payments where amount=0;
delete from purchase_expenses where amount=0;


create temporary table if not exists temp_purchase_partners as
    select
        purchase_proformas.id as proforma_id,
        partners.fiscal_name as partner_name
    from purchase_proformas inner join partners on purchase_proformas.partner_id = partners.id;


create temporary table if not exists temp_purchase_expenses_eur as
    select
        purchase_expenses.proforma_id as proforma_id,
        sum(purchase_expenses.amount) as expenses_eur
    from purchase_expenses group by purchase_expenses.proforma_id;


