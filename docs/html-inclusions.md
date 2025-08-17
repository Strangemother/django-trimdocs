# HTML Inclusions

Sometimes your markdown may not parse correctly if HTML is applied

Works. All content is correctly parsed into HTML:

```jinja2
{% include "_readme/intro.md" %}
{% include "trimdocs/badges/pypi.md" %}
```

Fails, the _badges_ render as _pure_ markdown:

```jinja2
<div align="center">
{% include "_readme/intro.md" %}
{% include "trimdocs/badges/pypi.md" %}
</div>
```

To fix this, we use the _markdown builtin_, to detect markdown within HTML entities:

Works:

```jinja2
<div align="center" markdown=1>
{% include "_readme/intro.md" %}
{% include "trimdocs/badges/pypi.md" %}
</div>
```