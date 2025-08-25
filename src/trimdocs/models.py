from pathlib import Path

from django.db import models
from trim.models import fields

class Project(models.Model):
    """A Project captures the srcdocs and destdocs and allows the
    aggregation of assets under one unit.
    """
    src_dir = fields.text(help_text="the target source directory", null=False, primary_key=True)
    run_dir = fields.text(help_text="the base directory of the execute path")
    dest_dir = fields.text(help_text='the target destination directory')
    readme_filepath = fields.text(help_text="the path of the optional readme")


class PageModel(models.Model):
    origin_path = fields.text(null=False, primary_key=True)
    origin_path_parent = fields.text()
    project = fields.fk(Project)

    @property
    def name(self):
        return self.as_path().name

    def as_path(self, full=False):
        if full:
            return Path(self.project.src_dir) / Path(self.origin_path)
        return Path(self.origin_path)
