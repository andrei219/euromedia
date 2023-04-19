use euromedia;


create temporary table if not exists temp_purchase_partners as
    select
        purchase_proformas.id as proforma_id,
        partners.fiscal_name as partner_name
    from purchase_proformas inner join partners on purchase_proformas.partner_id = partners.id;

create temporary table if not exists temp_sale_partners as
    select
        sale_proformas.id as proforma_id,
        partners.fiscal_name as partner_name
    from sale_proformas inner join partners on sale_proformas.partner_id = partners.id;


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
drop temporary table if exists left_side_base;

create temporary table temp_purchase_expenses as
    select
        purchase_proformas.id as proforma_id,
        coalesce(expenses, 0) as total_expenses
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
        reception_lines.item_id as item_id,
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

# Delete trash payments:
delete from sale_payments where amount = 0;

# Delete trash expenses
delete from sale_expenses where amount = 0;

# Delete orphan lines:
delete from sale_proforma_lines where proforma_id is null;
delete from advanced_lines where proforma_id is null;


drop temporary table if exists temp_sale_expenses; # proforma_id, total_expenses
drop temporary table if exists temp_sale_payments; # proforma_id, total_paid, total_paid_rated, average
drop temporary table if exists temp_sale_devices; # proforma_id, devices
drop temporary table if exists temp_sale_debt; # proforma_id, total_debt
drop temporary table if exists temp_sale_repr; # proforma_id, doc_repr, date
drop temporary table if exists temp_sale_series; # proforma_id, serie, clean_repr, condition, spec, price
drop temporary table if exists temp_sale_income;
drop temporary table if exists temp_sale_returns; # proforma_id, serie, item_id, condition, spec, price
# Auxiliary table for temp_sale_series
drop temporary table if exists temp_sale_stock_lines; # proforma_id, item_id, condition, spec, price

# Auxiliary table for temp_sale_series
create temporary table temp_sale_stock_lines as
    select
        proforma_id, item_id, `condition`, `spec`, price
    from sale_proforma_lines
    where item_id is not null and
          `condition` is not null and
            `spec` is not null
    union
    select
        proforma_id, item_id, `condition`, `spec`, price
        from advanced_lines
        where item_id is not null and
              `condition` is not null and
                `spec` is not null
    union
    select
        proforma_id,
        advanced_lines_definition.item_id,
        advanced_lines_definition.`condition`,
        advanced_lines_definition.`spec`,
        advanced_lines.price
        from advanced_lines_definition inner join
            advanced_lines on advanced_lines_definition.line_id = advanced_lines.id;

CREATE TEMPORARY TABLE temp_sale_repr AS
SELECT
    id as proforma_id,
    CONCAT(type, '-', LPAD(number, 6, '0')) AS doc_repr,
    DATE_FORMAT(date, '%d/%m/%Y') AS date
FROM sale_proformas
WHERE agent_id=5;

create temporary table temp_sale_series as
    select
        sale_proformas.id as proforma_id,
        expedition_series.serie as serie,
        expedition_lines.item_id,
        temp_items.clean_repr,
        expedition_lines.`condition`,
        expedition_lines.`spec`,
        (
            select price
            from temp_sale_stock_lines
            where proforma_id = expeditions.proforma_id and
            `condition` = expedition_lines.`condition` and
            `spec` = expedition_lines.`spec` and
            item_id = expedition_lines.item_id
        ) as price
    from expedition_series
    inner join expedition_lines on expedition_series.line_id = expedition_lines.id
    inner join expeditions on expedition_lines.expedition_id = expeditions.id
    inner join temp_items on expedition_lines.item_id = temp_items.id
    inner join sale_proformas on expeditions.proforma_id = sale_proformas.id
    where sale_proformas.agent_id=5;

create temporary table temp_sale_returns as
    select
        proforma_id,
        sn as serie,
        item_id,
        `condition`,
        `spec`,
        price
    from credit_note_lines inner join sale_proformas on sale_proformas.id=credit_note_lines.proforma_id
    where sale_proformas.agent_id=5;

create temporary table temp_sale_payments as
    select
        sale_proformas.id as proforma_id,
        coalesce(amount, 0) as total_paid ,
        coalesce(amount_rated,0) as total_paid_rated,
        coalesce(average_rate, 1) as average_rate
    from sale_proformas left outer join (
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
            from sale_payments
            group by proforma_id) as t

    ) as u on u.proforma_id = sale_proformas.id
    where sale_proformas.agent_id=5;

create temporary table temp_sale_debt as
    select
        proforma_id,
        sum(quantity * price * (1 + tax/100)) as total_debt
    from (
        select
            proforma_id,
            price,
            quantity,
            tax
          from sale_proforma_lines
          union all
          select
            proforma_id,
            price,
            quantity,
            tax
          from advanced_lines
    ) as t group by proforma_id;

create temporary table temp_sale_expenses as
    select
        sale_proformas.id as proforma_id,
        - coalesce(sum(amount), 0) as total_expenses
    from sale_proformas left outer join sale_expenses
    on sale_proformas.id = sale_expenses.proforma_id
    where sale_proformas.agent_id=5
    group by sale_proformas.id;

create temporary table temp_sale_income as
    select
        proforma_id,
        income
    from (
            select
                proforma_id,
                sum(price * quantity) as income
            from sale_proforma_lines
            where (item_id is null or `condition` is null or `spec` is null) and price > 0 and quantity > 0
            group by proforma_id
            union all
            select
                proforma_id,
                sum(price * quantity) as income
            from advanced_lines
            where item_id is null and mixed_description is null and price > 0 and quantity > 0
            group by proforma_id
         ) as t
    where proforma_id in (select proforma_id from expeditions);

create temporary table temp_sale_devices as
    select
        proforma_id,
        quantity as number_of_devices
    from (
        select
            proforma_id,
            sum(quantity) as quantity
        from sale_proforma_lines
        where item_id is not null and `condition` is not null and `spec` is not null
        group by proforma_id
        union all
        select
            proforma_id,
            sum(quantity) as quantity
        from advanced_lines
        where item_id is not null or `condition` is not null
        group by proforma_id

    ) as t;


# Now the final results:

# # Left side:
# create temporary table left_side_base as
#     select
#         temp_purchase_series.proforma_id                                                                                  as 'proforma_id',
#         temp_purchase_repr.doc_repr                                                                                       as 'Document',
#         temp_purchase_repr.date                                                                                           as 'Date',
#         temp_purchase_partners.partner_name                                                                               as 'Partner',
#         temp_items.clean_repr                                                                                             as 'Description',
#         temp_purchase_series.`condition`                                                                                  as 'Condition',
#         temp_purchase_series.`spec`                                                                                       as 'Spec',
#         IF(average_rate != 1, temp_purchase_series.price * average_rate, 'Unknown') as 'USD',
#         temp_purchase_series.price/temp_purchase_payments.average_rate as 'EUR',
#         average_rate as 'Average Rate',
#         case
#             when total_debt - total_paid < 1 then 'Paid'
#             when total_paid = 0 then 'Not Paid'
#             else 'Partially Paid'
#         end as 'Financial Status',
#         temp_purchase_expenses.total_expenses/temp_purchase_devices.number_of_devices/temp_purchase_payments.average_rate as 'Expenses',
#         temp_purchase_series.price/temp_purchase_payments.average_rate as 'Cost',
#
#         temp_purchase_series.serie                                                                                        as 'Serie'
#     from temp_purchase_series
#         inner join temp_purchase_repr on temp_purchase_series.proforma_id = temp_purchase_repr.proforma_id
#         inner join temp_purchase_partners on temp_purchase_series.proforma_id = temp_purchase_partners.proforma_id
#         inner join temp_purchase_devices on temp_purchase_series.proforma_id = temp_purchase_devices.proforma_id
#         inner join temp_items on temp_purchase_series.item_id = temp_items.id
#         inner join temp_purchase_expenses on temp_purchase_series.proforma_id = temp_purchase_expenses.proforma_id
#         inner join temp_purchase_debt on temp_purchase_series.proforma_id = temp_purchase_debt.proforma_id
#         inner join temp_purchase_payments on temp_purchase_series.proforma_id = temp_purchase_payments.proforma_id
#         where temp_purchase_series.serie is not null;


create temporary table left_side_base as
    select
        temp_purchas



