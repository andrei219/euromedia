
use euromedia;

set @`from` = '2023-01-01';
set @to = '2023-03-31';
set @agent_id = 5;


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
drop temporary table if exists temp_purchase_expenses_inv; # proforma_id, expenses in lines
drop temporary table if exists temp_purchase_payments; # proforma_id, paid, paid_rated
drop temporary table if exists temp_purchase_devices; # proforma_id, devices
drop temporary table if exists temp_purchase_debt; # proforma_id, total_debt
drop temporary table if exists temp_purchase_repr; # proforma_id, doc_repr, date
drop temporary table if exists temp_purchase_series; # proforma_id, description item_id, condition, spec, serie
drop temporary table if exists temp_purchase_lines; # proforma_id, description, item_id, condition, spec, price
drop temporary table if exists temp_purchase_series_cost; # proforma_id, serie, price
drop temporary table if exists temp_purchase_currency_rate; # proforma_id, cur(code)
drop temporary table if exists left_numbered;
drop table if exists left_side_base; # proforma_id, serie, expenses_eur, expenses_inv, cost, currency, rate

delete from purchase_payments where amount=0;
delete from purchase_expenses where amount=0;

create temporary table if not exists temp_purchase_partners as
    select
        purchase_proformas.id as proforma_id,
        partners.fiscal_name as partner_name
    from purchase_proformas inner join partners on purchase_proformas.partner_id = partners.id
    where purchase_proformas.agent_id = @agent_id;

create temporary table if not exists temp_purchase_expenses_eur as
    select
        purchase_expenses.proforma_id as proforma_id,
        sum(purchase_expenses.amount) as expenses_eur
    from purchase_expenses
    inner join purchase_proformas
    on purchase_expenses.proforma_id = purchase_proformas.id
    group by purchase_expenses.proforma_id;

create temporary table if not exists temp_purchase_expenses_inv as
    select
        proforma_id,
        sum(quantity * price) as expenses_inv
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where `condition` is null and agent_id=@agent_id
    group by proforma_id;

create temporary table if not exists temp_purchase_payments as
    select
        proforma_id,
        sum(amount) as paid,
        sum(amount/rate) as paid_rated
    from purchase_payments
    inner join purchase_proformas
    on purchase_payments.proforma_id = purchase_proformas.id
    where agent_id=@agent_id
    group by proforma_id;

create temporary table if not exists temp_purchase_devices as
    select
        proforma_id,
        sum(quantity) as devices
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where `condition` is not null
    and agent_id=@agent_id
    group by proforma_id;

create temporary table if not exists temp_purchase_debt as
    select
        proforma_id,
        sum(quantity * price * ( 1 + tax/100)) as debt
    from purchase_proforma_lines inner join purchase_proformas
    on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where agent_id=@agent_id
    group by proforma_id;


create temporary table if not exists temp_purchase_repr as
    select
        po.id as proforma_id,
        case
            when pi.type is not null then concat('FR ', pi.type, '-', lpad(pi.number, 6, '0'))
            when pi.type is null then concat('PR ', po.type, '-', lpad(po.number, 6, '0'))
        end as doc_repr,
        case
            when pi.date is not null then date_format(pi.date, '%d/%m/%Y')
            when pi.date is null then date_format(po.date, '%d/%m/%Y')
        end as date
    from purchase_proformas po
    left join purchase_invoices pi on po.invoice_id = pi.id
    inner join partners on po.partner_id = partners.id;


create temporary table temp_purchase_lines as
    select
        purchase_proforma_lines.proforma_id as proforma_id,
        purchase_proforma_lines.description as description,
        purchase_proforma_lines.item_id as item_id,
        purchase_proforma_lines.condition as `condition`,
        purchase_proforma_lines.spec as spec,
        purchase_proforma_lines.price as price
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id
    where purchase_proforma_lines.`condition` is not null and agent_id=@agent_id;

create temporary table temp_purchase_series as
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
    inner join purchase_proformas on receptions.proforma_id = purchase_proformas.id
    where purchase_proformas.agent_id=@agent_id;

create temporary table temp_purchase_series_cost as
    select temp_purchase_lines.proforma_id as proforma_id, serie, price as cost
    from temp_purchase_series inner join temp_purchase_lines
    on temp_purchase_series.proforma_id = temp_purchase_lines.proforma_id
    and coalesce(temp_purchase_series.description, 0) = coalesce(temp_purchase_lines.description, 0)
    and coalesce(temp_purchase_series.item_id, 0) = coalesce(temp_purchase_lines.item_id, 0)
    and temp_purchase_series.`condition` = temp_purchase_lines.`condition`
    and temp_purchase_series.spec = temp_purchase_lines.spec;

create temporary table if not exists temp_purchase_currency_rate as
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
        left join temp_purchase_debt on temp_purchase_debt.proforma_id = purchase_proformas.id
    where agent_id=@agent_id;

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

drop temporary table if exists temp_sale_partners;
drop temporary table if exists temp_sale_expenses_eur;
drop temporary table if exists temp_sale_income_inv;
drop temporary table if exists temp_sale_payments;
drop temporary table if exists temp_sale_stock_lines; # proforma_id, item_id, condition, spec, income
drop temporary table if exists temp_sale_devices;
drop temporary table if exists temp_sale_debt;
drop temporary table if exists temp_sale_repr;
drop temporary table if exists temp_sale_series; # proforma_id, serie, item_id, condition, spec
drop temporary table if exists temp_sale_series_income;
drop temporary table if exists temp_sale_currency_rate; # proforma_id, currency, rate
drop temporary table if exists right_numbered;
drop table if exists right_side_base;


create temporary table if not exists temp_sale_partners as
    select
        sale_proformas.id as proforma_id,
        fiscal_name
    from sale_proformas
    inner join partners on sale_proformas.partner_id = partners.id
    where sale_proformas.agent_id=@agent_id;

create temporary table if not exists temp_sale_expenses_eur as
    select
        proforma_id,
        sum(amount) as expenses_eur
    from sale_expenses
    inner join sale_proformas
    on sale_proformas.id = sale_expenses.proforma_id
    where agent_id=@agent_id
    group by proforma_id;

create temporary table if not exists temp_sale_income_inv as
    select
        proforma_id,
        sum(quantity * price) as income_inv
    from sale_proforma_lines
    inner join sale_proformas
    on sale_proforma_lines.proforma_id = sale_proformas.id
    where agent_id=@agent_id and description is not null
    group by proforma_id
    having income_inv > 0
    union all
    select
        proforma_id,
        sum(quantity * price) as income_inv
    from advanced_lines
    inner join sale_proformas
    on advanced_lines.proforma_id = sale_proformas.id
    where free_description is not null and agent_id=@agent_id
    group by proforma_id
    having income_inv > 0;

create temporary table if not exists temp_sale_payments as
    select
        proforma_id,
        sum(amount) as paid,
        sum(amount/rate) as paid_rated
    from sale_payments
    inner join sale_proformas
    on sale_payments.proforma_id = sale_proformas.id
    where agent_id=@agent_id
    group by proforma_id
    having paid > 0;

# This table serves for join with warehouse part
create temporary table if not exists temp_sale_stock_lines as
    select
        sale_proforma_lines.proforma_id,
        sale_proforma_lines.item_id,
        sale_proforma_lines.`condition`,
        sale_proforma_lines.spec as spec,
        sale_proforma_lines.quantity as quantity,
        sale_proforma_lines.price as income
    from sale_proforma_lines
    inner join sale_proformas
    on sale_proforma_lines.proforma_id = sale_proformas.id
    where agent_id=@agent_id and sale_proforma_lines.item_id is not null
    union all
    select
        advanced_lines.proforma_id,
        advanced_lines.item_id,
        advanced_lines.`condition`,
        advanced_lines.spec as spec,
        advanced_lines.quantity as quantity,
        advanced_lines.price as income
    from advanced_lines
    inner join sale_proformas
    on sale_proformas.id = advanced_lines.proforma_id
    where agent_id=@agent_id and free_description is null
    union all
    select
        advanced_lines.proforma_id,
        advanced_lines_definition.item_id,
        advanced_lines_definition.spec,
        advanced_lines_definition.`condition`,
        advanced_lines_definition.quantity as quantity,
        advanced_lines.price as income
    from advanced_lines_definition
    inner join advanced_lines
    on advanced_lines_definition.line_id = advanced_lines.id
    inner join sale_proformas on advanced_lines.proforma_id = sale_proformas.id
    where agent_id=@agent_id;

create temporary table if not exists temp_sale_devices as
    # First part already filtered above.
    select
        proforma_id,
        sum(quantity) as devices
    from temp_sale_stock_lines
    group by proforma_id
    union all
    select
        proforma_id,
        count(*) as devices
    from credit_note_lines
    inner join sale_proformas on
        credit_note_lines.proforma_id = sale_proformas.id
    where agent_id=@agent_id
    group by proforma_id;

# Pre-orders and Normal Sales. We dont need credit notes here.
create temporary table if not exists temp_sale_debt as
    select
        proforma_id,
        sum(quantity * price * (1 + tax/100)) as debt
    from sale_proforma_lines
    inner join sale_proformas
    on sale_proforma_lines.proforma_id = sale_proformas.id
    where agent_id=@agent_id
    union all
    select
        proforma_id,
        sum(quantity * price * (1 + tax/100)) as debt
    from advanced_lines
    inner join sale_proformas
    on sale_proformas.id=advanced_lines.proforma_id
    where agent_id=@agent_id
    group by proforma_id;


create temporary table if not exists temp_sale_repr as
    select
        sp.id as proforma_id,
        case
            when si.type is not null then concat('FR ', si.type, '-', lpad(si.number, 6, '0'))
            when si.type is null then concat('PR ', sp.type, '-', lpad(sp.number, 6, '0'))
        end as doc_repr,
        case
            when si.type is not null then date_format(si.date, '%d/%m/%Y')
            when si.type is null then date_format(sp.date, '%d/%m/%Y')
        end as date

    from sale_proformas sp
        inner join sale_invoices si on sp.sale_invoice_id=si.id

    where agent_id=@agent_id and si.date >= @`from` and si.date <= @to;


create temporary table if not exists temp_sale_series as
    select
        expedition_series.serie as serie,
        expedition_lines.item_id,
        expedition_lines.`condition` as `condition`,
        expedition_lines.spec as spec,
        expeditions.proforma_id as proforma_id
    from expedition_series
    inner join expedition_lines on expedition_series.line_id = expedition_lines.id
    inner join expeditions on expedition_lines.expedition_id = expeditions.id
    inner join sale_proformas on expeditions.proforma_id = sale_proformas.id
    inner join sale_invoices on sale_proformas.sale_invoice_id = sale_invoices.id
    where
        agent_id=@agent_id and
        sale_invoices.date >= @`from` and
        sale_invoices.date <= @to;


create temporary table if not exists temp_sale_series_income as
    select
        temp_sale_series.proforma_id as proforma_id,
        temp_sale_series.serie as serie,
        temp_sale_series.item_id as item_id,
        temp_sale_series.`condition` as `condition`,
        temp_sale_series.`spec`,
        temp_sale_stock_lines.income
    from temp_sale_series
    inner join temp_sale_stock_lines
        on temp_sale_series.proforma_id = temp_sale_stock_lines.proforma_id
        and temp_sale_series.item_id = temp_sale_stock_lines.item_id
        and temp_sale_series.`condition` = temp_sale_stock_lines.`condition`
        and temp_sale_series.`spec` = temp_sale_stock_lines.`spec`

    union all
    select
            proforma_id, sn as serie, item_id, `condition`, spec, price
        from credit_note_lines
        inner join sale_proformas
        on sale_proformas.id = credit_note_lines.proforma_id
        where agent_id=@agent_id;

# Can generate duplicates:
# A = all proforma_ids
# B = all proforma_ids if proforma.warehouse_id is null
# Then use union instead of union all.
create temporary table if not exists temp_sale_currency_rate as
    select
        sale_proformas.id as proforma_id,
        case
            when coalesce(paid, 0) = 0 and eur_currency = 1 then 'EUR'
            when coalesce(paid, 0) = 0 and eur_currency = 0 then 'USD'
            when coalesce(paid, 0) = coalesce(paid_rated, 0) and paid != 0 then 'EUR'
            when coalesce(paid, 0) <> coalesce(paid_rated, 0) and paid_rated != 0 then 'USD'
        end as currency,
        coalesce(paid/paid_rated, 1) as rate
    from sale_proformas
        left join temp_sale_payments on temp_sale_payments.proforma_id=sale_proformas.id
        left join temp_sale_debt on temp_sale_debt.proforma_id = sale_proformas.id
    where agent_id=@agent_id
    union
        select
            proforma_id,
            'EUR' as currency,
            1 as rate
        from (select distinct proforma_id from credit_note_lines) as c ;

create table if not exists right_side_base as
    select
        temp_sale_series_income.proforma_id as proforma_id,
        temp_sale_series_income.serie as serie,
        temp_sale_series_income.income,
        coalesce((income_inv/devices)/rate, 0) as additional_income,
        coalesce(expenses_eur/devices, 0) as expenses_eur,
        IF(currency='USD' and rate <> 1, 'EUR', currency) as currency,
        rate
    from temp_sale_series_income
        left join temp_sale_expenses_eur tsee on temp_sale_series_income.proforma_id = tsee.proforma_id
        left join temp_sale_income_inv tsii on temp_sale_series_income.proforma_id = tsii.proforma_id
        inner join temp_sale_currency_rate tscr on temp_sale_series_income.proforma_id = tscr.proforma_id
        inner join temp_sale_devices tsd on temp_sale_series_income.proforma_id = tsd.proforma_id;

create temporary table if not exists left_numbered as
        SELECT
            ROW_NUMBER() OVER (PARTITION BY serie ) AS n,
            left_side_base.*
        FROM left_side_base;

create temporary table if not exists right_numbered as
            SELECT
            ROW_NUMBER() OVER (PARTITION BY serie ) AS n,
            right_side_base.*
        FROM right_side_base;


drop temporary table if exists result;
create temporary table result as
    select l.proforma_id       as purchase_proforma_id,
                l.serie             as purchase_serie,
                coalesce(l.expenses_eur, 0)      as purchase_expenses_eur,
                coalesce(l.expenses_inv, 0)      as purchase_expenses_inv,
                coalesce(l.cost, 0)              as cost,
                l.currency          as purchase_currency,
                l.rate              as purchase_rate,
                r.proforma_id       as sale_id,
                r.serie             as sale_serie,
                r.income            as income,
                r.additional_income as additional_income,
                r.expenses_eur      as sale_expenses_eur,
                r.currency          as sale_currency,
                r.rate              as sale_rate,
                r.n                 as `partition`
         from right_numbered r
                  left join left_numbered l ON l.serie = r.serie AND l.n = r.n;


drop temporary table if exists harvest;
create temporary table if not exists harvest as
    select
        result.sale_serie as serie,
        1 as `partition`,
        round(
            sum(income)+
            sum(additional_income)-
            sum(sale_expenses_eur)-
            sum(cost)-
            sum(purchase_expenses_inv)-
            sum(purchase_expenses_eur),
        2)
        as harvest
    from result
    group by sale_serie;

select * from harvest;


select
    temp_purchase_repr.doc_repr as 'Document',
    temp_purchase_repr.date as date,
    result.purchase_serie as serie,
    round(result.purchase_expenses_eur, 2) as expenses_eur,
    round(result.purchase_expenses_inv, 2) as expenses_doc,
    round(result.cost, 2) as cost,
    result.purchase_currency as cur,
    result.purchase_rate as rate,
    temp_sale_repr.doc_repr as 'Document',
    temp_sale_repr.date as date,
    result.sale_serie as serie,
    round(result.income, 2) as income,
    round(result.additional_income, 2) as `Add. income`,
    round(result.sale_expenses_eur, 2) as expenses,
    result.sale_currency as cur,
    result.sale_rate as rate,
    harvest.harvest
from result
    left join harvest on harvest.serie=result.sale_serie and harvest.`partition`=result.`partition`
    left join temp_sale_repr on temp_sale_repr.proforma_id=result.sale_id
    left join temp_purchase_repr on temp_purchase_repr.proforma_id=result.purchase_proforma_id
    order by result.sale_serie, result.partition;


