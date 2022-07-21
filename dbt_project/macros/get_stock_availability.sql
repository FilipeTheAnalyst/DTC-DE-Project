{#
    This macro returns the stock availability for each game
#}

{% macro get_stock_availability(stock_status) -%}

    case {{ stock_status }}
        when 'En stock' then 'In Stock'
        when 'En Stock' then 'In Stock'
        when 'Agotado' then 'Out of Stock'
        when 'En stock, Recíbelo en 24/48 horas' then 'In Stock'
        when 'En Stock, Recíbelo en 24/48 horas' then 'In Stock'
        when 'Enstock' then 'In Stock'
        when 'En stcok' then 'In Stock'
        when 'EN stock' then 'In Stock'
        when 'Disponible' then 'In Stock'
    else 'TBD'
    end

{%- endmacro %}