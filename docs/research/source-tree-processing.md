# Source Tree Processing

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