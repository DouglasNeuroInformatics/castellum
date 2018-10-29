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

from django.contrib.auth.models import Permission

from .models import Study
from .models import StudyPosition


class StudyPermissionBackend:
    def authenticate(self, request, **kwargs):
        return None

    def get_user(self, user_id):
        return None

    def _permissions_to_strings(self, qs):
        tuples = qs.values_list('content_type__app_label', 'codename')
        return ('{}.{}'.format(ct, name) for ct, name in tuples)

    def _get_group_permissions(self, user, obj=None):
        perms = set()
        if user.is_active and isinstance(obj, Study):
            positions = StudyPosition.objects.filter(user=user, study=obj)
            for position in positions:
                permissions = Permission.objects.filter(group=position.group)
                perms.update(self._permissions_to_strings(permissions))
        return perms

    def get_group_permissions(self, user, obj=None):
        perms = set()
        if obj:
            perms.update(user.get_group_permissions())
        perms.update(self._get_group_permissions(user, obj=obj))
        return perms

    def get_all_permissions(self, user, obj=None):
        perms = set()
        if obj:
            perms.update(user.get_all_permissions())
        perms.update(self._get_group_permissions(user, obj=obj))
        return perms

    def has_perm(self, user, perm, obj=None):
        perms = self.get_all_permissions(user, obj=obj)
        return perm in perms
