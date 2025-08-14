"""Base URLs for trimdocs within the django apps:

        from trim.urls import path_includes_pair as includes

        urlpatterns += includes(
                    'trimdocs',
                )

By default the django trimdocs is configured to look for a DOCS url.
"""
from django.urls import include, path

from docs import views
from trim import urls

from . import views

app_name = 'trimdocs'

urlpatterns = urls.paths_named(views,
    index=('ExampleIndexTemplateView', '',),

    path=('PathView', ("path/", "path/<path:path>/")),
    dir=('PathDirView', ("dir/", "dir/<path:path>/")),
    # src_dir=('DirView', "dir/<path:path>/"),

    trimdocs_suppliments=('TrimdocsSupplimentsIndexTemplateView', ('', 'trimdocs/'),),

    # theatre_process=('ImmediateProcessTheatreFilesView', ('process/',)),
    # point_src=('PointSrcAssetView', ('point_src/<path:path>',)),
    # theatre_src=('TheatreSrcAssetView', ('theatre/<path:path>',)),
    # script_raw=('ScriptsRawImportView', 'script_list_raw/<str:name>/'),
    # script_list=('ScriptsImportListView', 'script_list/<str:name>/'),
    # image_post_form=('ImagePostFormView', 'upload/image/'),

    # clone_file=('CloneFileView', 'clone/<path:path>/',),
    # rename_file=('RenameFileView', 'rename/<path:path>/',),
    # # file_example_png=('ExampleExtFileView', '<path:path>.png/'),
    # file_example_images=('ExampleFileImagesView', 'images/<path:path>/'),

    # ## View the file-list only.
    # file_example_scrips=('ExampleFileScriptsView', 'scripts/<path:path>/'),

    # # Catch-all
    # file_example=('ExampleFileView', '<path:path>/'),
    # file_example_html=('ExampleExtFileView', '<path:path>.html/'),

)

