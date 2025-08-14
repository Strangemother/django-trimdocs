from pathlib import Path
from pprint import pprint as pp

from django.shortcuts import redirect
from django.conf import settings
from django.utils.functional import cached_property
from django.urls import resolve, reverse

from trim import views


FRAME_MAP = {
    'minimal': "trimdocs/base/minimal.html",
    'base': "trimdocs/base/base.html",
    'null': "trimdocs/base/null.html"
}


class ExampleIndexTemplateView(views.TemplateView):
    template_name = 'trimdocs/example_index.html'

    def get_frame_name(self):
        frame = self.request.GET.get('frame', 'base')
        return FRAME_MAP.get(frame)

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        r['trimdocs_global_frame'] = self.get_frame_name()
        return r

    def get(self, request, *args, **kwargs):
        has_src_docs = hasattr(settings, 'TRIMDOCS_SRC_DOCS')

        if has_src_docs:
            # The user has implemented the root directory... Continue to
            # index viewer.
            src_docs_path = Path(settings.TRIMDOCS_SRC_DOCS)
            context = self.get_context_data(**kwargs,
                    has_src_docs=has_src_docs,
                    src_docs_path=src_docs_path,
                    )
            return self.render_to_response(context)

        # Pre-configured install page with example.
        return redirect('trimdocs:trimdocs_suppliments')



class TrimdocsSupplimentsIndexTemplateView(views.TemplateView):
    """Show a page of trimdocs extra infos for the developer. This includes

    + A readme page (the primary pre-configured exampe)
    + Potentially any internal settings etc.

    By default this should be shown to the developer in the index,
    then the index switches away, with this URL still exposed.
    """
    template_name = 'trimdocs/suppliment_index.html'

    def get_context_data(self, **kw):
        res = super().get_context_data(**kw)
        has_src_docs = hasattr(settings, 'TRIMDOCS_SRC_DOCS')
        has_dest_docs = hasattr(settings, 'TRIMDOCS_DEST_DOCS')

        # check docs is a path and exists.
        src_docs_path = Path(settings.TRIMDOCS_SRC_DOCS)
        dest_docs_path = Path(settings.TRIMDOCS_DEST_DOCS)

        res['src_docs_path']= src_docs_path
        res['dest_docs_path']= dest_docs_path

        res['src_docs_exists'] = res['src_docs_exist'] = src_docs_path.exists()
        res['dest_docs_exists'] = res['dest_docs_exist'] = dest_docs_path.exists()

        res['has_src_docs'] = has_src_docs
        res['has_dest_docs'] = has_dest_docs

        return res


def get_directory_list(path_info):
    """The absolute directory path. Return a list of objects for each directory
    """
    given_absolute_path = path_info['given_absolute']
    parent_path = path_info['srcdocs_path']

    res = ()
    for asset in given_absolute_path.iterdir():
        rel_path = asset.relative_to(parent_path)
        nn = rel_path.with_suffix('')
        if asset.is_file():
            modified = asset.stat().st_mtime
            res += ({
                    # The plain name of the file, without the extension
                    'name': str(nn.as_posix()),
                    # rel_name is used within the iterface, as the slug
                    # and guessing pattern for associations.
                    'rel_name': str(rel_path.with_suffix('').as_posix()),
                    # The rel_path is the filepath of this file, relative within
                    # the polypoint src dir.
                    'rel_path': str(rel_path.as_posix()),
                    'is_dir': False,
                    'is_file': True,
                    'modified': modified,
                },)
        else:
            # modified = asset.stat().st_mtime
            res += ({
                    'name': str(nn.as_posix()),
                    'rel_name': str(rel_path.as_posix()),
                    'rel_path': str(rel_path.as_posix()),
                    'is_dir': True,
                    'is_file': False,
                    'modified': -1,
                },)
    return res


class PathBaseListView(views.ListView):
    """Present a file

        localhost:8000/trimdocs/path/readme.md/?frame=base&html_render=True
    """
    template_name = 'trimdocs/path_view.html'

    def get_queryset(self):
        """
        Return the list of items for this view.
        """
        p = self.get_path_info
        if p['given_absolute'].is_dir():
            # check for assets
            return get_directory_list(p)
        return []

    @cached_property
    def get_path_info(self):

        path = self.kwargs.get('path', '')
        return self.get_relative_path_info(path)

    def get_relative_path_info(self, path):
        # UI Safe but unhandled.
        given_path = Path(path) # .with_suffix('.js')

        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        # not UI safe, DATA safe
        given_absolute_path = srcdocs_path / given_path
        # This is UI safe
        given_relative_path = given_absolute_path.relative_to(srcdocs_path)

        return {
            'path': path,
            'given': given_path,
            'given_relative': given_relative_path,
            'given_relative_str': str(given_relative_path),
            'given_absolute': given_absolute_path,
            'given_absolute_str': str(given_absolute_path),
            'srcdocs_path': srcdocs_path,
        }

    def get_param_options(self):
        g = self.request.GET.copy()
        g.setdefault('frame', 'minimal')
        g.setdefault('html_render', 'true')
        return g

    def get_frame_name(self):
        opts = self.get_param_options()
        frame = opts.get('frame', 'base')
        return FRAME_MAP.get(frame)

    def get_html_render(self):
        opts = self.get_param_options()
        return len(opts.get('html_render', '')) > 0

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        p = self.get_path_info
        r['object_path_info'] = p
        r['object_path'] = p['path']
        r['html_render'] = self.get_html_render()
        r['is_rendered'] = self.get_html_render()
        # r['trimdocs_global_frame'] = "trimdocs/base.html"
        r['primary_include_filename'] = './source_demo_view.md'
        r['trimdocs_global_frame'] = self.get_frame_name()
        # r['trimdocs_global_frame'] = "trimdocs/base/null.html"
        r['object_content'] = self.get_object_content(p)
        return r

    def get_object_content(self, path_info):
        """Return the content of the object, (the markdown text)
        if this is a directory, the markdown content is the dir index
        page.
        """
        content = ''
        # pp(path_info)
        filepath = path_info['given_absolute']
        if filepath.exists() and filepath.is_file():
            # return text
            content = filepath.read_text(encoding='ISO-8859-1')
        # find and return file.

        return content


class PathView(PathBaseListView):

    def get(self, request, *args, **kwargs):
        """A few options exist here.

        + Render inline, returning the view of a subview
        + redirect: to target views, e.g DirView, CustomViewForPath

        This base view serves as a simple plain debug view.
        """
        # if path is blank: assume readme
        # if path == file
        # if path == dir: show dir page.
        ppath = self.get_path_info
        filepath = ppath['given_absolute']

        view_name = None

        if filepath.is_dir():
            print('is DIR')
            view_name = 'trimdocs:dir'

        if filepath.stem.lower() == 'readme':
            print('readme file')

        if view_name:
            resolve_match = resolve(reverse(view_name, args=args))
            view_class = resolve_match.func.view_class
            initkwargs = resolve_match.func.view_initkwargs
            view_class.view_initkwargs = initkwargs

            instance = view_class(**initkwargs)
            instance.setup(request, *args, **kwargs)
            return instance.get(request, *args, **kwargs)

        res = super().get(request, *args, **kwargs)
        return res


class PathDirView(PathBaseListView):
    template_name = 'trimdocs/dir_view.html'

    def get_directory_index_filename(self, **kwargs):
        """Find the first preferred file from a directory:
        """
        names = (
                "readme.md",
                "contents.md",
                "index.md",
                "_readme.md",
                "_index.md",
                "_contents.md",
            )
        # get this dir, for each.
        path_info = self.get_path_info
        loc = path_info['given_absolute']
        for name in names:
            p = loc / name
            if p.exists():
                return p

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        fn = self.get_directory_index_filename()
        if fn:
            r['index_filename_info'] = self.get_relative_path_info(fn)
        r['primary_include_filename'] = './dir_demo_view.md'
        return r
