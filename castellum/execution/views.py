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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import SubjectMixin


class StudyListView(LoginRequiredMixin, ListView):
    template_name = 'execution/study_list.html'
    model = Study

    def get_queryset(self):
        qs = super().get_queryset()
        perms = ('recruitment.view_participation_pseudonyms', 'studies.access_study')
        return [study for study in qs.filter(study_mode=Study.EXECUTION) if (
            self.request.user.has_perms(perms, obj=study)
        )]


class StudyDetailView(StudyMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/study_detail.html'
    model = Study
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_modes = [Study.EXECUTION]

    def get_object(self):
        return self.study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list'] = []
        for pr in self.study.participationrequest_set.filter(status=ParticipationRequest.INVITED):
            has_access = self.request.user.has_privacy_level(pr.subject.privacy_level)
            context['list'].append((pr, has_access))

        return context


class ParticipationRequestDetailView(StudyMixin, SubjectMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/participationrequest_detail.html'
    model = ParticipationRequest
    permission_required = 'recruitment.view_participation_pseudonyms'
    study_modes = [Study.EXECUTION]

    def get_object(self):
        return get_object_or_404(
            ParticipationRequest,
            pk=self.kwargs['pk'],
            study=self.study,
            status=ParticipationRequest.INVITED,
        )
