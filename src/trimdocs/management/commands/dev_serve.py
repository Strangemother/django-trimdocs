# from django.core.management.commands.runserver import Command as RunserverCommand
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from runpy import run_path
from pathlib import Path
import os


from django.core import management
from django.core.management.commands import migrate

class Command(RunserverCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'trimdocs_settings',
            # "--elk",
            # "-e",
            nargs='?',
            default=None,
            # action="store_true",
            # dest="use_ipv6",
            help="trimdocs settings file",
        )
        super().add_arguments(parser)

    def on_bind(self, server_port):
        print('\n\nBound to port', server_port)
        # management.call_command(migrate.Command(), verbosity=3)
        super().on_bind(server_port)

    # def inner_run(self, *args, **options):
    def run(self, *args, **options):
        # Check settings
        file = options['trimdocs_settings']
        filepath = Path(file)
        print('Testing file', file)
        print('exists', filepath.exists())
        if filepath.exists():
            # These settings are merged into the primary
            settings = run_path(filepath.absolute())
            os.environ["TRIMDOCS_SETTNGS_FILE"] = str(filepath.absolute())
            print('loaded', settings.keys())
        # super().inner_run(*args, **options)

        super().run(*args, **options)
