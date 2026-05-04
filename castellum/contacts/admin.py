# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin

from castellum.utils.admin import NoCreateModelAdmin

from .models import Address
from .models import BlockHash
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


if settings.CASTELLUM_ADVANCED_ADMIN_UI:  # pragma: no branch
    admin.site.register(BlockHash)
    admin.site.register(Contact, ContactAdmin)
    admin.site.register(ContactCreationRequest, NoCreateModelAdmin)
    admin.site.register(Street)
