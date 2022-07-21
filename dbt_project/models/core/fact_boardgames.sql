{{ config(materialized='table') }}

with avg_price as (
    select distinct
    id,
    COUNT(id) AS stores_total_items,
    AVG(price) AS average_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
    from {{ ref('stg_games_prices') }}
    group by id
),
boardgame_data as ( 
select distinct
    bg_data.id,
    bg_data.name,
    bg_data.rank,
    bg_data.url,
    bg_data.rating,
    bg_data.num_voters,
    bg_data.year_published,
    bg_data.description,
    bg_data.date,
    avg_price.stores_total_items,
    avg_price.average_price,
    avg_price.max_price,
    avg_price.min_price,
    ROW_NUMBER() OVER(PARTITION BY bg_data.id  ORDER BY bg_data.date DESC, bg_data.num_voters DESC) AS RN,
    CASE
    when avg_price.average_price BETWEEN 0 AND 15 then '0-15€'
    when avg_price.average_price BETWEEN 16 AND 30 then '16-30€'
    when avg_price.average_price BETWEEN 31 AND 45 then '31-45€'
    when avg_price.average_price BETWEEN 46 AND 60 then '46-60€'
    when avg_price.average_price > 60 then '+60€'
    else 'N/A'
    end as price_range
from {{ ref('stg_boardgame_data') }} as bg_data
left join avg_price
on bg_data.id = avg_price.id
where bg_data.year_published <= 2022
)
select
    boardgame_data.id,
    boardgame_data.name,
    boardgame_data.rank,
    boardgame_data.url,
    boardgame_data.rating,
    boardgame_data.num_voters,
    boardgame_data.year_published, 
    boardgame_data.description,
    boardgame_data.date,
    boardgame_data.stores_total_items,
    boardgame_data.average_price,
    boardgame_data.min_price,
    boardgame_data.max_price,
    boardgame_data.price_range,
    RN
from boardgame_data
where RN = 1
ORDER BY stores_total_items DESC