# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
                membership = (
                    StudyMembership.objects
                    .filter(user=user, study=obj)
                    .first()
                )
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
