from pathlib import Path
from pprint import pprint as pp

from django.shortcuts import redirect
from django.conf import settings
from django.utils.functional import cached_property
from django.urls import resolve, reverse
from django.http import Http404


from django.core import management

try:
    import markdown as markdown_orig
except ImportError:
    markdown_orig = None

from trim import views

from . import nulldown
from . import models
from . import forms

from trim.response import content_type_response, content_data_response



FRAME_MAP = {
    'minimal': "trimdocs/base/minimal.html",
    'base': "trimdocs/base/base.html",
    'null': "trimdocs/base/null.html"
}

MARKDOWN_EXTENSIONS=[
    'meta',
    # 'extra',
    'toc',
    'pymdownx.details',
    "pymdownx.extra",
]

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


class Paren:
    """The Parens is latin for Parent. This Parens Path object allows the
    inspection of a Path (only ever) in relative to the parent.

    This ensures a path is landlocked to a source, and we can derive relative
    paths with ease.
    """
    def __init__(self, root_path, child_path=''):
        self.root_path = Path(root_path)
        self.child_path = Path(child_path)

    def get_resolved(self):
        return (self.root_path / self.child_path).resolve()

    def exists(self):
        return self.path.exists()

    @property
    def abs(self):
        """Return the absolute path of the root and child.
        """
        return self.get_resolved().absolute()

    @property
    def rel(self):
        return self.get_resolved().relative_to(self.root_path)

    @property
    def path(self):
        return self.get_resolved()

    @property
    def src(self):
        return self.root_path.resolve()


class FrameMixin:
    def get_frame_name(self):
        """REturn the name of the page frame from the GET or default options.
        """
        opts = self.get_param_options()
        frame = opts.get('frame', 'base')
        return FRAME_MAP.get(frame)

    def get_html_render(self):
        """Return a bool if the html render is flagged.
        True will render the content as html
        False will present the markdown, but with the jinja tags replaced.
        """
        opts = self.get_param_options()
        return len(opts.get('html_render', '')) > 0

    def get_param_options(self):
        """Return a dict of _options_ for the view. They include the
        frame and _if should render_ HTML.
        """
        g = self.request.GET.copy()
        g.setdefault('frame', 'minimal')
        g.setdefault('html_render', 'true')
        if hasattr(self, 'view_initkwargs'):
            g.update(self.view_initkwargs)
        return g


class PathBaseListView(views.ListView, FrameMixin):
    """A Base for listing a _Path_ as a directory.

        localhost:8000/trimdocs/path/readme.md/?frame=base&html_render=True

    Importantly, the queryset isn't models (yet)

    """
    template_name = 'trimdocs/path_view.html'
    inner_markdown_template = './source_demo_view.md'

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


    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        p = self.get_path_info
        r['object_path_info'] = p

        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        path = self.kwargs.get('path', '')
        r['parenpath'] = Paren(srcdocs_path, path)

        r['object_path'] = p['path']
        r['html_render'] = self.get_html_render()
        r['is_rendered'] = self.get_html_render()
        # r['trimdocs_global_frame'] = "trimdocs/base.html"
        r['primary_include_filename'] = self.inner_markdown_template
        r['trimdocs_global_frame'] = self.get_frame_name()
        # r['trimdocs_global_frame'] = "trimdocs/base/null.html"
        r['asset_cache'] = {'asset_stash': []}
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
    """The primary entry for browser based viewing of files

        /path/foo/bar/baz.md

    This acts as a (hidden) redirect to prepared views.
    For example if the given path is a directory or _special file_, serve their
    response.
    Default to the natural request, serving a placeholder file.

    This is the same view used for `compile`.
    """
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
        view_name = self.get_view_name(filepath)

        if view_name:
            return self.subview_get(view_name, request, *args, **kwargs)

        res = super().get(request, *args, **kwargs)
        return res


    def get_markdown_object(self):
        # context['view']

        # meta into the context.
        # HTML is the raw
        # https://python-markdown.github.io/extensions/
        md = markdown_orig.Markdown(extensions=MARKDOWN_EXTENSIONS)
        return md

    def subview_get(self, view_name, request, *args, **kwargs):
        """Given a view name and the original request parameters,
        return the get() response of the _other_ class.

        This overrides the original rendering to present this inner view.
        Fundamentally like a redirect, but with a shadowed URL.
        """

        resolve_match = resolve(reverse(view_name, args=args, kwargs=kwargs))
        view_class = resolve_match.func.view_class
        initkwargs = resolve_match.func.view_initkwargs
        view_class.view_initkwargs = initkwargs
        # view_class.view_initkwargs.update(self.kwargs)
        instance = view_class(**initkwargs)
        kw = kwargs.copy()
        kw.update(self.kwargs)
        instance.setup(request, *args, **kw)

        res = instance.get(request, *args, **kw)

        return res

    def get_view_name(self, filepath):
        """Return the target viewname to render.
        If None is returned, the default view (this one) is rendered.
        """
        view_name = None
        if filepath.is_dir():
            print('is DIR')
            view_name = 'trimdocs:dir'
        else:
            view_name = 'trimdocs:detail'

        stem = filepath.stem.lower()

        if stem == 'readme':
            print('readme file')
        if stem == '_indicies':
            # print('indicies file')
            view_name = 'trimdocs:indicies'
        if stem == '_contents':
            # print('contents file')
            view_name = 'trimdocs:contents'

        return view_name


class PageModel404View(views.TemplateView, FrameMixin):
    template_name = 'trimdocs/path_view.html'
    inner_markdown_template = './pagemodel_404.md'

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        # p = self.get_path_info
        # r['object_path_info'] = p

        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        path = self.kwargs.get('path', '')
        r['parenpath'] = Paren(srcdocs_path, path)

        # r['object_path'] = p['path']
        r['html_render'] = self.get_html_render()
        r['is_rendered'] = self.get_html_render()
        # r['trimdocs_global_frame'] = "trimdocs/base/base.html"
        r['primary_include_filename'] = self.inner_markdown_template
        r['trimdocs_global_frame'] = self.get_frame_name()
        return r


import re
from pathlib import Path

def parse_attrs_and_clean(s: str, keys=("width", "height")):
    """
        # Example
        s = "foo/bar/baz/large-logo-width-400-height-auto.png"
        attrs, clean = parse_attrs_and_clean(s)

        print(attrs)
        # {'width': 400, 'height': 'auto'}

        print(clean)
        # foo/bar/baz/large-logo.png
    """
    # Extract attributes
    found = dict(re.findall(r"(\w+)-(auto|\d+)", s))
    result = {}
    for k in keys:
        v = found.get(k, "auto")
        result[k] = int(v) if v.isdigit() else v

    # Remove -key-value pairs
    clean_name = re.sub(r"-(%s)-(?:auto|\d+)" % "|".join(keys), "", s)
    max_size = 20_000
    clean_result = {}
    for k,v in result.items():
        clean_result[k] = max_size if v == 'auto' else v

    return clean_result, clean_name

from PIL import Image
import glob, os

from io import BytesIO

from io import BytesIO
from PIL import Image, ImageOps

def thumbnail_bytes(path, size=(128, 128), fmt="PNG"):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).copy()
        im.thumbnail(size, Image.Resampling.LANCZOS)
        if fmt.upper() in ("JPEG", "JPG") and im.mode != "RGB":
            im = im.convert("RGB")
        buf = BytesIO()
        im.save(buf, format=fmt.upper(), optimize=True)
        buf.seek(0)
        return buf#.getvalue()  # <- return BYTES


class AssetView(views.TemplateView, FrameMixin):

    def get_relative_path_info(self, path, srcdocs_path=None):
        # UI  Safe but unhandled.
        given_path = Path(path) # .with_suffix('.js')
        # srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        # not UI safe, DATA safe
        given_absolute_path = Path((srcdocs_path / given_path).as_posix())
        # This is UI safe
        given_relative_path = Path(Path(given_absolute_path).relative_to(srcdocs_path).as_posix())

        return {
            'path': path,
            'given': given_path,
            'given_relative': given_relative_path,
            'given_relative_str': str(given_relative_path.as_posix()),
            'given_absolute': given_absolute_path,
            'given_absolute_str': str(given_absolute_path.as_posix()),
            'srcdocs_path': srcdocs_path,
        }

    def is_image(self, path):
         return path.suffix in ['.png', '.jpeg', '.jpg']

    def get(self, request, *args, **kwargs):
        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        path = self.kwargs.get('path', '')
        return self.get_content_response(path, srcdocs_path)

    def get_content_response(self, path, srcdocs_path):
        pv = self.get_relative_path_info(path, srcdocs_path)
        ap = pv['given_absolute']
        # If image, do special asset name parse.
        print('\nassetview: static path: ', ap)
        attrs, clean = parse_attrs_and_clean(ap.as_posix())
        clean_path = Path(clean)
        if clean_path.exists() and self.is_image(clean_path):
            # do resize
            size = (attrs.get('width', 20_000), attrs.get('height', 20_000))
            data = thumbnail_bytes(clean_path, size=size, fmt="PNG")
            return content_data_response(data, clean_path.with_suffix(".png"))

            # buf = BytesIO()
            # with Image.open(clean_path) as im:
            #     im.thumbnail(size)
            #     file = clean_path.parent / (clean_path).name
            #     # im.save(buf, format="png")
            #     im.save(buf, 'PNG')
            #     buf.seek(0)
            #     # return content_type_response(ap)
                # return content_data_response(buf, clean_path.name)


class PageModelDetailView(views.DetailView, FrameMixin):
    pk_url_kwarg = 'path'
    slug_field = 'origin_path'
    model = models.PageModel

    template_name = 'trimdocs/path_view.html'
    inner_markdown_template = './pagemodel_detail.md'

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        p = self.get_path_info
        r['object_path_info'] = p

        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        path = self.kwargs.get('path', '')
        r['parenpath'] = Paren(srcdocs_path, path)

        # r['object_path'] = p['path']
        r['html_render'] = self.get_html_render()
        r['is_rendered'] = self.get_html_render()

        # r['trimdocs_global_frame'] = "trimdocs/base.html"
        r['primary_include_filename'] = self.inner_markdown_template
        r['trimdocs_global_frame'] = self.get_frame_name()
        metadata, clean_content = self.get_markdown_metadata(r['object'])
        r['metadata'] = metadata
        r['clean_content'] = clean_content
        r['title'] = self.get_title(r)
        r['asset_cache'] = {'asset_stash': []}
        # r['trimdocs_global_frame'] = "trimdocs/base/null.html"
        # r['object_content'] = self.get_object_content(p)
        return r

    def get_title(self, context):
        """Return the title from the meta data or the filename.
        """
        titles = context['metadata'].get('title')
        if titles and len(titles) > 0:
            title = titles[0]
            return title

        if 'object' in context:
            obj = context['object']
            name = obj.name
        elif 'parenpath' in context:
            parenpath = context['parenpath']
            name = parenpath.rel.name

        return Path(name).stem.replace('-', ' ').title()

    def get_markdown_metadata(self, pagemodel):
        filepath = pagemodel.as_path(full=True)
        # meta into the context.
        # HTML is the raw
        # https://python-markdown.github.io/extensions/
        extensions=[
            'meta',
        ]
        # md = markdown_orig.Markdown(extensions=extensions)
        md = nulldown.ReducedMarkdown(extensions=extensions)
        content = filepath.read_text(encoding='ISO-8859-1')
        html = md.convert(content)
        metaless_content = '\n'.join(md.lines)
        return md.Meta, metaless_content


    def get_markdown_object(self):
        # context['view']

        # meta into the context.
        # HTML is the raw
        # https://python-markdown.github.io/extensions/
        md = markdown_orig.Markdown(extensions=MARKDOWN_EXTENSIONS)
        return md

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except (self.model.DoesNotExist, Http404):
            # If the file exists, then we can build this file
            # on the fly.

            srcdocs_path = settings.TRIMDOCS_SRC_DOCS
            path = self.kwargs.get('path', '')
            pv = self.get_relative_path_info(path, srcdocs_path)
            ap = pv['given_absolute']

            view_class = PageModel404View
            if self.is_image(ap) or ap.exists():
                view_class = AssetView
                # This is a file, but not a model.
                # For now, assume raw return..

            # resolve_match = resolve(reverse(view_name, args=args, kwargs=kwargs))
            # view_class = resolve_match.func.view_class
            # initkwargs = resolve_match.func.view_initkwargs
            # view_class.view_initkwargs = initkwargs
            kw = kwargs.copy()
            kw.update(self.kwargs)
            # view_class.view_initkwargs.update(kw)
            instance = view_class(**kw)
            instance.setup(request, *args, **kw)
            return instance.get(request, *args, **kw)

            # In response, we serve the other page.
            # raise Exception('GET Custom Error')

    def is_image(self, path):
         return path.suffix in ['.png', '.jpeg', '.jpg']

    @cached_property
    def get_path_info(self):
        path = self.kwargs.get('path', '')
        return self.get_relative_path_info(path)

    def get_relative_path_info(self, path, srcdocs_path=None):
        # UI  Safe but unhandled.
        given_path = Path(path) # .with_suffix('.js')

        srcdocs_path = srcdocs_path or models.PageModel.objects.get(pk=given_path.as_posix()).project.src_dir
        # srcdocs_path = settings.TRIMDOCS_SRC_DOCS

        # not UI safe, DATA safe
        given_absolute_path = Path((srcdocs_path / given_path).as_posix())
        # This is UI safe
        given_relative_path = Path(Path(given_absolute_path).relative_to(srcdocs_path).as_posix())

        return {
            'path': path,
            'given': given_path,
            'given_relative': given_relative_path,
            'given_relative_str': str(given_relative_path.as_posix()),
            'given_absolute': given_absolute_path,
            'given_absolute_str': str(given_absolute_path.as_posix()),
            'srcdocs_path': srcdocs_path,
        }

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


class PageModelListView(views.ListView, FrameMixin):
    model = models.PageModel
    inner_markdown_template = './pagemodel_list.md'

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        # p = self.get_path_info
        # r['object_path_info'] = p

        srcdocs_path = settings.TRIMDOCS_SRC_DOCS
        path = self.kwargs.get('path', '')
        r['parenpath'] = Paren(srcdocs_path, path)

        # r['object_path'] = p['path']
        r['html_render'] = self.get_html_render()
        r['is_rendered'] = self.get_html_render()
        # r['trimdocs_global_frame'] = "trimdocs/base.html"
        r['primary_include_filename'] = self.inner_markdown_template
        r['trimdocs_global_frame'] = self.get_frame_name()
        # r['trimdocs_global_frame'] = "trimdocs/base/null.html"
        # r['object_content'] = self.get_object_content(p)
        return r


class DirectoryFileMixin:
    special_names = (
            "readme",
            "contents",
            "indicies",
        )


    def get_markdown_object(self):
        # context['view']

        # meta into the context.
        # HTML is the raw
        # https://python-markdown.github.io/extensions/

        md = markdown_orig.Markdown(extensions=MARKDOWN_EXTENSIONS)
        return md

    def get_special_names(self):
        return self.special_names

    def get_directory_index_filename(self, **kwargs):
        """Find the first preferred file from a directory:
        """
        names = self.get_special_names()
        # names = (
        #         "readme.md",
        #         "contents.md",
        #         "indicies.md",
        #         "_readme.md",
        #         "_indicies.md",
        #         "_contents.md",
        #     )
        discover_patterns = settings.DIR_FILE_EXTENSIONS
        # get this dir, for each.
        path_info = self.get_path_info
        loc = path_info['given_absolute']
        for name in names:
            for ext in discover_patterns:
                p = (loc / name).with_suffix(ext)
                if p.exists():
                    return p
        # Seach for the name in underscore
        for name in names:
            for ext in discover_patterns:
                p = (loc / f"_{name}").with_suffix(ext)
                if p.exists():
                    return p



class PathDirView(PathBaseListView, DirectoryFileMixin):
    """A Directory view Lists its children, and has a primary
    file, one of the specials; hopefully a README.

    The object will be the current _directory_, where the `index_filename_info`
    is the index file.
    """
    template_name = 'trimdocs/dir_view.html'
    inner_markdown_template = './dir_demo_view.md'

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        fn = self.get_directory_index_filename()
        if fn:
            r['index_filename_info'] = self.get_relative_path_info(fn)
        r['primary_include_filename'] = self.inner_markdown_template
        return r


class IndiciesPathView(PathDirView, DirectoryFileMixin):
    """An _indicies presents all files below as a flat list of urls.

    This is a _special view_ served on `trimdocs:indices`
    """
    inner_markdown_template = './indicies_demo_view.md'
    special_names = (
            "indicies",
            )

    def get_context_data(self, **kwargs):
        r = super().get_context_data(**kwargs)
        fn = self.get_directory_index_filename()
        if fn:
            r['object'] = self.get_relative_path_info(fn)
        r['primary_include_filename'] = self.inner_markdown_template
        r['object_list'] = models.PageModel.objects.order_by('origin_path')
        return r


class ContentsPathView(PathDirView):
    """An `_contents` of any directory presents its children with titles and
    descriptions

    This is a _special view_ served on `trimdocs:contents`
    """
    inner_markdown_template = './contents_demo_view.md'
    special_names = (
            "contents",
            )


class InfoView(ContentsPathView):
    """Present special information about the docs.
    This render a default page or _info.md if it exists.
    """
    template_name = 'trimdocs/dir_view.html'
    inner_markdown_template = './info_demo_view.md'
    special_names = (
            "info",
            )


class CompileView(InfoView, views.FormView):
    """Run compile.
    """
    inner_markdown_template = './compile_demo_view.md'
    special_names = (
            "compile",
            )

    form_class = forms.CompileConfirmForm
    success_url = views.reverse_lazy('trimdocs:info')

    def form_valid(self, form):

        # from django.core import management
        # from django.core.management.commands import loaddata

        # py trimdocs_project\manage.py trimdocs compile ^
        #     --srcdocs demos\demo-srcdocs ^
        #     --destdocs demos\demo-destdocs %*

        # management.call_command("flush", verbosity=0, interactive=False)
        p = Path('./compile_output.txt')
        with p.open("w") as stream:
            management.call_command("trimdocs", "compile",
                "--srcdocs", "demos/demo-srcdocs",
                "--destdocs", "demos/demo-destdocs",
                stdout=stream,
                verbosity=1)
        # management.call_command(loaddata.Command(), "test_data", verbosity=0)
        # run compile command
        return super().form_valid(form)
