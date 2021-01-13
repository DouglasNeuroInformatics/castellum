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

from typing import List
from typing import Optional

from django.shortcuts import get_object_or_404

from .models import Study


class StudyMixin:
    """Use this on every view that belongs to a study.

    -   set ``self.study``
    -   check ``access_study`` permission (basically allow access only
        to study members)
    -   check that status is in ``study_status`` and matches
        ``is_onetime_invitation``, otherwise return 404
    -   use study as permission object

    Requires PermissionRequiredMixin.
    """

    study_status: List[int] = []
    is_onetime_invitation: Optional[bool] = None

    def get_study(self):
        qs = Study.objects.all()
        if self.study_status:
            qs = qs.filter(status__in=self.study_status)
        if self.is_onetime_invitation is not None:
            qs = qs.filter(is_onetime_invitation=self.is_onetime_invitation)
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
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        return context
