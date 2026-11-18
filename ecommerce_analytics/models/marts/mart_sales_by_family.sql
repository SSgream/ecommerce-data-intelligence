
SELECT
    p.family_id,
    p.family_name,

    COUNT(f.id) AS total_forecasts,
    SUM(f.predicted_sales) AS total_predicted_sales,
    AVG(f.predicted_sales) AS avg_predicted_sales,
    MIN(f.predicted_sales) AS min_predicted_sales,
    MAX(f.predicted_sales) AS max_predicted_sales

FROM {{ ref('stg_sales_forecast') }} f

JOIN {{ ref('stg_families') }} p
    ON f.family_id = p.family_id

GROUP BY
    p.family_id,
    p.family_name
