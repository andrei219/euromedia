
use euromedia;

set @at_capital_id = (select id from partners where fiscal_name like '%at capital%');
set @`from` = '2022-09-01';
set @to = '2022-09-30';

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


drop temporary table if exists temp_purchase_documents_repr;
drop temporary table if exists temp_purchase_lines;
drop temporary table if exists temp_purchase_series;
drop temporary table if exists temp_purchase_series_cost;
drop temporary table if exists temp_purchase_rate;
drop temporary table if exists right_side_base;

create temporary table if not exists temp_purchase_documents_repr as
    select
        po.id as proforma_id,
        case
            when po.external != '' then concat('EXT:',  po.external)
            when pi.type is not null then concat('FR ', pi.type, '-', lpad(pi.number, 6, '0'))
            when pi.type is null then concat('PR ', po.type, '-', lpad(po.number, 6, '0'))
        end as doc_repr,
        partners.fiscal_name
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
    where purchase_proforma_lines.`condition` is not null;

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
    inner join purchase_proformas on receptions.proforma_id = purchase_proformas.id;

create temporary table temp_purchase_series_cost as
    select temp_purchase_lines.proforma_id as proforma_id, serie, price as cost
    from temp_purchase_series inner join temp_purchase_lines
    on temp_purchase_series.proforma_id = temp_purchase_lines.proforma_id
    and coalesce(temp_purchase_series.description, 0) = coalesce(temp_purchase_lines.description, 0)
    and coalesce(temp_purchase_series.item_id, 0) = coalesce(temp_purchase_lines.item_id, 0)
    and temp_purchase_series.`condition` = temp_purchase_lines.`condition`
    and temp_purchase_series.spec = temp_purchase_lines.spec;

create temporary table if not exists temp_purchase_rate as
    select
        proforma_id,
        sum(amount)/sum(amount/rate) as rate
    from purchase_payments group by proforma_id;




drop temporary table if exists temp_sale_documents_repr;
drop temporary table if exists temp_sale_stock_lines; #
drop temporary table if exists temp_sale_series; # pid, item_id, `cond`, spec, income ...
drop temporary table if exists temp_sale_series_income;
drop temporary table if exists left_side_base;


create temporary table if not exists temp_sale_documents_repr as

    select
        *
    from (
        select so.id                      as proforma_id,
                 case
                 when si.type is not null then concat('FR ', si.type, '-', lpad(si.number, 6, '0'))
                 when si.type is null then concat('PR ', so.type, '-', lpad(so.number, 6, '0'))
                 end                    as doc_repr,
                 coalesce(si.date, so.date) as `date`,
                 partners.fiscal_name,
                 partners.fiscal_number
          from sale_proformas so
               left join sale_invoices si on so.sale_invoice_id = si.id
               inner join partners on so.partner_id = partners.id
          where partners.id = @at_capital_id) as temp
    where
        temp.`date` >= @`from` and
        temp.`date` <= @to;

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
    where
        sale_proforma_lines.item_id is not null and
        sale_proformas.partner_id = @at_capital_id
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
    where
        sale_proformas.partner_id = @at_capital_id and
        free_description is null
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
    where
        sale_proformas.partner_id = @at_capital_id;

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
    where sale_proformas.partner_id = @at_capital_id;

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
        and temp_sale_series.`spec` = temp_sale_stock_lines.`spec`;

create temporary table if not exists left_side_base as
    select
        tsr.proforma_id as proforma_id,
        tsr.doc_repr as 'Document',
        tsr.date as 'Date',
        tsr.fiscal_name 'Customer',
        tsr.fiscal_number as 'NIF',
        tssi.serie as serie,
        ti.clean_repr as 'Description',
        tssi.income as 'Sale Price'
    from temp_sale_documents_repr tsr
        inner join temp_sale_series_income tssi on tsr.proforma_id = tssi.proforma_id
        inner join temp_items ti on ti.id = tssi.item_id;

create temporary table if not exists right_side_base as
    select
        tpsc.serie as serie,
        tpr.doc_repr as 'Document',
        tpr.fiscal_name as 'Supplier',
        tpsc.cost/coalesce(rate, 1) as Cost,
        rate
    from temp_purchase_documents_repr tpr
        inner join temp_purchase_series_cost tpsc on tpsc.proforma_id=tpr.proforma_id
        left join temp_purchase_rate on tpsc.proforma_id=temp_purchase_rate.proforma_id;


drop temporary table if exists result;
create temporary table if not exists result as
    select
        left_side_base.Document as 'Sale Doc.',
        left_side_base.Date as 'Date',
        left_side_base.Customer as Customer,
        left_side_base.NIF as NIF,
        left_side_base.serie as Serie,
        left_side_base.Description as Description,
        left_side_base.`Sale Price` as `Sale Price`,
        right_side_base.Document as 'Purchase Doc.',
        right_side_base.Supplier as Supplier,
        round(right_side_base.cost, 2) as Cost
    from
        left_side_base inner join right_side_base
        on left_side_base.serie = right_side_base.serie;

select * from result order by Date;
