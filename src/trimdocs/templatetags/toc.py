"""
Render a TOC

    {% load toc %}
    {% toc %}

"""
import os.path
import datetime
from pathlib import Path
from collections import ChainMap

from django import template

from trim.templatetags.markdown import get_markdown_object


register = template.Library()


@register.simple_tag(name="spaces")
def make_spaces(multipler=1, offset=0, char=' '):
    count = ((multipler-1-offset) * 4) + 1
    # return f". {count} . "
    return char * count


@register.inclusion_tag("trimdocs/templatetags/toc.html",
                        takes_context=True, name='toc')
# @register.simple_block_tag(takes_context=True)
def double_render_toc(context, page='.', *args, **kwargs):

    view = context['view']
    view_class = view.__class__
    if view_class.view_initkwargs.get('is_toc_render', False) is True:
        # SKIP nested render
        print('Skip depth render')
        return {
            "title": "no",
            "path": "path",
        }
    # view_class = resolve_match.func.view_class
    # initkwargs = resolve_match.func.view_initkwargs
    # view_class.view_initkwargs = initkwargs
    kw = kwargs.copy()
    kw.setdefault('html_render', '')
    kw.setdefault('frame', 'null')
    kw.setdefault('is_toc_render', True)
    kw.update(view.kwargs)
    kw.update(kwargs)

    view_class.view_initkwargs =kw

    instance = view_class(**kw)
    request = context['request']

    instance.setup(request, *args, **kw)
    result = instance.get(request, *args, **kw)
    ss = result.rendered_content
    # Now TOC it.
    md = get_markdown_object(context, **kwargs)
    html = md.convert(ss)

    toc_tokens = md.toc_tokens
    start = kwargs.get('start', 0)

    if start > 0:
        # _start_ the childred at this level.

        depth = 0
        max_depth = 10

        while depth < max_depth:
            if toc_tokens[0]['level'] == start+1:
                # Found the level.
                break
            # destack children

            items = []
            for item in toc_tokens:
                items += item['children']

            toc_tokens = items

    return {
        'title': 'title',
        'path': 'path',
        'md': md,
        'toc': md.toc,
        'toc_tokens': toc_tokens,
        'start': start
    }

