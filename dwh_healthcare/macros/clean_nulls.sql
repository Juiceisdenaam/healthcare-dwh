
-- macros/clean_nulls.sql

{% macro clean_text(value) %}
    case
        when trim(lower({{ value }})) in ('nan', '', 'null') then null
        else {{ value }}
    end
{% endmacro %}
