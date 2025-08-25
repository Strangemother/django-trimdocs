from pprint import pprint as pp
from pathlib import Path

from trim.models import live
from itertools import islice

def scrub():
    print(live.trimdocs.PageModel.objects.all().delete())


def gather_files(src_dir, discover_patterns, verbose=0):
    # src_dir = options['srcdocs']
    if verbose > 0:
        print('')
        print('running compilation of: ')
        print('    src_dir:', src_dir.absolute())
        print('    exists: ', src_dir.absolute().exists())
    # For now, create the destination directory and copy .md files verbatim
    count = 0
    """For every file in the srcdocs, create the sibling in the destination.
    Functionality this is a copy/paste - but through a markdown renderer view.

    For each file, call to the path view renderer, render the text and write
    it to the destination.

    However, writing needs to be cached, so we can perform any
    cross-referencing later. This may be memory intensive, so a flag for
    _write now_ should be appliable.
    """

    print('')

    # discover_patterns = settings.DISCOVER_PATTERNS

    keep = ()
    skips = ()
    for pattern in discover_patterns:
        for src_file in src_dir.rglob(pattern):
            count += 1
            name = src_file.name
            # And excludes?
            rel = src_file.absolute()#.relative_to(src_dir)
            # rel2 = src_file.absolute().relative_to(src_dir.absolute())
            # print(rel2, rel)
            if any(x.name.startswith('_') for x in rel.parents):
                if verbose > 0:
                    print('x Skip', rel)
                skips += (rel,)
                continue
            keep += (rel, )
            prefix = '  '
            if name == 'readme.md':
                prefix = ' *'

            if verbose > 1:
                print(f"{prefix}{rel}")


    # Test each folder to ensure a _readme_.
    # Insert specials.
    keep += (Path(src_dir) / '_indicies.md',)

    if verbose > 1:
        print('')
    if verbose > 0:
        print('\n')


    return keep, skips, count


def populate(files, src_dir):
    batch_size = 500
    print('Populate.')
    PageModel = live.trimdocs.PageModel
    project = live.trimdocs.Project.objects.get(src_dir=src_dir)
    objs = ()
    pp(files)
    for n in set(files):
        origin_path = n.relative_to(src_dir)
        m = PageModel(project=project,
                    origin_path=origin_path.as_posix(),
                    origin_path_parent=origin_path.parent.as_posix(),
                    )
        objs += (m,)

    PageModel.objects.bulk_create(objs)
    # while True:
    #     batch = tuple(islice(objs, batch_size))
    #     if not batch:
    #         break
    #     print('Writing', len(batch))
    #     PageModel.objects.bulk_create(batch, batch_size)


