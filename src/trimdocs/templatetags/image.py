"""
image

    {% load image %}
    {% image "./name.png" %}

"""
from pathlib import Path
from django import template


register = template.Library()


# @register.simple_block_tag(takes_context=True)
@register.inclusion_tag("trimdocs/templatetags/image.html",
                        takes_context=True, name='image')
def image_tag(context, rel_input_path, *args, **kwargs):
    """An image tag returns a markdown formatted image tag, with a URL
    configured for resizing:

        {% load image %}
        {% image "./images/logo.png" width=300 %}

    Markdown:

        ![title](images/logo-width-300-height-auto.png)

    The destination view is relative to the src docs:

        http://localhost:8000/trimdocs/path/images/logo-width-300-height-auto.png

    The `AssetView` will return a formated image FileResponse, reparsing the
    path into the real string and its attributes.

    Upon `compile`, this asset is copied to the destination docs, as the addressed name:

        images/logo-width-300-height-auto.png

    ---

    There's no enforced location for images (they can be anywhere) respecting
    relative paths and will be copied to the destdocs in the same format.

    """
    # Reshape URL to impart size.
    print(rel_input_path)
    p = Path(rel_input_path)
    if rel_input_path.startswith('./'):
        # is relative. If the object path is a file,
        # this needs to be fixed.
        if 'object' in context:
            current_path = context['object'].as_path()
        else:
            current_path = context['object_path_info']['given_relative']

        if current_path.is_file():
            p = '..' / p

    w = kwargs.get('width', 'auto')
    h = kwargs.get('height', 'auto')
    addition = f'-width-{w}-height-{h}'
    out_path = p.parent / (p.stem + addition + p.suffix)
    attrs, clean = parse_attrs_and_clean(out_path.as_posix())
    asset_stash = context.get('asset_stash', [])
    unit = {
        'image': {
            'rel_input_path': rel_input_path,
            'rel_output_path': out_path.as_posix(),
            'attrs': attrs,
            'clean_output_path': clean,
            'title': 'title',
        },
        **kwargs,
    }

    asset_stash.append({
            'asset_type': 'image',
            **unit['image'],
        })
    if 'asset_stash' not in context:
        context['asset_stash'] = asset_stash
    context['asset_cache']['asset_stash'] = asset_stash
    # If the filepath is within a path context, the
    return unit

import re
from pathlib import Path

def parse_attrs_and_clean(s: str, keys=("width", "height")):
    """
        # Example
        s = "foo/bar/baz/large-logo-width-400-height-auto.png"
        attrs, clean = parse_attrs_and_clean(s)

        print(attrs)
        # {'width': 400, 'height': 'auto'}

        print(clean)
        # foo/bar/baz/large-logo.png
    """
    # Extract attributes
    found = dict(re.findall(r"(\w+)-(auto|\d+)", s))
    result = {}
    for k in keys:
        v = found.get(k, "auto")
        result[k] = int(v) if v.isdigit() else v

    # Remove -key-value pairs
    clean_name = re.sub(r"-(%s)-(?:auto|\d+)" % "|".join(keys), "", s)

    return result, clean_name

