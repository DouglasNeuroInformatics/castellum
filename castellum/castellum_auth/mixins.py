# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import user_login_failed
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from castellum.utils.views import LoginNotRequiredMixin

from .models import User


class PermissionRequiredMixin(auth_mixins.PermissionRequiredMixin):
    def get_permission_object(self):
        return None

    def has_permission(self):
        perms = self.get_permission_required()
        permission_object = self.get_permission_object()
        return self.request.user.has_perms(perms, obj=permission_object)

    def check_auth_conditions(self):
        """Hook to add additional conditions."""
        return self.has_permission()

    def dispatch(self, request, *args, **kwargs):
        if not self.check_auth_conditions():
            return self.handle_no_permission()
        # skip auth_mixins.PermissionRequiredMixin
        return super(auth_mixins.PermissionRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )


class APIAuthMixin(LoginNotRequiredMixin):
    """Authenticate with token header instead of login.

    This should be the first mixin so that authentication is checked
    before anything else.
    """

    raise_exception = True

    def get_token(self):
        auth = self.request.headers.get('Authorization', '').split()
        if len(auth) != 2 or auth[0].lower() not in ['token', 'bearer']:
            raise PermissionDenied
        return auth[1]

    def authenticate(self):
        try:
            user = User.objects.get(token=self.get_token(), is_active=True)
        except User.DoesNotExist as e:
            raise PermissionDenied from e

        if not user.expiration_date:
            raise PermissionDenied('Account is not activated.')
        elif user.expiration_date < timezone.now():
            raise PermissionDenied('Account is expired.')

        return user

    def dispatch(self, request, *args, **kwargs):
        try:
            self.request.user = self.authenticate()
        except PermissionDenied:
            user_login_failed.send(sender=__name__, credentials={}, request=request)
            raise
        return super().dispatch(request, *args, **kwargs)


class ParamAuthMixin(APIAuthMixin):
    def get_token(self):
        if 'token' not in self.request.GET:
            raise PermissionDenied
        return self.request.GET['token']
