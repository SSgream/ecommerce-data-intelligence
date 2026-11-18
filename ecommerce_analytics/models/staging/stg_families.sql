
SELECT
    family_id,
    family_name
FROM {{ source('ecommerce_dw', 'dim_family') }}
