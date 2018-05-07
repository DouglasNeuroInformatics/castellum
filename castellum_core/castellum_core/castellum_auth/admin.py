from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import User


def expires_in(obj):
    if obj.expiration_date is None or obj.expiration_date < timezone.now():
        return None
    else:
        return obj.expiration_date - timezone.now()


expires_in.admin_order_field = 'expiration_date'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + (expires_in,)
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'expiration_date')
        }),
    )
