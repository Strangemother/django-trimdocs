{% trimdocs.breadcrumbs %}
{% block source.content %}
# 404

The given path `{{ parenpath|safe }}` is not a source file.

{% endblock source.content %}

{% block source.footer %}
---
## Source Information

+ File `{{ object.origin_path }}`
+ Breadcrumbs {{ object.as_path.parts }}

---
{% include "./object_info.md" %}
{% endblock source.footer %}

