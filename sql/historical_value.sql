
WITH 
params AS (
    SELECT 
        DATE('2024-01-01') AS start_date,
        DATE('2024-12-31') AS end_date,
        1 AS default_rate_value
),
totals AS (
    SELECT 
        ppl.`proforma_id`,
        SUM(ppl.`quantity` * ppl.`price` * (1 + ppl.`tax` / 100)) AS total
    FROM `purchase_proforma_lines` AS ppl
    GROUP BY ppl.`proforma_id`
), 
rates AS (
    SELECT 
        proforma_id,
        amount / NULLIF(amount_converted, 0) AS rate
    FROM (
        SELECT 
            proforma_id,
            SUM(`amount`) AS amount,
            SUM(`amount` * `rate`) AS amount_converted
        FROM `purchase_payments` pp
        GROUP BY proforma_id
    ) AS tmp
), 
invoices AS (
    SELECT 
        p.`id` AS proforma_id,
        i.`date`
    FROM `purchase_proformas` p
    INNER JOIN `purchase_invoices` i
        ON i.`id` = p.`invoice_id`
    WHERE p.`cancelled` = 0
)
SELECT 
    YEAR(i.`date`) AS year,
    MONTH(i.`date`) AS month,
    SUM(t.total * COALESCE(r.rate, p.default_rate_value)) AS _val
FROM invoices i
CROSS JOIN params p
INNER JOIN totals t 
    ON t.`proforma_id` = i.`proforma_id`
LEFT JOIN rates r 
    ON r.`proforma_id` = i.`proforma_id`
WHERE i.`date` BETWEEN p.start_date and p.end_date
GROUP BY YEAR(i.`date`), MONTH(i.`date`)
ORDER BY year, month;
