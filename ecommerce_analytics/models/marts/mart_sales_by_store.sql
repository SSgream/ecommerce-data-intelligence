
SELECT
    s.store_nbr,
    s.city,
    s.state,
    s.store_type,
    s.cluster,

    COUNT(f.id) AS total_forecasts,
    SUM(f.predicted_sales) AS total_predicted_sales,
    AVG(f.predicted_sales) AS avg_predicted_sales,
    MIN(f.predicted_sales) AS min_predicted_sales,
    MAX(f.predicted_sales) AS max_predicted_sales

FROM {{ ref('stg_sales_forecast') }} f

JOIN {{ ref('stg_stores') }} s
    ON f.store_nbr = s.store_nbr

GROUP BY
    s.store_nbr,
    s.city,
    s.state,
    s.store_type,
    s.cluster
