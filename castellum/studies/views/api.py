# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import JsonResponse
from django.views.generic import View

from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin

from ..mixins import StudyMixin
from ..models import Study


class APIStudyListView(APIAuthMixin, View):
    def get_queryset(self):
        qs = Study.objects.all()
        if self.request.GET.get('status') in ['edit', 'draft']:
            qs = qs.filter(status=Study.DRAFT)
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
