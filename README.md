# django-trimdocs

Author-friendly docs pipeline for Django projects. Write partial Markdown with optional Django/Jinja sugar; compile to Markdown or HTML with frames. Ships as a Django app (`trimdocs`) and CLI (`trim-docs`).

See `docs/research/trim-docs.md` in the django-trim repo for the concept draft.

## Quickstart

```bash
pip install trimdocs
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'trim',      # django-trim
    'trimdocs',  # this package
]

TRIM_DOCS = {
    'srcdocs': 'srcdocs',
}
```

Run via CLI:

```bash
trim-docs compile --dest docs/
```

Or via Django management command:

```bash
python manage.py trimdoc compile --dest docs/
```

Initial version copies `.md` files from `srcdocs` to `docs`. Subsequent releases will add templating, frames, TOC, images, and plugins.
