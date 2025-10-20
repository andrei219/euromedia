sql="""
WITH
month_names AS (
    SELECT 1 AS month_num, 'January' AS month_name UNION ALL
    SELECT 2, 'February' UNION ALL
    SELECT 3, 'March' UNION ALL
    SELECT 4, 'April' UNION ALL
    SELECT 5, 'May' UNION ALL
    SELECT 6, 'June' UNION ALL
    SELECT 7, 'July' UNION ALL
    SELECT 8, 'August' UNION ALL
    SELECT 9, 'September' UNION ALL
    SELECT 10, 'October' UNION ALL
    SELECT 11, 'November' UNION ALL
    SELECT 12, 'December'
),
params AS (
    SELECT 
        DATE('{start_date}') AS start_date,
        DATE('{end_date}') AS end_date,
        {default_rate} AS default_rate_value
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
) SELECT 
    base.year
    ,`month_names`.month_name
    ,base._val as val 
 FROM ( 
SELECT
    YEAR(i.`date`) AS year,
    MONTH(i.`date`) AS month,
    SUM(t.total * COALESCE(r.rate, p.default_rate_value)) AS _val
FROM invoices i
CROSS JOIN params p
INNER JOIN totals t
    ON t.`proforma_id` = i.`proforma_id`
INNER JOIN month_names mn
    ON mn.month_num = MONTH(i.`date`)
LEFT JOIN rates r
    ON r.`proforma_id` = i.`proforma_id`
WHERE i.`date` BETWEEN p.start_date and p.end_date
GROUP BY YEAR(i.`date`), MONTH(i.`date`)
ORDER BY year, month
 ) as base 
    inner join `month_names` on `month_names`.month_num=base.month; 
"""

def render_sql(start_date, end_date, default_rate):
    return sql.format(
        start_date=start_date,
        end_date=end_date,
        default_rate=default_rate
    )

def execute_query(sql: str):
    import db 
    yield from map(list, db.session.execute(sql))


import typing
def save(data: typing.Iterator[list], file_path: str):
    import openpyxl
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    sheet.append(["Year", "Month", "Total"])

    for row in data: 
        sheet.append(row)

    workbook.save(file_path)

def collect_args_file_path():
    import sys 
    filepath = sys.argv[1]
    return filepath


def adapt_date(date_str: str) -> str:
    from datetime import datetime
    dt = datetime.strptime(date_str, '%d%m%Y')
    return dt.strftime("%Y-%m-%d")

def run_report(start_date: str, end_date: str, default_rate: float, file_path: str):
    save(execute_query(
        sql=render_sql(adapt_date(start_date), adapt_date(end_date), default_rate)
    ), file_path)

if __name__ == "__main__":

    start_date='2023-01-01'
    end_date='2023-12-31'
    default_rate=1.2

    run_report(
        start_date,
        end_date,
        default_rate,
        collect_args_file_path()
    )


