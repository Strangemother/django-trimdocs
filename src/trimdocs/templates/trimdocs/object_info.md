+ object_path: {{ object_path }}
+ Exists: {{ object_path_info.given_absolute.exists }}
+ Type: {% if object_path_info.given_absolute.is_file %}file{% else %}directory{% endif %}
+ rel path: {{ object_path_info.given_relative }}
+ -
{% for key, value in object_path_info.items %}+ {{ key }}: {{ value }}
{% endfor %}