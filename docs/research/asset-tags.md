# Asset Tags (CSS/JS)

Some tags can be imported or written inline. The hugo supports inline CSS, but github docs do not. HTML files support imports.

This should be selected programaically at runtime, allowing for switch for e.g. github/docs (no css), hugo (inline css), browser (import css)

In the import case, we should also copy the file to dest. Therefore the tag needs to emit a flag after render.

    css.inline
    css.import
    css [detect]