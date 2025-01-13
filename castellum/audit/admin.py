# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from .models import AuditEvent


class AuditEventAdmin(admin.ModelAdmin):
    list_display = ['action', 'username', 'study_pk', 'subject_pk', 'created_at']
    list_filter = ['action', 'username', 'study_pk', 'subject_pk']
    date_hierarchy = 'created_at'


admin.site.register(AuditEvent, AuditEventAdmin)
