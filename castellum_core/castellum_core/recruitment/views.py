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
from django.views.generic import ListView, DetailView
from studies.models import Study
from subject_management.models import Subject


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    queryset = Study.objects.all()
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class SubjectChoiceView(LoginRequiredMixin, ListView):
    model = Subject
    paginate_by = 5
    queryset = Subject.objects.all()
    context_object_name = 'subjects'
    template_name = 'recruitment/subjects_list.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        study = Study.objects.filter(id=self.kwargs['study_id']).first()
        if study:
            context['study'] = study
            context['study_id'] = self.kwargs['study_id']
        return context


class SubjectDetailsView(LoginRequiredMixin, DetailView):
    model = Subject
    slug_field = 'id'
    slug_url_kwarg = 'subject_id'
    template_name = 'recruitment/subject_detail_view.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['study_id'] = self.kwargs['study_id']
        return context
