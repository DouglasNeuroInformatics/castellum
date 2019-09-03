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

from django.shortcuts import get_object_or_404

from .models import Study


class StudyMixin:
    study_modes = []

    def get_study(self):
        qs = Study.objects.all()
        if self.study_modes:
            qs = qs.filter(study_mode__in=self.study_modes)
        key = 'study_pk' if 'study_pk' in self.kwargs else 'pk'
        return get_object_or_404(qs, pk=self.kwargs.get(key))

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.study = self.get_study()

    def get_permission_object(self):
        return self.study

    def get_permission_required(self):
        """If used together with PermissionRequiredMixin, require access_study permission."""
        permission_required = {'studies.access_study'}
        permission_required.update(super().get_permission_required())
        return permission_required
