
drop table if exists temp_expedition_series;
create table if not exists temp_purchase_series as
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

drop table if exists temp_purchase_lines;
create table if not exists temp_purchase_lines as
    select
        purchase_proforma_lines.proforma_id as proforma_id,
        purchase_proforma_lines.description as description,
        purchase_proforma_lines.item_id as item_id,
        purchase_proforma_lines.condition as `condition`,
        purchase_proforma_lines.spec as spec,
        purchase_proforma_lines.price as price
    from purchase_proforma_lines
    inner join purchase_proformas on purchase_proforma_lines.proforma_id = purchase_proformas.id;

drop table if exists temp_purchase_series_cost;
create table if not exists temp_purchase_series_cost as
    select
        serie, price as cost
    from temp_purchase_series inner join temp_purchase_lines
    on temp_purchase_series.proforma_id = temp_purchase_lines.proforma_id
    and coalesce(temp_purchase_series.description, 0) = coalesce(temp_purchase_lines.description, 0)
    and coalesce(temp_purchase_series.item_id, 0) = coalesce(temp_purchase_lines.item_id, 0)
    and temp_purchase_series.`condition` = temp_purchase_lines.`condition`
    and temp_purchase_series.spec = temp_purchase_lines.spec;

drop function if exists get_stock_value;
CREATE FUNCTION get_stock_value(END_DATE DATE)
RETURNS DECIMAL(18, 2)
DETERMINISTIC
BEGIN
    declare stock_value decimal(18, 2);
    select sum(cost) into stock_value
    from temp_purchase_series_cost
    inner join (
        SELECT DISTINCT serie
        FROM reception_series
        WHERE DATE(created_on) <= END_DATE
        AND serie NOT IN (
            SELECT DISTINCT serie
            FROM expedition_series
            WHERE DATE(created_on) <= END_DATE
        )
    ) as t on temp_purchase_series_cost.serie = t.serie;

    return stock_value;
END;
