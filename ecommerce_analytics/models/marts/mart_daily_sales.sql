
SELECT
    d.date,
    d.year,
    d.month,
    d.day,
    d.day_of_week,
    d.is_weekend,

    COUNT(f.id) AS total_forecasts,
    SUM(f.predicted_sales) AS total_predicted_sales,
    AVG(f.predicted_sales) AS avg_predicted_sales

FROM {{ ref('stg_sales_forecast') }} f

JOIN {{ ref('stg_dates') }} d
    ON f.date = d.date

GROUP BY
    d.date,
    d.year,
    d.month,
    d.day,
    d.day_of_week,
    d.is_weekend
