# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin
from parler.admin import TranslatableAdmin

from . import models


class StudySessionInline(admin.TabularInline):
    model = models.StudySession


class StudyAdmin(admin.ModelAdmin):
    inlines = [StudySessionInline]
    search_fields = ['name']


class StudyGroupAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    filter_horizontal = ['permissions']


admin.site.register(models.Resource)
admin.site.register(models.StudyGroup, StudyGroupAdmin)
admin.site.register(models.StudyType, TranslatableAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:
    admin.site.register(models.Study, StudyAdmin)
    admin.site.register(models.StudyMembership)
