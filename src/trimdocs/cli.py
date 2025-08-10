from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import django
from django.conf import settings as dj_settings
from django.core.management import call_command


def ensure_django_configured() -> None:
    if not dj_settings.configured:
        # Minimal settings for running management command without a project.
        dj_settings.configure(
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "trim",
                "trimdocs",
            ],
            SECRET_KEY="trimdocs-cli",
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        django.setup()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="trim-docs", description="Compile docs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_compile = sub.add_parser("compile", help="Compile docs from src to dest")
    p_compile.add_argument("src", nargs="?", default=".")
    p_compile.add_argument("--dest", default=None)
    p_compile.add_argument("--frame", default=None)
    p_compile.add_argument("--format", default=None, choices=["markdown", "html"])

    args = parser.parse_args(argv)

    ensure_django_configured()

    if args.cmd == "compile":
        kwargs = {k: v for k, v in {
            "src": args.src,
            "dest": args.dest,
            "frame": args.frame,
            "format": args.format,
        }.items() if v is not None}
        call_command("trimdoc", "compile", **kwargs)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
