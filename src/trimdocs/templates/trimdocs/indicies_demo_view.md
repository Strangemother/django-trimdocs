{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

# Indicies

This is a _special_ file to list the index content of the pages below.

---

{% if index_filename_info.given_relative  %}{% include index_filename_info.given_absolute_str %}{% else %}{{ object_path_info }}{% endif %}

> Indicies `{{ object_path_info.given_relative }}/`


{% if not index_filename_info.given_relative %}
An existing _indicies_ file does not exist. A default one is applied.
{% endif %}
---

{% include "./object_info.md" %}

> Found File: `{{ index_filename_info.given_relative }}`

{% include "./object_info.md" with object_path_info=index_filename_info %}


{{ object_list|length }} children

{% for unit in object_list %}
+ [{{ unit.name }}{% if unit.is_dir %}/{% endif %}]({{unit.rel_path}})
    Unit: {{ unit }}
{% endfor %}