# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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
from parler.admin import TranslatableTabularInline

from .models import AttributeCategory
from .models import AttributeChoice
from .models import AttributeDescription
from .models import ExecutionTag
from .models import MailBatch
from .models import NewsMailBatch
from .models import Participation
from .models import ReliabilityEntry
from .models import SubjectFilter
from .models import SubjectFilterGroup


class AttributeChoiceInline(TranslatableTabularInline):
    model = AttributeChoice


class AttributeDescriptionAdmin(TranslatableAdmin):
    inlines = [
        AttributeChoiceInline,
    ]


admin.site.register(AttributeCategory, TranslatableAdmin)
admin.site.register(AttributeDescription, AttributeDescriptionAdmin)

if settings.CASTELLUM_ADVANCED_ADMIN_UI:
    admin.site.register(ReliabilityEntry)
    admin.site.register(MailBatch)
    admin.site.register(NewsMailBatch)
    admin.site.register(Participation)
    admin.site.register(SubjectFilter)
    admin.site.register(SubjectFilterGroup)
    admin.site.register(ExecutionTag)
