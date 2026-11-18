
SELECT
    id,
    date,
    store_nbr,
    family_id,
    predicted_sales,
    created_at
FROM {{ source('ecommerce_dw', 'fact_sales_forecast') }}
