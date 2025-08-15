"""Base URLs for trimdocs within the django apps:

        from trim.urls import path_includes_pair as includes

        urlpatterns += includes(
                    'trimdocs',
                )

By default the django trimdocs is configured to look for a DOCS url.
"""
from django.urls import include, path, re_path

from docs import views
from trim import urls

from . import views

app_name = 'trimdocs'

urlpatterns = urls.paths_named(views,
    index=('ExampleIndexTemplateView', '',),
    indicies=('IndiciesPathView', (
                "indicies/",
                "indicies/<path:path>/",
                # Captures
                # "path/<path:path>/_indicies/",
                # "path/<path:path>/_indicies.md/",
                )
            ),
    contents=('ContentsPathView', (
                "contents/",
                "contents/<path:path>/",
                # Captures
                # "path/<path:path>/_contents/",
                # "path/<path:path>/_contents.md/",
                )
            ),
    path=('PathView', ("path/", "path/<path:path>/")),
    dir=('PathDirView', ("dir/", "dir/<path:path>/")),

    trimdocs_suppliments=('TrimdocsSupplimentsIndexTemplateView', ('', 'trimdocs/'),),

    # theatre_src=('TheatreSrcAssetView', ('theatre/<path:path>',)),
    # script_raw=('ScriptsRawImportView', 'script_list_raw/<str:name>/'),
    # image_post_form=('ImagePostFormView', 'upload/image/'),
    # file_example_png=('ExampleExtFileView', '<path:path>.png/'),
    # file_example_html=('ExampleExtFileView', '<path:path>.html/'),
)


