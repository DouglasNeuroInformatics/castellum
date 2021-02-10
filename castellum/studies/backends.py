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

from django.contrib.auth.backends import BaseBackend

from .models import Study
from .models import StudyMembership


class StudyPermissionBackend(BaseBackend):
    def _permissions_to_strings(self, qs):
        tuples = qs.values_list('content_type__app_label', 'codename')
        return (f'{app_label}.{name}' for app_label, name in tuples)

    def _get_group_permissions(self, user, obj=None):
        if user.is_active and isinstance(obj, Study):
            perm_cache_name = f'_study:{obj.pk}_perm_cache'
            if not hasattr(user, perm_cache_name):
                perms = set()
                membership = StudyMembership.objects.filter(user=user, study=obj).first()
                if membership:
                    perms.add('studies.access_study')
                    for group in membership.groups.all():
                        permissions = group.permissions.all()
                        perms.update(self._permissions_to_strings(permissions))
                setattr(user, perm_cache_name, perms)
            return getattr(user, perm_cache_name)
        return set()

    def get_all_permissions(self, user, obj=None):
        perms = set()
        if obj:
            perms.update(user.get_all_permissions())
        perms.update(self._get_group_permissions(user, obj=obj))
        return perms
