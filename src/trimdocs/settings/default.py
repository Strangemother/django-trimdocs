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

# No dest supplied will expect a an explicit dest when compiling.
TRIMDOCS_DEST_DOCS = None

INPUT_ENCODING = "utf-8"
OUTPUT_ENCODING = "utf-8"

# file types to discover when scanning for assets.
DISCOVER_PATTERNS = ("*.md", )
DIR_FILE_EXTENSIONS = (".md", )

