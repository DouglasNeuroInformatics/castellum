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
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic import UpdateView

from studies.models import Study
from subject_management.models import Subject

from .models import Participation


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class SubjectChoiceView(LoginRequiredMixin, ListView):
    model = Subject
    paginate_by = 5
    context_object_name = 'subjects'
    template_name = 'recruitment/subjects_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('first_name')

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        context['study'] = study
        return context


class ContactView(LoginRequiredMixin, UpdateView):
    model = Participation
    fields = ['status']
    template_name = 'recruitment/contact.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        subject_pk = self.kwargs['subject_pk']

        participation, __ = queryset.get_or_create(study=study, subject_pk=subject_pk)
        return participation

    def get_success_url(self):
        return reverse('recruitment:select_subject', args=[self.object.study.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.object.study
        context['subject'] = get_object_or_404(Subject, pk=self.object.subject_pk)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_at = timezone.now()
        return super(ContactView, self).form_valid(form)
