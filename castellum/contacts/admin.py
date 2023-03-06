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

from django.contrib import admin

from castellum.utils.admin import NoCreateModelAdmin

from .models import Address
from .models import Contact
from .models import ContactCreationRequest
from .models import Street


class AddressInline(admin.StackedInline):
    model = Address


class ContactAdmin(admin.ModelAdmin):
    list_display = 'first_name', 'last_name', 'address', 'email', 'phone_number'
    list_display_links = 'first_name', 'last_name'
    list_per_page = 200
    search_fields = 'first_name', 'last_name'
    inlines = [AddressInline]

    fieldsets = [
        (None, {
            'fields': (
                ('first_name', 'last_name', 'title'),
                'gender',
                'date_of_birth',
            ),
        }),
        ('Contact Data', {
            'fields': (
                'email',
                ('phone_number', 'phone_number_alternative'),
                'legal_representatives',
            )
        }),
    ]

    def get_queryset(self, request):  # pragma: no cover
        return super().get_queryset(request).select_related('address')


admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactCreationRequest, NoCreateModelAdmin)
admin.site.register(Street)
