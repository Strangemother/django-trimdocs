+ object_path: {{ object_path }}
+ Exists: {{ object_path_info.given_absolute.exists }}
+ Is file: {{ object_path_info.given_absolute.is_file }}
+ Is dir: {{ object_path_info.given_absolute.is_dir }}
+ rel path: {{ object_path_info.given_relative }}
+ -
{% for key, value in object_path_info.items %}+ {{ key }}: {{ value }}
{% endfor %}