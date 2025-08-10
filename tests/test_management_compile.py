from pathlib import Path
import sys
import types

import django
from django.conf import settings
from django.core.management import call_command


def setup_module(module: types.ModuleType):
    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'trim',
                'trimdocs',
            ],
            SECRET_KEY='test',
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )
        django.setup()


def test_compile_copies_markdown(tmp_path: Path):
    src = tmp_path / 'srcdocs'
    dest = tmp_path / 'docs'
    (src / 'nested').mkdir(parents=True)
    (src / 'a.md').write_text('# A', encoding='utf-8')
    (src / 'nested' / 'b.md').write_text('# B', encoding='utf-8')

    call_command('trimdoc', 'compile', src=str(src), dest=str(dest))

    assert (dest / 'a.md').exists()
    assert (dest / 'nested' / 'b.md').exists()
