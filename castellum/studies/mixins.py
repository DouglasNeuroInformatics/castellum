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
from .models import StudyGroup


class StudyMixin:
    """Use this on every view that belongs to a study.

    -   set ``self.study``
    -   check ``access_study`` permission (basically allow access only to study members)
    -   check that study mode is in ``study_modes``, otherwise return 404
    -   use study as permission object

    Requires PermissionRequiredMixin.
    """

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
        permission_required = {'studies.access_study'}
        permission_required.update(super().get_permission_required())
        return permission_required

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        return data


class StudyGroupMixin(StudyMixin):
    def get_study(self):
        qs = StudyGroup.objects.all()
        if 'study_pk' in self.kwargs:
            qs = qs.filter(study_id=self.kwargs['study_pk'])
        if self.study_modes:
            qs = qs.filter(study__study_mode__in=self.study_modes)
        self.group = get_object_or_404(qs, pk=self.kwargs['group_pk'])
        return self.group.study

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['group'] = self.group
        return data
