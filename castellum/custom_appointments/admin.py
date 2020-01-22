from django.contrib import admin

from . import models

admin.site.register(models.Membership)
admin.site.register(models.Project)
