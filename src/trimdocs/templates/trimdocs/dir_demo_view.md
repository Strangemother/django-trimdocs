{% extends "./source_demo_view.md" %}

{% block source.content %}
{% if object_path_info.given_relative  %}
<!-- {{ index_filename_info.given_relative_str }} -->
{% spaceless %}
    {% if index_filename_info.given_absolute.is_file %}
        {% include index_filename_info.given_relative_str %}
    {% else %}
        Is not a file: {{ index_filename_info.given_absolute }}
    {% endif %}
{% endspaceless %}
{% else %}
    No File. {{ object_path_info }}
{% endif %}
{% endblock source.content %}

{% block source.footer %}
---
## Directory Information

Directory `{{ object_path_info.given_relative }}/`

{% include "./object_info.md" %}
{% if index_filename_info %}
> Index File: `{{ index_filename_info.given_relative }}`

{% include "./object_info.md" with object_path_info=index_filename_info %}
{% else %}
No index file.
{% endif %}


{% endblock source.footer %}

{% block source.childlist %}
{{ object_list|length }} dir child{{ object_list|pluralize:',ren' }}

{% for unit in object_list %}+ {% link.rel unit.rel_path %}{% if unit.is_dir %}/{% endif %}
{% endfor %}
{% endblock source.childlist %}
