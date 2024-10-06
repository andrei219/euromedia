# Original query: 
select exists(
    select 
        expedition_series.serie as serie_expedicion,
        reception_series.serie  as serie_reception
    from expedition_series 
    left join reception_series
    on reception_series.serie = expedition_series.serie and 
        reception_series.created_on = expedition_series.created_on
    where expedition_series.serie = :serie
) as result;

# Expected : 1 
# Actual: 1 
# Needed : 0

# New tuned query: 
# read inside out. 
# first level, get the last time paired input from output
# if there exists one and is auto then it has "sister_serie"
# which means prevent from input via reception. 
# everything outside this predicate should pass . 
# the condition b is dependant always on inner conditions 


SELECT  
    NOT ISNULL(last_reception_serie.created_on) AS has_sister_serie
FROM (
    SELECT 
        reception_series.created_on AS created_on, 
        expedition_series.created_on as exp_created_on, 
        receptions.auto
    FROM expedition_series 
    LEFT JOIN reception_series
        ON reception_series.serie = expedition_series.serie 
            AND reception_series.created_on = expedition_series.created_on
    LEFT JOIN reception_lines
        ON reception_lines.id = reception_series.line_id 
    LEFT JOIN receptions
        ON reception_lines.reception_id = receptions.id 
    WHERE expedition_series.serie = :serie
    ORDER BY expedition_series.created_on DESC 
    LIMIT 1
) last_reception_serie; 

# Expected : 0
# Actual: 0



SELECT 
        reception_series.created_on AS created_on, 
        receptions.auto
    FROM expedition_series 
    LEFT  JOIN reception_series
        ON reception_series.serie = expedition_series.serie 
        AND reception_series.created_on = expedition_series.created_on
    left JOIN reception_lines
        ON reception_lines.id = reception_series.line_id 
    left JOIN receptions
        ON reception_lines.reception_id = receptions.id 
    WHERE expedition_series.serie = :serie


# NEW IDEA:
# WHAT IF WE ONLY ARE INTERESTED IN THE CURRENT DOCUMENT SPACE?
# THIS IS A DIRECT SHORTCUT

# THIS RETURNS TRUE AS EXPECTED
select exists(
    select 
        expedition_series.serie as serie_expedicion,
        reception_series.serie  as serie_reception
    from expedition_series 
    left join reception_series
    on reception_series.serie = expedition_series.serie and 
        reception_series.created_on = expedition_series.created_on
    where expedition_series.serie = :serie
) as result;

# THIS RETURNS FALSE, BECAUSE WE ARE REDUCING THE DATASET TO THE CURRENT RECEPTION SPACE
# WHEN A NEW RECEPTION IS CREATED
select exists(
    select 
        expedition_series.serie as serie_expedicion,
        reception_series.serie  as serie_reception
        ,receptions.id 
    from expedition_series 
    inner join reception_series
    on reception_series.serie = expedition_series.serie and 
        reception_series.created_on = expedition_series.created_on
    inner JOIN reception_lines
        ON reception_lines.id = reception_series.line_id
    inner JOIN receptions
        ON reception_lines.reception_id = receptions.id
    where expedition_series.serie = :serie
        AND receptions.id = :current_reception
) ; 


select receptions.`id`
from receptions inner join reception_lines 
    on reception_lines.reception_id = receptions.id
inner join 
    `reception_series`
    on `reception_series`.`line_id` = `reception_lines`.`id`
where `reception_series`.`serie` = :serie