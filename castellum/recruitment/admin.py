# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
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

import json

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from .models import AttributeChoice
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest
from .models import ParticipationRequestRevision
from .models import SubjectFilter
from .models import SubjectFilterGroup


class AttributeChoiceInline(admin.TabularInline):
    model = AttributeChoice


class AttributeDescriptionAdmin(admin.ModelAdmin):
    inlines = [
        AttributeChoiceInline,
    ]
    actions = ['export_json']

    def export_json(self, request, queryset):
        response = HttpResponse(content_type="application/json")
        data = [description.export() for description in queryset.all()]
        json.dump(data, response)
        return response
    export_json.short_description = _('Export as JSON')


admin.site.register(AttributeDescription, AttributeDescriptionAdmin)
admin.site.register(AttributeSet)
admin.site.register(ParticipationRequest)
admin.site.register(ParticipationRequestRevision)
admin.site.register(SubjectFilter)
admin.site.register(SubjectFilterGroup)
