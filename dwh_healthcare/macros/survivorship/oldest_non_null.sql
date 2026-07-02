
-- macros/survivorship/oldest_non_null.sql

{% macro oldest_non_null(column_name, order_column='registration_date') %}

(
    array_agg(
        {{ column_name }}
        order by
            case when {{ column_name }} is not null then 0 else 1 end,
            {{ order_column }} asc
    )
)[1]

{% endmacro %}
