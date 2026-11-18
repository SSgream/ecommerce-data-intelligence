
SELECT
    date,
    year,
    month,
    day,
    day_of_week,
    day_of_year,
    week_of_year,
    quarter,
    is_weekend
FROM {{ source('ecommerce_dw', 'dim_date') }}
