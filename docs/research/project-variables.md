# Project Variables

In my app, I want to reference the name of the app, in several ways

+ Verbose: Django Trim Docs Version 1.1
+ Long: Django Trimdocs
+ Short: trimdocs
+ codey: django-trim

I should be able to access this though a complex project property

    {{ project.title.long }}

This project content can be collected from the package manifest.