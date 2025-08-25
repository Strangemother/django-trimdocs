# Indicies

{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %} {% else %}
no file: {{ object_path_info.given_absolute.as_posix }} {% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

{{ object_list|length }} children

{% for unit in object_list %}+ [{{ unit.origin_path }}{% if unit.as_path.is_dir %}/{% endif %}]({% link.relpath unit.origin_path %})
{% endfor %}

---

{% if index_filename_info.given_relative  %}{% include index_filename_info.given_absolute_str %}{% else %}No `index_filename_info`, data: {{ object_path_info }}{% endif %}

> Indicies `{{ object_path_info.given_relative }}/`

This is a _special_ file to list the index content of the pages below.

{% if not index_filename_info.given_relative %}
An existing _indicies_ file does not exist. A default one is applied.
{% endif %}
---

{% include "./object_info.md" %}

> Found File: `{{ index_filename_info.given_relative }}`

{% include "./object_info.md" with object_path_info=index_filename_info %}
