import os.path
from pathlib import Path
from django import template
import datetime
from collections import ChainMap


register = template.Library()


# @register.inclusion_tag("trimdocs/templatetags/link_rel.html",
#                         takes_context=True, name='link.rel')
# @register.simple_block_tag(takes_context=True)
# def align(context, content, position='center'):
#     return f"""<div align="center" markdown=1>\n{content}\n</div>"""