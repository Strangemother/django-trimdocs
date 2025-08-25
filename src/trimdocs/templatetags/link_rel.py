import os.path
from pathlib import Path
from django import template
import datetime
from collections import ChainMap


register = template.Library()


@register.inclusion_tag("trimdocs/templatetags/link_rel.html",
                        takes_context=True, name='link.rel')
def markdown_link_relative(context, target, title=None, *args, **kwargs):
    """ Convert a link to another relative link:

        {% link.rel "bunny/nested/panda/purple/window/eric.md" %}

    Given: bunny/nested/example/doccing/text.md/
    Dest: bunny/nested/panda/purple/window/eric.md
    Result: ../../../panda/purple/window/eric.md
    """
    return link_data(context, target, title=title, **kwargs)


@register.simple_tag(takes_context=True, name='link.relpath')
def markdown_link_relative_path(context, target, title=None, *args, **kwargs):
    return link_data(context, target, title=title, **kwargs)['path']


def link_data(context, target, title=None, **kwargs):
    dest = Path(target)
    here = context['object_path_info']['given']
    res = Path(os.path.relpath(dest, here)).as_posix()
    clean_title = dest.name if res == '.' else res
    title = title or kwargs.get('title') or clean_title

    return {
        'path': res,
        'title': title,
    }


