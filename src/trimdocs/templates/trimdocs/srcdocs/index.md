{% load link %}
# Getting Started

This is the builtin `trimdocs/` page within the templates folder. It should default to reading a `TRIMDOCS_SRC_DOCS` directory.

if you're reading this, the next steps are:

## Step 1 {% if has_src_docs %}(Complete{% if src_docs_exists is False %} with issues{% endif %}){% endif %}

{% if src_docs_exists is False %}
> **The `TRIMDOCS_SRC_DOCS` directory does not exist `{{ src_docs_path }}`**
{% endif %}

Point trimdocs at your exiting `docs/` directory to render them in the browser.

```py
SITE_DIR = (Path(__file__).parent / '../').resolve().absolute()
TRIMDOCS_SRC_DOCS = SITE_DIR / 'srcdocs/'
```

## Step 2 {% if has_dest_docs %}(Complete{% if dest_docs_exists is False %} with issues{% endif %}){% endif %}

{% if dest_docs_exists is False %}
> **The `TRIMDOCS_DEST_DOCS` directory does not exist `{{ dest_docs_path }}`**

This is acceptable if:

+ Intend to view your files within the browser
+ Supply a destination directory during the compile stage (optional)

---

{% endif %}

Now setup a "destination", where you will put your _pre markdown_.

> To cheat: copy your existing `docs/` to a `srcdocs/`

In your `settings.py`, add the `TRIMDOCS_DEST_DOCS`


```py
# Continued from above ...
TRIMDOCS_DEST_DOCS = SITE_DIR / "demo-build-docs/",
```

Refresh this page again to see it detected

## Step 4

Refresh this page, (or navigate to your `trimdocs/` endpoint) to see your `readme.md`.

{% link "trimdocs:index" "Goto Index" %}