# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from django.http import JsonResponse
from django.views.generic import View

from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin

from ..mixins import StudyMixin
from ..models import Study


class APIStudyListView(APIAuthMixin, View):
    def get_queryset(self):
        qs = Study.objects.all()
        if self.request.GET.get('status') == 'edit':
            qs = qs.filter(status=Study.EDIT)
        elif self.request.GET.get('status') == 'execution':
            qs = qs.filter(status=Study.EXECUTION)
        elif self.request.GET.get('status') == 'finished':
            qs = qs.filter(status=Study.FINISHED)
        return qs

    def get(self, request, **kwargs):
        pks = self.get_queryset().values_list('pk', flat=True)
        return JsonResponse({'studies': list(pks)})


class APIStudyDetailView(APIAuthMixin, StudyMixin, PermissionRequiredMixin, View):
    permission_required = ['studies.view_study']

    def get(self, request, **kwargs):
        return JsonResponse(self.study.export())
