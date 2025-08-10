from dataclasses import dataclass
from typing import Optional

from django.conf import settings


@dataclass(frozen=True)
class TrimDocsSettings:
    """Resolved settings for trimdocs.

    Attributes
    ----------
    srcdocs: str
        Source docs directory with authoring (partial) markdown/templates.
    dest: Optional[str]
        Default destination directory for compiled output. If None, compile
        into the source directory.
    frame: Optional[str]
        Name of the rendering frame to apply for HTML output.
    format: str
        Output format ("markdown" or "html").
    """

    srcdocs: str = "srcdocs"
    dest: Optional[str] = "docs"
    frame: Optional[str] = None
    format: str = "markdown"


DEFAULTS = TrimDocsSettings()


def get_settings() -> TrimDocsSettings:
    data = getattr(settings, "TRIM_DOCS", {}) or {}
    return TrimDocsSettings(
        srcdocs=data.get("srcdocs", DEFAULTS.srcdocs),
        dest=data.get("dest", DEFAULTS.dest),
        frame=data.get("frame", DEFAULTS.frame),
        format=data.get("format", DEFAULTS.format),
    )
