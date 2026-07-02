
-- macros/survivorship/longest_non_null.sql

{% macro longest_non_null(column_name) %}

(
    array_agg(
        {{ column_name }}
        order by
            case when {{ column_name }} is not null then 0 else 1 end,
            length({{ column_name }}) desc
    )
)[1]

{% endmacro %}
