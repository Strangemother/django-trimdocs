{% trimdocs.breadcrumbs %}{% load strings markdown %}

{% block source.content %}

{% include object.origin_path %}
{% comment "alt" %}
{% markdown %}{{ clean_content }}{% endmarkdown %}
{% endcomment %}

{% endblock source.content %}
{% block source.footer %}
---
## Source Information

+ Metadata: {{ metadata }}
+ File `{{ object.origin_path }}`
+ Breadcrumbs {{ object.as_path.parts }}

---
{% include "./object_info.md" %}
{% endblock source.footer %}

{% block source.childlist %}{% endblock source.childlist %}
