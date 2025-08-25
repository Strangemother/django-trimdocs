# Path Resolution

## Relative relative resolve

Link to:

    {% linkto "./foo/bar/baz.img" %}

### OR

return a path, given a source, destination, and _root_ location.
The returned path is relative to the root location, If a root location isn't applied, the source location, relative to the _root_ is used.

    from A to B, through C
    res_path = rel_rel(source, desination, root)

if source is not abs, use configured `srcdocs`
if root is not defined, use the `destdocs`
if destination is undefined, assume _this_, being the `source`

    rel_rel('assets/img/image.png')
    # resolves
    rel_rel('assets/img/image.png', 'assets/img/image.png', TRIMDOCS_SRC_DIR)
    assets/img/image.png

Example. We want to link to another file. From a sub directory of another location
```py

source_root = '/root/local/projects/myapp/srcdocs/'
dest_root   = '/root/local/projects/myapp/docs/'

# This is where we are, the _current_ place
source = 'foo/bar/baz/bax/bar.md'
# /root/local/projects/myapp/srcdocs/foo/berf/bar/baz/bax/bar.md
# Linking to another ancestor
# /root/local/projects/myapp/srcdocs/foo/berf/yom/florp.md
res_path = rel_rel(source, desination, dest_root, source_root)
"../../../yom/florp.md"
# Result
# /root/local/projects/myapp/srcdocs/foo/berf/../../../bar.md
```

Allowing the markdown to correctly link to the internal reference.