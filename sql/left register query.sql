use euromedia;

create temporary table if not exists temp_partners as
    select id, fiscal_name from partners;

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


# Delete trash payments:
delete from purchase_payments where amount = 0;

# Delete trash expenses
delete from purchase_expenses where amount = 0;

# Delete orphan lines:
delete from purchase_proforma_lines where proforma_id is null;

drop temporary table if exists temp_purchase_expenses; # proforma_id, total_expenses
drop temporary table if exists temp_purchase_payments; # proforma_id, total_paid, total_paid_rated, average
drop temporary table if exists temp_purchase_devices; # proforma_id, devices
drop temporary table if exists temp_purchase_debt; # proforma_id, total_debt
drop temporary table if exists temp_purchase_repr; # proforma_id, doc_repr, date
drop temporary table if exists temp_purchase_series; # proforma_id, serie, clean_repr, condition, spec, price


create temporary table temp_purchase_expenses as
    select
        purchase_proformas.id as proforma_id,
        coalesce(expenses,0) as total_expenses
    from purchase_proformas left outer join (
        select
            proforma_id,
            sum(amount) as expenses
        from (
            select
                proforma_id,
                amount
            from purchase_expenses
            union all
            select
                proforma_id,
                sum(quantity * price)
            from purchase_proforma_lines
            where item_id is null or not (description like '%ixed%')
            ) as t group by proforma_id

        ) as u on purchase_proformas.id = u.proforma_id
        where purchase_proformas.agent_id=5;

create temporary table temp_purchase_payments as
    select
        purchase_proformas.id as proforma_id,
        coalesce(amount, 0) as total_paid ,
        coalesce(amount_rated,0) as total_paid_rated,
        coalesce(average_rate, 1) as average_rate
    from purchase_proformas left join (
        select
            proforma_id,
            amount,
            amount_rated,
            amount/amount_rated as average_rate
         from (
            select
                proforma_id,
                sum(amount)        as amount,
                sum(amount/rate) as amount_rated
            from purchase_payments
            group by proforma_id ) as t

    ) as u on u.proforma_id = purchase_proformas.id
    where purchase_proformas.agent_id=5;

create temporary table temp_purchase_devices as
    select
        proforma_id,
        sum(quantity) as number_of_devices
    from purchase_proforma_lines
    where item_id is not null or description like '%ixed%'
    group by proforma_id;


create temporary table temp_purchase_debt as
    select
        proforma_id,
        sum(quantity * price * ( 1 + tax/100)) as total_debt
    from
        purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where purchase_proformas.agent_id=5
    group by
        proforma_id;

CREATE TEMPORARY TABLE temp_purchase_repr AS
SELECT
    id as proforma_id,
    CONCAT(type, '-', LPAD(number, 6, '0')) AS doc_repr,
    DATE_FORMAT(date, '%d/%m/%Y') AS date
FROM purchase_proformas
WHERE agent_id = 5;


create temporary table temp_purchase_series as
    select
        receptions.proforma_id as proforma_id,
        reception_series.serie as serie,
        temp_items.clean_repr as clean_repr,
        reception_series.`condition`as `condition`,
        reception_series.`spec` as spec,
        (
            select price
            from purchase_proforma_lines
            where proforma_id = receptions.proforma_id and
            `condition` = reception_lines.`condition` and
            `spec` = reception_lines.`spec` and
                (item_id = reception_lines.item_id or description = reception_lines.description)
        ) as price

    from
        reception_series
    inner join reception_lines on reception_series.line_id = reception_lines.id
    inner join receptions on reception_lines.reception_id = receptions.id
    inner join purchase_proformas on receptions.proforma_id = purchase_proformas.id
    inner join temp_items on reception_series.item_id = temp_items.id
    where purchase_proformas.agent_id = 5;


select
    temp_purchase_series.*,
    temp_purchase_expenses.*,
    temp_purchase_payments.*,
    temp_purchase_debt.*,
    temp_purchase_devices.*,
    temp_purchase_repr.*
from temp_purchase_series
    inner join temp_purchase_expenses on temp_purchase_series.proforma_id = temp_purchase_expenses.proforma_id
    inner join temp_purchase_payments on temp_purchase_series.proforma_id = temp_purchase_payments.proforma_id
    inner join temp_purchase_debt on temp_purchase_series.proforma_id = temp_purchase_debt.proforma_id
    inner join temp_purchase_repr on temp_purchase_series.proforma_id = temp_purchase_repr.proforma_id
    inner join temp_purchase_devices on temp_purchase_series.proforma_id = temp_purchase_devices.proforma_id
WHERE total_expenses != 0
order by temp_purchase_series.proforma_id;


# Delete trash payments:
delete from purchase_payments where amount = 0;

# Delete trash expenses
delete from purchase_expenses where amount = 0;

# Delete orphan lines:
delete from purchase_proforma_lines where proforma_id is null;


drop temporary table if exists temp_sale_expenses; # proforma_id, total_expenses
drop temporary table if exists temp_sale_payments; # proforma_id, total_paid, total_paid_rated, average
drop temporary table if exists temp_sale_devices; # proforma_id, devices
drop temporary table if exists temp_sale_debt; # proforma_id, total_debt
drop temporary table if exists temp_sale_repr; # proforma_id, doc_repr, date
drop temporary table if exists temp_sale_series; # proforma_id, serie, clean_repr, condition, spec, price
