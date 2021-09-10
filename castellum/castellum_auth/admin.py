# (c) 2018-2021
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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import StudyGroup

from .forms import UserCreationAdminForm
from .models import User


def expiration_date_repr(obj):
    if not obj.expiration_date:
        return

    formatted_date = formats.date_format(
        timezone.localtime(obj.expiration_date), 'SHORT_DATE_FORMAT'
    )

    if obj.expiration_date < timezone.now():
        expire = _('expired')
    else:
        expires_in = obj.expiration_date - timezone.now()
        expire = _('{} days left').format(expires_in.days)

    return '{} ({})'.format(formatted_date, expire)


expiration_date_repr.admin_order_field = 'expiration_date'
expiration_date_repr.short_description = _('expiration date')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationAdminForm
    list_display = list(BaseUserAdmin.list_display) + [expiration_date_repr]
    actions = ['list_permissions']
    fieldsets = [
        (None, {
            'fields': ['username', 'token', 'password']
        }),
        (_('personal info'), {
            'fields': ['first_name', 'last_name', 'email', 'language']
        }),
        (_('permissions'), {
            'fields': [
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
                'general_domains',
            ]
        }),
        (_('important dates'), {
            'fields': ['last_login', 'date_joined', 'expiration_date', 'logout_timeout']
        }),
    ]

    def list_permissions(self, request, queryset):
        return render(request, 'admin/castellum_auth/user_permissions.html', {
            'opts': User._meta,
            'title': _('Permission list'),
            'users': queryset.all(),
            'groups': Group.objects.all(),
            'studygroups': StudyGroup.objects.all(),
        })
    list_permissions.short_description = _('List all permissions')
