from django import template
import datetime
from collections import ChainMap


register = template.Library()


@register.simple_tag
def current_time(format_string=None):
    """ {% current_time %} """
    return 'current_time'
    # return datetime.datetime.now().strftime(format_string)


@register.inclusion_tag("trimdocs/templatetags/breadcrumbs.html",
                        takes_context=True, name='trimdocs.jump_link')
def jump_link(context, *args, **kwargs):
    return {
        "link": "home_link",
        "title": "home_title",
    }

@register.inclusion_tag("trimdocs/templatetags/breadcrumbs.html",
                        takes_context=True, name='trimdocs.breadcrumbs')
def breadcrumbs(context, *args, **kwargs):
    parenpath = context['parenpath']
    res = ()
    total_distance = len(parenpath.rel.parents)
    for parent in parenpath.rel.parents:

        # Steps applies the count _away from the total_.
        #
        # This creates a reversed list, because the closest relative link
        # (0, being _here_), is also the furthest away (in steps)
        #
        # So after we calculate each parent directory step back,
        # reverse it, so the _furthest away_ (this file) is at the end.
        steps = total_distance - (len(parent.parts))
        rel_link = '../' * steps
        distance = total_distance - steps
        name = parent.name
        if len(name) == 0:
            name = '{root}'
        res += ({
                'rel_link':rel_link,
                "name": name,
                "path": parent,
                "distance": distance,
            }, )

    info = {
        'crumbs': reversed(res)
    }
    return ChainMap(context, info, kwargs)