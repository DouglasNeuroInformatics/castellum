# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from .models import Attribute
from .models import AttributeCategory
from .models import AttributeChoice
from .models import ExecutionTag
from .models import MailBatch
from .models import NewsMailBatch
from .models import Participation
from .models import ParticipationConsent
from .models import ReliabilityEntry
from .models import SubjectFilter
from .models import SubjectFilterGroup


class AttributeChoiceInline(TranslatableTabularInline):
    model = AttributeChoice


class AttributeAdmin(TranslatableAdmin):
    inlines = [
        AttributeChoiceInline,
    ]


admin.site.register(AttributeCategory, TranslatableAdmin)
admin.site.register(Attribute, AttributeAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:
    admin.site.register(ReliabilityEntry)
    admin.site.register(MailBatch)
    admin.site.register(NewsMailBatch)
    admin.site.register(Participation)
    admin.site.register(ParticipationConsent)
    admin.site.register(SubjectFilter)
    admin.site.register(SubjectFilterGroup)
    admin.site.register(ExecutionTag)
