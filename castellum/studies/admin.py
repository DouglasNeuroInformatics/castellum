# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

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
    search_fields = ['name"']
    ordering = ['name']
    filter_horizontal = ['permissions']


admin.site.register(models.Resource)
admin.site.register(models.StudyGroup, StudyGroupAdmin)
admin.site.register(models.StudyType, TranslatableAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:
    admin.site.register(models.Study, StudyAdmin)
    admin.site.register(models.StudyMembership)
