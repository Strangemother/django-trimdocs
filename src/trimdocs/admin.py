from django.contrib import admin
from trim import admin as t_admin

from . import models

@t_admin.register(models.PageModel)
class PageModelAdmin(admin.ModelAdmin):
    list_display = ('origin_path',)


t_admin.register_models(models, ignore=__name__)