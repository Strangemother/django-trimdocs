# Extra Files Output

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