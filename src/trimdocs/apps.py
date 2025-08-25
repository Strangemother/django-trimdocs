from django.apps import AppConfig
from pathlib import Path

from django.core import management
from django.core.management.commands import migrate

import sqlite3
# management.call_command(migrate.Command(), verbosity=1)

# management.call_command("flush", verbosity=0, interactive=False)
# management.call_command("migrate", "test_data", verbosity=0)

class TrimDocsConfig(AppConfig):
    """Django AppConfig for trimdocs."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "trimdocs"

    def ready(self):
        # Mem migrate
        # management.call_command("migrate", verbosity=1)
        pass
    #     p = Path('trimdocs_project/db.sqlite3')
    #     print('realdb exists', p.exists())

    #     source = sqlite3.connect(p)
    #     # dest = sqlite3.connect(':memory:')
    #     print('Copying content into mem.')
    #     # source.backup(dest)
    #     from django.db import connections
    #     wrapper = connections['default']
    #     wrapper.connect()
    #     conn = wrapper.connection
    #     source.backup(conn)

    #     management.call_command(migrate.Command(), verbosity=1)
