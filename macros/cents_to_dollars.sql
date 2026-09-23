{% macro cents_to_dollars(columns_name, decimal_places=2) %}
    round(cast({{ columns_name }} as numeric) / 100.0, {{ decimal_places }})
{% endmacro %}