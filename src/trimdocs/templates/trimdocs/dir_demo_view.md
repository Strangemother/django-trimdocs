{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

{% if index_filename_info.given_relative  %}{% include index_filename_info.given_absolute_str %}{% else %}{{ object_path_info }}{% endif %}

> Directory `{{ object_path_info.given_relative }}/`


This template presents a directory from the srcdocs - This should present the markdown readme of the directory.

{% include "./object_info.md" %}

> Found File: `{{ index_filename_info.given_relative }}`

{% include "./object_info.md" with object_path_info=index_filename_info %}


{{ object_list|length }} children

{% for unit in object_list %}
+ [{{ unit.name }}{% if unit.is_dir %}/{% endif %}]({{unit.rel_path}})
    Unit: {{ unit }}
{% endfor %}