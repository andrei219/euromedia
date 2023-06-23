
drop  table if exists temp_purchase_partners; # proforma_id, partner_name
drop  table if exists temp_purchase_expenses_eur; # proforma_id, sum(expenses.amount)
drop  table if exists temp_purchase_expenses_inv; # proforma_id, expenses in lines
drop  table if exists temp_purchase_payments; # proforma_id, paid, paid_rated
drop  table if exists temp_purchase_devices; # proforma_id, devices
drop  table if exists temp_purchase_debt; # proforma_id, total_debt
drop  table if exists temp_purchase_repr; # proforma_id, doc_repr, date
drop  table if exists temp_purchase_series; # proforma_id, description item_id, condition, spec, serie
drop  table if exists temp_purchase_lines; # proforma_id, description, item_id, condition, spec, price
drop  table if exists temp_purchase_series_cost; # proforma_id, serie, price
drop  table if exists temp_purchase_currency_rate; # proforma_id, cur(code)
drop  table if exists left_numbered;
drop table if exists left_side_base; # proforma_id, serie, expenses_eur, expenses_inv, cost, currency, rate

delete from purchase_payments where amount=0;
delete from purchase_expenses where amount=0;

create  table if not exists temp_purchase_partners as
    select
        purchase_proformas.id as proforma_id,
        partners.fiscal_name as partner_name
    from purchase_proformas inner join partners on purchase_proformas.partner_id = partners.id;


create  table if not exists temp_purchase_expenses_eur as
    select
        purchase_expenses.proforma_id as proforma_id,
        sum(purchase_expenses.amount) as expenses_eur
    from purchase_expenses
    inner join purchase_proformas
    on purchase_expenses.proforma_id = purchase_proformas.id
    group by purchase_expenses.proforma_id;

create  table if not exists temp_purchase_expenses_inv as
    select
        proforma_id,
        sum(quantity * price) as expenses_inv
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where `condition` is null
    group by proforma_id;

create  table if not exists temp_purchase_payments as
    select
        proforma_id,
        sum(amount) as paid,
        sum(amount/rate) as paid_rated
    from purchase_payments
    inner join purchase_proformas
    on purchase_payments.proforma_id = purchase_proformas.id
    group by proforma_id;

create  table if not exists temp_purchase_devices as
    select
        proforma_id,
        sum(quantity) as devices
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where `condition` is not null
    group by proforma_id;

create  table if not exists temp_purchase_debt as
    select
        proforma_id,
        sum(quantity * price * ( 1 + tax/100)) as debt
    from purchase_proforma_lines inner join purchase_proformas
    on purchase_proforma_lines.proforma_id = purchase_proformas.id
    group by proforma_id;


create  table temp_purchase_lines as
    select
        purchase_proforma_lines.proforma_id as proforma_id,
        purchase_proforma_lines.description as description,
        purchase_proforma_lines.item_id as item_id,
        purchase_proforma_lines.condition as `condition`,
        purchase_proforma_lines.spec as spec,
        purchase_proforma_lines.price as price
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where purchase_proforma_lines.`condition` is not null;

create  table temp_purchase_series as
    select
        reception_series.serie,
        reception_lines.description as description,
        reception_lines.item_id as item_id,
        reception_lines.condition as `condition`,
        reception_lines.spec as spec,
        receptions.proforma_id as proforma_id
    from reception_series
    inner join reception_lines on reception_series.line_id = reception_lines.id
    inner join receptions on reception_lines.reception_id = receptions.id
    inner join purchase_proformas on receptions.proforma_id = purchase_proformas.id;


create  table temp_purchase_series_cost as
    select temp_purchase_lines.proforma_id as proforma_id, serie, price as cost
    from temp_purchase_series inner join temp_purchase_lines
    on temp_purchase_series.proforma_id = temp_purchase_lines.proforma_id
    and coalesce(temp_purchase_series.description, 0) = coalesce(temp_purchase_lines.description, 0)
    and coalesce(temp_purchase_series.item_id, 0) = coalesce(temp_purchase_lines.item_id, 0)
    and temp_purchase_series.`condition` = temp_purchase_lines.`condition`
    and temp_purchase_series.spec = temp_purchase_lines.spec;

create  table if not exists temp_purchase_currency_rate as
    select
        purchase_proformas.id as proforma_id,
        case
            when coalesce(paid, 0) = 0 and eur_currency = 1 then 'EUR'
            when coalesce(paid, 0) = 0 and eur_currency = 0 then 'USD'
            when coalesce(paid, 0) = coalesce(paid_rated, 0) and paid_rated != 0 then 'EUR'
            when coalesce(paid, 0) <> coalesce(paid_rated, 0) and paid_rated != 0 then 'USD'
        END as currency,
        coalesce(debt, 0) as debt,
        coalesce(paid, 0) as paid,
        coalesce(paid_rated, 0) as paid_rated,
        coalesce(paid/paid_rated, 1) as rate
    from purchase_proformas
        left join temp_purchase_payments on temp_purchase_payments.proforma_id = purchase_proformas.id
        left join temp_purchase_debt on temp_purchase_debt.proforma_id = purchase_proformas.id;


create table if not exists left_side_base as
    select
        temp_purchase_series_cost.proforma_id,
        temp_purchase_series_cost.serie as serie,
        coalesce(expenses_eur/devices,0) as expenses_eur,
        coalesce((expenses_inv/rate)/devices, 0) as expenses_inv,
        cost/rate as cost,
        IF(currency = 'USD' and rate <> 1, 'EUR', currency) as currency,
        rate

    from temp_purchase_series_cost

        left join temp_purchase_expenses_inv on temp_purchase_expenses_inv.proforma_id = temp_purchase_series_cost.proforma_id
        left join temp_purchase_expenses_eur on temp_purchase_expenses_eur.proforma_id = temp_purchase_series_cost.proforma_id
        inner join temp_purchase_currency_rate on temp_purchase_currency_rate.proforma_id = temp_purchase_series_cost.proforma_id
        inner join temp_purchase_devices on temp_purchase_devices.proforma_id = temp_purchase_series_cost.proforma_id;

select * from left_side_base;

drop function if exists get_stock_value;
CREATE FUNCTION get_stock_value(END_DATE DATE)
RETURNS DECIMAL(18, 2)
DETERMINISTIC
BEGIN
    declare stock_value decimal(18, 2);
    select sum(cost) into stock_value
    from left_side_base
    inner join (
        select distinct serie
        from (
            SELECT serie
            FROM reception_series
            WHERE DATE(created_on) <= END_DATE
            UNION
            SELECT SN AS SERIE
            FROM credit_note_lines
            WHERE DATE(created_on) <= END_DATE
            ) as t1

        WHERE serie NOT IN (
            SELECT serie
            FROM expedition_series
            WHERE DATE(created_on) <= END_DATE
        )
    ) as t on left_side_base.serie = t.serie;

    return stock_value;
END;

