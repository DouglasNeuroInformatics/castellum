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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .forms import UserCreationAdminForm
from .models import User


def expiration_date_repr(obj):
    if not obj.expiration_date:
        return

    expiration_date = obj.expiration_date.date()
    formatted_expiration_date = _("%(month)s/%(day)s/%(year)s") % {
        "month": expiration_date.month,
        "day": expiration_date.day,
        "year": expiration_date.year,
    }

    if obj.expiration_date < timezone.now():
        return "{} ({})".format(formatted_expiration_date, _("expired"))

    expires_in = obj.expiration_date - timezone.now()
    formatted_expires_in = _("%(days)s days left") % {"days": expires_in.days}
    return "{} ({})".format(formatted_expiration_date, formatted_expires_in)


expiration_date_repr.admin_order_field = 'expiration_date'
expiration_date_repr.short_description = _('expiration date')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationAdminForm
    list_display = BaseUserAdmin.list_display + (expiration_date_repr,)
    actions = ['list_permissions']
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'language')
        }),
        (_('permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('important dates'), {
            'fields': ('last_login', 'date_joined', 'expiration_date', 'logout_timeout')
        }),
    )

    def list_permissions(self, request, queryset):
        return render(request, 'admin/castellum_auth/user_permissions.html', {
            'opts': User._meta,
            'title': _('Permission list'),
            'users': queryset.all(),
            'groups': Group.objects.all(),
        })
    list_permissions.short_description = _('List all permissions')
