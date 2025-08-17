# Mandates

+ trimdocs are always resolved finalised
+ Local referenced (markdown) final.
+ With assets bundled.
+ low-code
+ Underscore files and dirs aren't compiled automatically
+ The input docs (srcdocs) are never altered by the tool

---


In polypoint, data is read from the top of a source file, converting md header docs to html.

trimdocs should be able to traverse a source tree, and read to the headers, creatinga markdown for each file in the same dir location.

Furthermore the accessor can help with function doccing.

    module
      __init__.md
      file.py
      other.py
      foo/
        foo.py
        another.py

Producing docs:

    docs/
      sources/
        module
          readme.md
          __init__.md
          file.md
          other.md
          _indicies.md
          foo/
            readme.md
            foo.md
            another.md
            _indicies.md


Accessing module exports with locate and readers:

    {% for file in sources %}
        {{ file.__all__ }}
    {% endfor %}

---

When injecting new files..

For example, a _zoomed_ or large version of an image.

1. Apply a new URL in the compile
2. have a view, to present this larger image
3. compile, saving new assets in the relative location


---

### `project` var

In my app, I want to reference the name of the app, in several ways

+ Verbose: Django Trim Docs Version 1.1
+ Long: Django Trimdocs
+ Short: trimdocs
+ codey: django-trim

I should be able to access this though a complex project property

    {{ project.title.long }}

This project content can be collected from the package manifest.


### Asset destination (static file build)

Assets can be applied in one directory.
But links to those assets are relative

The dev may nominate a new store (such as a same directory path) and the asset is moved as required.

---

### Relative relative resolve

Link to:

    {% linkto "./foo/bar/baz.img" %}

#### OR

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


---


### extra files out

Add extra files

    (
      "/foo/bar/path.md"
    )

to a new file


    (
      ("/foo/bar/path.md", "/foo/out.md", )
    )

with special view:

    (
      ("/foo/bar/path.md",('trimdocs:path' "/foo/out.md", ))
    )


---

### Outs

one input, many outputs, allow variants.

Outputs include:

+ git view renderings
  + Flat markdown files (AKA Docs/)
    + Meta supported
    + JS/CSS/IMG supported
  + github docs/
    + No Meta support
    + NO JS/CSS support
    + IMG supported
  + gitlab docs/
    ...
  + github pages
  + Hugo
    + Meta supported
  + Browser (HTML Frame, and rendered markdown)
    + Meta supported
    + JS/CSS/IMG supported
  + HTML Flat Files (same as browser - e.g. self-hosted site)
    + Meta supported
    + JS/CSS/IMG supported

---

To process the content, we need a meta testing phase, of which reads srcdocs meta-data and processes tags.

This allows us to evaluate titles, meta, and post-parse knowledge, to process the final markdown

1. `compile` gathers target files
2. Process meta-data and rendered content
3. save-render, providing the ensured meta-data

This is because some tags may flag code changes, e.g. a _image_ has an optional name. These must be aggregated at the correct time, so files can be copied.

Elements like _breadcrumbs_ needs _titles_ and history. This may be expensive if computing every time, therefore when breadcrumbs compile, they need a pre-parsed history.

As a note, it feels acceptable to parse a file at request, because _runserver debug_ mode is expected to be minimal, compilation occurs once.


### CSS JS (Asset) tag

Some tags can be imported or written inline. The hugo supports inline CSS, but github docs do not. HTML files support imports.

This should be selected programaically at runtime, allowing for switch for e.g. github/docs (no css), hugo (inline css), browser (import css)

In the import case, we should also copy the file to dest. Therefore the tag needs to emit a flag after render.

    css.inline
    css.import
    css [detect]