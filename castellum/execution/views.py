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
from django.views.generic import DetailView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.mixins import StudyPermissionMixin
from castellum.studies.models import Study


class StudyListView(LoginRequiredMixin, ListView):
    template_name = 'execution/study_list.html'
    model = Study

    def get_queryset(self):
        qs = super().get_queryset()
        return [study for study in qs.filter(study_mode=Study.EXECUTION) if (
            self.request.user.has_perm('recruitment.view_participation_pseudonyms', obj=study) and
            self.request.user.has_perm('studies.access_study', obj=study)
        )]


class StudyDetailView(StudyPermissionMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/study_detail.html'
    model = Study
    permission_required = 'recruitment.view_participation_pseudonyms'

    def dispatch(self, request, *args, **kwargs):
        self.study = Study.get_by_pk_or_404(self.kwargs.get('study_pk'))
        self.study.raise_404_error_if_study_is_not_in_execution_mode()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list'] = []
        for pr in self.study.participationrequest_set.filter(status=ParticipationRequest.INVITED):
            has_access = self.request.user.has_privacy_level(pr.subject.privacy_level)
            context['list'].append((pr, has_access))

        return context
