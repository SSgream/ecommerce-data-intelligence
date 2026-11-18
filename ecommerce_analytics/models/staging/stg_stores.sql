
SELECT
    store_nbr,
    city,
    state,
    store_type,
    cluster
FROM {{ source('ecommerce_dw', 'dim_store') }}
