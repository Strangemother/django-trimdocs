{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

> Default Page `{{ object_path_info.given_relative }}`

This template presents a src file from the srcdocs - This should present the markdown rendered markdown.

{% if not object_path_info.given_absolute.exists %}# 404

If you're seeing this, your target file `{{ object_path_info.given_relative }}` may not exist.<br>
However this page `{{ request.path }}` will not exist in the destination compiled docs.

---{% endif %}

{% include "./object_info.md" %
}Objects:

{{ object_list|length }} children