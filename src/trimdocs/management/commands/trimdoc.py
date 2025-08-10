from __future__ import annotations

from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand

from trimdocs.conf import get_settings


class Command(BaseCommand):
    help = "Compile docs: partial Markdown -> Markdown/HTML with optional frame"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("compile",))
        parser.add_argument("src", nargs="?", default=None)
        parser.add_argument("--dest", dest="dest", default=None)
        parser.add_argument("--frame", dest="frame", default=None)
        parser.add_argument(
            "--format", dest="format", default=None, choices=("markdown", "html")
        )

    def handle(self, *args, **options):
        action = options["action"]
        if action == "compile":
            self.compile_docs(
                src=options.get("src"),
                dest=options.get("dest"),
                frame=options.get("frame"),
                out_format=options.get("format"),
            )
            return

    # -- core ---------------------------------------------------------------
    def compile_docs(
        self,
        src: Optional[str],
        dest: Optional[str],
        frame: Optional[str],
        out_format: Optional[str],
    ) -> None:
        conf = get_settings()
        srcdir = Path(src or conf.srcdocs).resolve()
        destdir = Path(dest or conf.dest or conf.srcdocs).resolve()
        frame_name = frame or conf.frame
        fmt = (out_format or conf.format or "markdown").lower()

        self.stdout.write(
            self.style.SUCCESS(
                f"trimdocs compile src={srcdir} dest={destdir} format={fmt} frame={frame_name}"
            )
        )
        # For now, create the destination directory and copy .md files verbatim
        destdir.mkdir(parents=True, exist_ok=True)
        count = 0
        for p in srcdir.rglob("*.md"):
            rel = p.relative_to(srcdir)
            outp = destdir / rel
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Compiled {count} markdown files."))
