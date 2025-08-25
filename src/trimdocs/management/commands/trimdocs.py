from __future__ import annotations

import os
from pprint import pprint as pp
from pathlib import Path
from typing import Optional

from django.urls import resolve, reverse
from django.core.management.base import BaseCommand

from trimdocs.conf import get_settings
from trim.models import live
from trimdocs import utils
from django.conf import settings


class Command(BaseCommand):
    help = "Compile docs: partial Markdown -> Markdown/HTML with optional frame"

    def add_arguments(self, parser):

        subparsers = parser.add_subparsers(title="action")
        # compile ---------------------------------------------------------
        parser_compile = subparsers.add_parser('compile', help='compile help')
        parser_compile.set_defaults(func=self.handle_compile_docs)
        parser_compile.add_argument("--srcdocs", nargs="?", type=Path, default=settings.TRIMDOCS_SRC_DOCS)
        parser_compile.add_argument("--destdocs", nargs="?", type=Path, default=settings.TRIMDOCS_DEST_DOCS)
        parser_compile.add_argument("--create-destdocs", action='store_true', default=False)
        parser_compile.add_argument("--dry-run", action='store_true', default=False)

    def handle(self, *args, **options):
        action = options["func"]
        if action:
            return action(*args, **options)
        self._out_log('No action found.')

    def _out_success(self, *pr_str):
        self.stdout.write(self.style.SUCCESS(' '.join(pr_str)))

    def _out_log(self, *pr_str):
        """
        ERROR,
        ERROR_OUTPUT,
        HTTP_BAD_REQUEST,
        HTTP_INFO,
        HTTP_NOT_FOUND,
        HTTP_NOT_MODIFIED,
        HTTP_REDIRECT,
        HTTP_SERVER_ERROR,
        HTTP_SUCCESS,
        MIGRATE_HEADING,
        MIGRATE_LABEL,
        NOTICE,
        SQL_COLTYPE,
        SQL_FIELD,
        SQL_KEYWORD,
        SQL_TABLE,
        SUCCESS,
        WARNING
        """
        self.stdout.write(' '.join(map(str, pr_str)))

    def handle_compile_docs(self, *args, **options):

        self._out_success(f"trimdocs compile")

        # options.setdefault('srcdocs', settings.TRIMDOCS_SRC_DOCS)
        # options.setdefault('destdocs', settings.TRIMDOCS_DEST_DOCS)

        options['srcdocs'] = options['srcdocs'].absolute()

        assert options['srcdocs'].exists(), f"srcdocs does not exist, {options['srcdocs']}"

        dest_dir = options['destdocs']
        mk_dest_dir = options['create_destdocs']
        if dest_dir.exists() is False:
            if mk_dest_dir is False:
                assert dest_dir.exists(), f'destdocs does not exist: {dest_dir}'
            else:
                self._out_log(f'making dest directory, {dest_dir}')
                dest_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._out_log('Destination exists', dest_dir)

        assert dest_dir.exists(), 'destdocs does not exist'

        final_options = self.configure_compile_options(*args, **options)
        self.run_compile_docs(final_options)

    def run_compile_docs(self, options):
        """Compile the docs, given the options are normalised
        """
        src_dir = options['srcdocs']

        discover_patterns = settings.DISCOVER_PATTERNS
        keep, skips, count = utils.gather_files(src_dir, discover_patterns, 1)

        utils.scrub()
        self._out_log('count', live.trimdocs.PageModel.objects.all().count())
        utils.populate(keep, src_dir)
        self._out_log('count', live.trimdocs.PageModel.objects.all().count())
        """Populate missing files

        index, incidies, content etc..
        """
        # every dir should contain a readme.md and contents.md
        # if not, create one from contents.md
        self._out_success(f"Compiling {len(keep)} of {count} {discover_patterns} files.")
        return self.render_assets(options, keep)
        # return self.duplicate_assets(options, keep)

    def render_assets(self, options, keep):
        dest_dir = options['destdocs']
        src_dir = options['srcdocs']
        input_encoding = settings.INPUT_ENCODING
        output_encoding = settings.OUTPUT_ENCODING

        self._out_log('    dest_dir', dest_dir)

        dry_run = options.get('dry_run', True)

        if dry_run:
            self._out_log('\n == Dry Run (will not write the result). == \n')

        self._out_log('Writing files to', dest_dir)

        made = ()
        max_width = 20
        # Now a _copy_ - but through a picked renderer.
        for src_file in keep:
            # rel = src_file.relative_to(src_dir)
            rel = src_file.absolute().relative_to(src_dir.absolute())
            outp = dest_dir / rel
            if outp.parent.exists() is False:
                if dry_run is False:
                    self._out_log('Making destination', outp.parent)
                    outp.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # we pretend it got made.
                    pass

            str_rel_src_path = str(src_file.relative_to(src_dir).as_posix())
            max_width = max(max_width, len(str_rel_src_path)+2)

            self._out_log(f'  {str_rel_src_path:<{max_width}} => ', outp.relative_to(dest_dir))

            # render the view, by resolving the trimdocs:path
            view_name = 'trimdocs:path'
            view_args = (str_rel_src_path, )
            kwargs = {
                "path":  Path(str_rel_src_path).as_posix()
            }

            """
            The simulated request for the view/page to render.

                /trimdocs/path/ui-controls.md/?frame=minimal&html_render=True

            """
            class R:
                META = {}
                GET = {
                    # 'frame': 'minimal',
                    # 'html_render': 'true',
                    'frame': 'null',
                    'html_render': '',
                }

            request = R()
            resolve_match = resolve(reverse(view_name, args=view_args))
            view_class = resolve_match.func.view_class
            initkwargs = resolve_match.func.view_initkwargs
            view_class.view_initkwargs = initkwargs

            instance = view_class(**initkwargs)
            instance.setup(request, *view_args, **kwargs)
            # self._out_log('Requesting', view_args, kwargs)
            template_response = instance.get(request)
            rendered = template_response.render()

            # template = template_response.resolve_template(template_response.template_name)
            # context = template_response.resolve_context(template_response.context_data)
            # # permission denied.
            # try:
            #     content = template.render(context, template_response._request)
            # except PermissionError:
            #     # likely trying to read a special or dir as a file.
            #     import pdb; pdb.set_trace()  # breakpoint ca33a3ff //
            # # template = instance.resolve_template(instance.template_name)
            # # context = instance.resolve_context(instance.context_data)
            # # template_response = template.render(context, instance._request)
            # content = ''
            content = rendered.content

            if dry_run is False:
                # new_outp = outp.with_suffix('.html')
                # new_outp.write_bytes(content)
                outp.write_bytes(content)

                # outp.write_text(content, encoding=output_encoding)
            else:
                # we pretend it got made
                pass

            made += (
                    (src_file, outp,),
                )

        self._out_success(f"Compiled {len(made)} files.")

    def duplicate_assets(self, options, keep):
        dest_dir = options['destdocs']
        src_dir = options['srcdocs']
        input_encoding = settings.INPUT_ENCODING
        output_encoding = settings.OUTPUT_ENCODING

        self._out_log('    dest_dir', dest_dir)

        dry_run = options.get('dry_run', True)

        if dry_run:
            self._out_log('\n == Dry Run (will not write the result). == \n')

        self._out_log('Writing files to', dest_dir)

        made = ()
        max_width = 20
        # Now a _copy_ - but through a picked renderer.
        for src_file in keep:
            rel = src_file.relative_to(src_dir)
            outp = dest_dir / rel
            if outp.parent.exists() is False:
                if dry_run is False:
                    self._out_log('Making destination', outp.parent)
                    outp.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # we pretend it got made.
                    pass

            str_rel_src_path = str(src_file.relative_to(src_dir))
            max_width = max(max_width, len(str_rel_src_path)+2)

            self._out_log(f'  {str_rel_src_path:<{max_width}} => ', outp.relative_to(dest_dir))
            if dry_run is False:
                outp.write_text(src_file.read_text(encoding=input_encoding),
                                encoding=output_encoding)

            else:
                # we pretend it got made
                pass
            made += (
                    (src_file, outp,),
                )

        self._out_success(f"Compiled {len(made)} files.")

    def configure_compile_options(self, *args, **options):
        """Add any object configurations used to compile, such as root definitions
        """
        project = live.trimdocs.Project.objects.get_or_create(
                run_dir=os.getcwd(),
                src_dir=options['srcdocs'],
            )
        self._out_log(f'{project=}')
        return options