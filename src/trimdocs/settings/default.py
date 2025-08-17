"""
from trimdocs.settings.default import *

The folders may need to resolve outside the django root folder.
But this is okay with the following:

+ The docs/ folder is considered root for markdown source only
+ Is dev
+ The compiled result is flat and doesn't include the root srcdocs

So build a complex relative, and absolute it:

    SITE_DIR = (Path(__file__).parent / '../../../../').resolve().absolute()
    TRIMDOCS_SRC_DOCS = SITE_DIR / 'srcdocs/'

"""

# Access the example src, complete with a complex example inside the module templates/
# templates/...
# TRIMDOCS_SRC_DOCS = 'trimdocs/srcdocs/'

# example for your settings.py
"""
from trimdocs.settings.default import *
SITE_DIR = (Path(__file__).parent / '../../../../').resolve().absolute()
# one more step out of site to root
ROOT = (SITE_DIR.parent / '../').resolve().absolute()

TRIMDOCS_SRC_DOCS = SITE_DIR / 'demo-srcdocs/'
TRIMDOCS_DEST_DOCS = ROOT / "docs/"
TRIMDOCS_README_SRCFILE = TRIMDOCS_SRC_DOCS / 'SRC_README.md'
TRIMDOCS_README_DESTFILE = ROOT / 'README.md'

"""

# No dest supplied will expect a an explicit dest when compiling.
TRIMDOCS_DEST_DOCS = None
TRIMDOCS_README_SRCFILE = None
TRIMDOCS_README_DESTFILE = None

INPUT_ENCODING = "utf-8"
OUTPUT_ENCODING = "utf-8"

# file types to discover when scanning for assets.
DISCOVER_PATTERNS = ("*.md", )
DIR_FILE_EXTENSIONS = (".md", )

