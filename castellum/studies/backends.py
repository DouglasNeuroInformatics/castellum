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

from .models import Study
from .models import StudyGroup


class StudyPermissionBackend:
    def authenticate(self, request, **kwargs):
        return None

    def get_user(self, user_id):
        return None

    def _get_group_permissions(self, user, obj=None):
        if user.is_active and isinstance(obj, Study):
            perm_cache_name = '_study:{}_perm_cache'.format(obj.pk)
            if not hasattr(user, perm_cache_name):
                perms = set()
                groups = StudyGroup.objects.filter(study=obj, users=user)
                for group in groups:
                    perms.update(group.get_permissions())
                setattr(user, perm_cache_name, perms)
            return getattr(user, perm_cache_name)
        return set()

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
