{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

> Default Page `{{ object_path_info.given_relative }}`

This template presents a src file from the srcdocs - This should present the markdown rendered markdown

{% include "./object_info.md" %}
Objects:

{{ object_list|length }} children