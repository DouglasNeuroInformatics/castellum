# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin

from castellum.utils.admin import NoCreateModelAdmin

from . import models


class SubjectAdmin(NoCreateModelAdmin):
    search_fields = ['uuid']


class ConsentDocumentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'is_valid', 'is_deprecated']
    list_filter = ['is_valid', 'is_deprecated']


admin.site.register(models.ConsentDocument, ConsentDocumentAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:
    admin.site.register(models.Subject, SubjectAdmin)
    admin.site.register(models.SubjectCreationRequest, NoCreateModelAdmin)
    admin.site.register(models.Consent)
    admin.site.register(models.ConsentRevision)
    admin.site.register(models.Report)
