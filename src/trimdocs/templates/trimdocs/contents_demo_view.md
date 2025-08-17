{% trimdocs.breadcrumbs %}
{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}{{ object_path_info }}{% endif %}
---

# Contents

This is a _special_ file to list the content of the pages below.

---

{% if index_filename_info.given_relative  %}{% include index_filename_info.given_absolute_str %}{% else %}{{ object_path_info }}{% endif %}

> Content `{{ object_path_info.given_relative }}/`


{% if not index_filename_info.given_relative %}
An existing _contents_ file does not exist. A default one is applied.
{% endif %}
---

{% include "./object_info.md" %}

> Found File: `{{ index_filename_info.given_relative }}`

{% include "./object_info.md" with object_path_info=index_filename_info %}

{{ object_list|length }} children
