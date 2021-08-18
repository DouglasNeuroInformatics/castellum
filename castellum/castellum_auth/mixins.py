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

from django.contrib.auth import mixins as auth_mixins
from django.core.exceptions import PermissionDenied

from .models import User


class PermissionRequiredMixin(auth_mixins.PermissionRequiredMixin):
    def get_permission_object(self):
        return None

    def has_permission(self):
        perms = self.get_permission_required()
        permission_object = self.get_permission_object()
        return self.request.user.has_perms(perms, obj=permission_object)


class APIAuthMixin:
    """Similar to PermissionRequiredMixin.

    Differences:
    -   Does not redirect to login on error
    -   Gets request.user from the HTTP_AUTHORIZATION header
    """
    permission_required = None

    def handle_no_permission(self):
        raise PermissionDenied

    def get_permission_required(self):
        return self.permission_required

    def get_permission_object(self):
        return None

    def has_permission(self):
        perms = self.get_permission_required()
        permission_object = self.get_permission_object()
        return self.request.user.has_perms(perms, obj=permission_object)

    def authenticate(self):
        auth = self.request.headers.get('Authorization', '').split()
        if len(auth) != 2 or auth[0].lower() != 'token':
            self.handle_no_permission()
        try:
            return User.objects.get(token=auth[1])
        except User.DoesNotExist:
            self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        self.request.user = self.authenticate()
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
