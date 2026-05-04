# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin

from . import models


class DomainAdmin(admin.ModelAdmin):
    readonly_fields = ['key']
    search_fields = ['name', 'key']
    list_filter = [('content_type', admin.RelatedOnlyFieldListFilter)]
    filter_horizontal = ['managers', 'exportable_attributes']


admin.site.register(models.Domain, DomainAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:  # pragma: no branch
    admin.site.register(models.Pseudonym)
