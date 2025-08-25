# notes

## Importants

+ All links should be relative to their current position
    e.g. a reference should correctly apply relative linking `../../../foo/bar/`
+ The end result is always invsible; A person may not be aware the pre-processing step occurred.

## Concept

A developer should be able to apply a range of small elements to build a nice Docs and its subset.

+ A top level readme
    + Maybe generated automatically if missing
+ docs/ readme
    + The top level readme file contains logo, intro, toc

The a readme is is faster to create:

```markdown
# {{ title }}

{% image "assets/images/logo.png" %}
{% include "trimdocs/badges" names=options.badges %}

{% lorem %}

{% toc . depth=3 %}

{% include "docs/getting-started.md" %}


{% license "mit" %}
```


## Output Terminology

This aims for a clean markdown output, structured, hybrid, or site

+ Clean: Produce pure output, no adaptions, only jinja replacements
    + Github
+ Structured: For `Hugo` or other strong structure receivers.
    + Hugo
+ Hybrid: Adaptive receivers, with HTML rendering capabilities
    + Hugo
    + Confluence
    + Personal
Site: Designed to slot into a website, e.g. _this one_
    + personal hosted
    + trimdocs
    + compiled html


## Asset collection

Images, CSS, JS may be applied. The linked URLS should be relative to bundled assets.
They should exist in the nominated location (if not already.) and copied into the dest upon `compile`.

### Example with Images

An example may be an _image_, pulled from an asset directory, resized, and stored relative to the file.
The result should be a markdown image tag, with the new reference:

    {% image "assets/images/logos/primary-inverted.png" "Logo image" width=400 save_as="./imgs/logo-400.png" %}

markdown:

    ![Logo image][./imgs/logo-400.png]

## tags

### {% env %} and {% options %}

Properies in the runtime and environment. Flags applied through the compile (like nim)

    platform: {{ env.platform }} <!-- linux -->
    dest: {{ options.destFormat }} <!-- github -->

make-like compilation:

    {% if options.destFormat == "custom" %}
    ## Custom options
    {% endif %}


### Tite and Title capture

A title may be supplied and applied in many forms.

+ Though the page name
+ meta data
+ H1 tag

The H1 may want to be dynamic `{{ title }}`, potentially applied through the meta:

```
title: my title
```

But some platforms (Hugo) provide strict guidleines to H1 creation.
As such, perhaps apply a test for platform

```markdown
    ---
    title: meta applied title
    ---
    {% if dest != "hugo" %}
    # {{ title }}
    {% endif %}
```

Serving all platforms.


### {% image %}

A relative image page insert

the iamge tag should allow the import of an image from a file

This builds a link relative in the srcdocs, and copies the image to the destdocs

    {% image "./local/path/logo.png" %}
    ![logo](./local/path/logo.png)

Rename the image or dest on output

    {% image "./local/path/logo.png" "./assets/img/logo.png" %}
    ![logo](./assets/img/logo.png)

    {% image "./local/path/logo.png" "./imgs" %}
    ![logo](./imga/logo.png)

We also want renaming and file resize

    {% image "./local/path/logo.png" "./imgs" width=400 %}
    ![logo](./imgs/logo-400.png)

Relative file location needs to know the current file dest

    # file /docs/bill/and/teds/excellent/adventure.md
    # IMAGES_DEST = '/docs/imgs/'

    {% image "./logo.png" IMAGES_DEST %}
    ![logo](../../../../imgs/logo.png)


---

run return as html or md `image.html`, `image.md` is the same as `image`


### {% toc . depth=3 %}

A TOC of a file or directory

    + [home](readme.md)
        + [foo](./foo/readme.md)
        + [bar](./bar/)
        + [baz](./baz)
            + [file.md](./baz/file.md)

Notably, relative displacement should be handled gracefully


A TOC of a file or directory

    {% toc .. depth=3 %}
    + [home](../readme.md)
        + [foo](../foo/readme.md)
        + [bar](../bar/)
        + [baz](../baz)
            + [file.md](../baz/file.md)


Relative to the current file location

    {% toc ../foo/ depth=3 %}
    + [home](../foo/readme.md)
        + [other](../foo/other/readme.md)
        + [frog](../foo/frog/)
            + [file.md](../foo/frog/file.md)


### {% breadcrumbs %}

relative list of markdown links,

    + [home](../../../)
    + [foo](../../)
    + [bar](../)
    + [baz](./)
    + [file.md](./file.md)

### {% siblings %}

relative files and dirs (to the current file/dir)

### {% parents %}

Read up the tree

### {% children %}

...

### {% code ... %}

Drop in code from example sources, reuse the same snippet, or wrap a code block with enhancements.


---

badge choice and options from settings to select builtin badges

+ With options to read build patterns (pyproject.toml)

---


home page Readme support mapped to `trimdocs/`, as the `trimdocs/path/` points into the srcdocs

---

Why not support any input type? Markdown, ReStructred text, txt files, ... anything to convert really.

---


### DB Support.

Say I have a list of links, or assets in DB models. The view should be able to access those.
Maybe using live models, and functional tags

    {% db live.products.Products.objects.all.count %}

Pressing compile would of course _stick_ that value.

---

Links could be backed by a database - where we store references and link to those in the MD

    {% link.named "polypoint-github" "github link" %}

This could also produce a file `/_links.md`

---

maybe perform `folder/readme.md` for all top-level files, for neater urls.

---

Can build fancy html wrappers using the `wrap` and `slots`

---

Read/use/apply Other assets, and readers for special formats:

Apply formatted json from another file:

    A settings for install:

    {% file.json "./assets/app/config.json" indent=4 %}
    Use your config with the `app.sh config.json`


output:

    A settings for install:

        {
            foo: 1
            bar: true
        }

    head to [install page](../install-page.md) to grab your app. [click here](github.com/assets/file.json) to download

    Use your config with the `app.sh config.json`


Build a code reader for your custom output:


```markdown
pre formatted form

    {% code.js "examples/points.js"%}

```

---

Tag box

> may require pre--processing of all files before rendering.

grab and render a group of pages based on tags.

Some file:

    ---
    tag: foo
    filename: eggs.md
    ---


    ---
    tag: foo
    filename: other.md
    ---


Usage:

    {% tag.box "foo" title="{tag} tags:" %}

output:

```

"Foo" tags:

+ [eggs](./eggs.md)
+ [other](./other.md)
```

---

Functional lists and stacks

+ Read functions, print their signature and docs e.g. polypoint functions
+ Iterate code files, listing as content - e.g. _trim fields_

---

many outputs

+ convert to github, hugo, html, browser - at once.

---

File injection

At times I may want to inject files into the output, e.g. a file with a list of links, or a new page dedicated to asset presentation (e.g. a fullpage image.)

Under the hood, this will add a new _path_ to the compilation set, A unique view captures and renders (as expected). This ensures a user doesn't need to use alternative tags.

---

### Model Backed

Pure files is fine, but we can back the files using models to make the rendering amazing.

A _Page_ model can be gathered at runtime, pushed into the table and iterated like normal models. Using a memory sqlite database (and an init-db cloner... from celeste-os)

A model can then:

+ contain slug
+ origin file, dest file
+ parents list
+ tags and markdown meta data
+ md init text.

When compiling, or reading the file structure we perform a bulk update for all pages.
Job done.

---

### Flat file

Convert the entire source into a single flat file, indexed by folder depth
