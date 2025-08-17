# README File layout

Your documentation may expose two primary elements:

+ README file: The _top level_ `README.md`, outside the primary _docs_ directory
+ The docs directory: Defined as the _root_ `srcdocs` (source docs), it may also have a _README.md_

But they are not the same.

---

Github reads them uniquely. If the top-level is missing, it utilises the `docs/README.md`.

---

For output, this changes the format for of the results.

Expected:

    {root}
       | LICENSE
       | setup.py
       | README.md
       + docs/
         | README.md
         | getting-started.md
         | more/
       + src/
         ...

Input:

    {root}
       | README.md
       ...
       + srcdocs/
         | README.md
         | ...
         | more/
       + src/
         ...

(Current) Output (without README config)

    {root}
       | README.md
       ...
       + destdocs/
         | README.md
         | ...
         | more/
       + srcdocs/
         ...
       + src/
         ...

(Changed) Output (with README config):

    {root}
       | README.md
       ...
       + docs/
         | README.md
         + docs/
            | README.md
            | ...
            | more/
       + srcdocs/
         ...
       + src/
         ...


**However** this is unpreferred. Because it leads to a nested output.


(ALT Changed) Input (with README config):

    {root}
       | # README.md # does not exist
       ...
       + srcdocs/
         | SRC_README.md
         + docs/
           | README.md
           | ...
           | more/
       + src/
         ...

Leading to the preferred output:

    {root}
       | README.md # created.
       ...
       + docs/
         | README.md
         | ...
         | more/
       + srcdocs/
         | SRC_README.md
         + docs/
           | README.md
           | ...
           | more/
       + src/
         ...


---

All of this can be configured through the settings, as the DEST DOCS is created where needed (note relative imports need to be considered).

