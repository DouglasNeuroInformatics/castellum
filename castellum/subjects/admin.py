# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.contrib import admin

from . import models


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['uuid']


class ConsentDocumentAdmin(admin.ModelAdmin):
    list_display = ['created_at']


admin.site.register(models.Subject, SubjectAdmin)
admin.site.register(models.SubjectCreationRequest)
admin.site.register(models.SubjectNote)
admin.site.register(models.Consent)
admin.site.register(models.ConsentDocument, ConsentDocumentAdmin)
