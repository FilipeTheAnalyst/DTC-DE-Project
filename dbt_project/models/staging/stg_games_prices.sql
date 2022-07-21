{{ config(materialized='view') }}

select 
    id,
    store,
    name,
    price,
    bgg_url,
    url as store_url,
    date,
    {{ get_stock_availability('availability') }} as stock_availability
from {{ source('staging', 'gamesprices') }}