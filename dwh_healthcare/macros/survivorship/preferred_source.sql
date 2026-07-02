
{% macro preferred_source(column_name) %}

(
    array_agg(
        {{ column_name }}
        order by
            case source_system
                when 'EPD_A' then 1
                when 'EPD_B' then 2
                else 99
            end
    )
)[1]

{% endmacro %}
