{% trimdocs.breadcrumbs %}

{% block source.content %}
{% if object_path_info.given_relative  %}{% if object_path_info.given_absolute.is_file %}{% include object_path_info.given_relative_str %}{% endif %}
{% else %}No File. {{ object_path_info }}{% endif %}
{% endblock source.content %}


{% block source.footer %}
---
## Source Information

+ File `{{ object_path_info.given_relative }}`
+ Breadcrumbs {{ parenpath.rel.parts }}

This template presents a src file from the srcdocs - This should present the markdown rendered markdown.

{% if not object_path_info.given_absolute.exists %}# 404

If you're seeing this, your target file `{{ parenpath.rel }}` may not exist.<br>
However this page `{% firstof request.path parenpath.rel %}` will not exist in the destination compiled docs.

---{% endif %}

{% include "./object_info.md" %}

{% endblock source.footer %}

{% block source.childlist %}{% endblock source.childlist %}
