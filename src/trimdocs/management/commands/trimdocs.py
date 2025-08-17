from __future__ import annotations

from pprint import pprint as pp

from pathlib import Path
from typing import Optional

from django.urls import resolve, reverse

from django.core.management.base import BaseCommand

from trimdocs.conf import get_settings
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

            # scaffold --------------------------------------------------------
            parser_scaffold = subparsers.add_parser('scaffold', help='copy packaged example docs to a destination directory')
            parser_scaffold.set_defaults(func=self.handle_scaffold)
            parser_scaffold.add_argument('--flavor', choices=('minimal', 'full'), default='minimal')
            parser_scaffold.add_argument('destination', nargs='?', default='srcdocs')
            parser_scaffold.add_argument('--force', action='store_true', default=False, help='overwrite existing files')

    def handle(self, *args, **options):
        action = options["func"]
        if action:
            return action(*args, **options)
        print('No action found.')

    def _out_success(self, pr_str):
        self.stdout.write(self.style.SUCCESS(pr_str))

    def handle_compile_docs(self, *args, **options):

        self._out_success(f"trimdocs compile")

        options.setdefault('srcdocs', settings.TRIMDOCS_SRC_DOCS)
        options.setdefault('destdocs', settings.TRIMDOCS_DEST_DOCS)


        assert options['srcdocs'].exists(), f"srcdocs does not exist, {options['srcdocs']}"

        dest_dir = options['destdocs']
        mk_dest_dir = options['create_destdocs']
        if dest_dir.exists() is False:
            if mk_dest_dir is False:
                assert dest_dir.exists(), 'destdocs does not exist'
            else:
                print(f'making dest directory, {dest_dir}')
                dest_dir.mkdir(parents=True, exist_ok=True)
        else:
            print('Destination exists', dest_dir)

        assert dest_dir.exists(), 'destdocs does not exist'

        final_options = self.configure_compile_options(*args, **options)
        self.run_compile_docs(final_options)

    def run_compile_docs(self, options):
        """Compile the docs, given the options are normalised
        """
        src_dir = options['srcdocs']

        print('')
        print('running compilation of: ')
        print('    src_dir', src_dir)
        # For now, create the destination directory and copy .md files verbatim
        count = 0
        """For every file in the srcdocs, create the sibling in the destination.
        Functionality this is a copy/paste - but through a markdown renderer view.

        For each file, call to the path view renderer, render the text and write
        it to the destination.

        However, writing needs to be cached, so we can perform any
        cross-referencing later. This may be memory intensive, so a flag for
        _write now_ should be appliable.
        """

        print('')

        discover_patterns = settings.DISCOVER_PATTERNS

        keep = ()
        skips = ()
        for pattern in discover_patterns:
            for src_file in src_dir.rglob(pattern):
                count += 1
                name = src_file.name
                # And excludes?
                if any(x.name.startswith('_') for x in src_file.parents):
                    print('x Skip', src_file)
                    skips += (src_file,)
                    continue
                keep += (src_file, )
                prefix = '  '
                if name == 'readme.md':
                    prefix = ' *'
                rel = src_file.relative_to(src_dir)
                print(f"{prefix}{rel}")

        print('')
        pp(options)
        print('\n')

        """Populate missing files

        index, incidies, content etc..
        """
        # every dir should contain a readme.md and contents.md
        # if not, create one from contents.md
        self._out_success(f"Compiling {len(keep)} of {count} {discover_patterns} files.")
        return self.render_assets(options, keep)
        # return self.duplicate_assets(options, keep)

    # ------------------------------------------------------------------
    # Scaffold
    # ------------------------------------------------------------------
    def handle_scaffold(self, *args, **options):
        """Copy the packaged example docs tree to a destination.

        This lets users quickly bootstrap a docs directory.
        """
        from trimdocs import get_example_path
        import shutil

        flavor = options['flavor']
        dest = Path(options['destination'])
        src = get_example_path(flavor)
        if not src.exists():
            self.stderr.write(self.style.ERROR(f"Example flavor not found: {flavor}"))
            return 1
        if dest.exists() and any(dest.iterdir()) and not options['force']:
            self.stderr.write(self.style.ERROR(f"Destination {dest} exists and is not empty (use --force)."))
            return 1
        dest.mkdir(parents=True, exist_ok=True)
        # Copy tree (shutil.copytree requires non-existing dst; do manual walk)
        for path in src.rglob('*'):
            rel = path.relative_to(src)
            outp = dest / rel
            if path.is_dir():
                outp.mkdir(parents=True, exist_ok=True)
                continue
            if outp.exists() and not options['force']:
                continue
            outp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, outp)
        self._out_success(f"Scaffolded '{flavor}' example into {dest}")
        return 0

    def render_assets(self, options, keep):
        dest_dir = options['destdocs']
        src_dir = options['srcdocs']
        input_encoding = settings.INPUT_ENCODING
        output_encoding = settings.OUTPUT_ENCODING

        print('    dest_dir', dest_dir)

        dry_run = options.get('dry_run', True)

        if dry_run:
            print('\n == Dry Run (will not write the result). == \n')

        print('Writing files to', dest_dir)

        made = ()
        max_width = 20
        # Now a _copy_ - but through a picked renderer.
        for src_file in keep:
            rel = src_file.relative_to(src_dir)
            outp = dest_dir / rel
            if outp.parent.exists() is False:
                if dry_run is False:
                    print('Making destination', outp.parent)
                    outp.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # we pretend it got made.
                    pass

            str_rel_src_path = str(src_file.relative_to(src_dir))
            max_width = max(max_width, len(str_rel_src_path)+2)

            print(f'  {str_rel_src_path:<{max_width}} => ', outp.relative_to(dest_dir))

            # render the view, by resolving the trimdocs:path
            view_name = 'trimdocs:path'
            view_args = (str_rel_src_path, )
            kwargs = {
                "path":  str_rel_src_path
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

        print('    dest_dir', dest_dir)

        dry_run = options.get('dry_run', True)

        if dry_run:
            print('\n == Dry Run (will not write the result). == \n')

        print('Writing files to', dest_dir)

        made = ()
        max_width = 20
        # Now a _copy_ - but through a picked renderer.
        for src_file in keep:
            rel = src_file.relative_to(src_dir)
            outp = dest_dir / rel
            if outp.parent.exists() is False:
                if dry_run is False:
                    print('Making destination', outp.parent)
                    outp.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # we pretend it got made.
                    pass

            str_rel_src_path = str(src_file.relative_to(src_dir))
            max_width = max(max_width, len(str_rel_src_path)+2)

            print(f'  {str_rel_src_path:<{max_width}} => ', outp.relative_to(dest_dir))
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
        return options