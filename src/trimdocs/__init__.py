"""trimdocs package

Documentation tooling for Django using django-trim conventions.

Includes packaged example source trees (see :func:`get_example_path`).
"""

from importlib import resources
from pathlib import Path
from typing import Literal

__all__ = [
    "__version__",
    "get_example_path",
]

__version__ = "0.1.0a0"

ExampleFlavor = Literal["minimal", "full"]


def get_example_path(flavor: ExampleFlavor = "full") -> Path:
    """Return the absolute filesystem path to a packaged example docs tree.

    Parameters
    ----------
    flavor:
        Either ``"minimal"`` or ``"full"``. Defaults to ``"full"``.
    """
    base = resources.files(__name__) / "examples" / flavor
    # Convert to concrete file-system path (extract if inside a zip)
    return Path(str(base))

