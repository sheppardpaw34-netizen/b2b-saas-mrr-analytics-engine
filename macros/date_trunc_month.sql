{% macro date_trunc_month(date_column) %}
    date_trunc('month', cast({{ date_column }} as date))
{% endmacro %}