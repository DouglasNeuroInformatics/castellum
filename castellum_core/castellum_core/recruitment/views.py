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

import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from pseudonyms.helpers import resolve_pseudonym
from studies.models import Study
from subject_management.models import Subject

from .models import AttributeSet
from .models import Participation

monitoring_logger = logging.getLogger('monitoring.subject_data')


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

        self.study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        self.subject = get_object_or_404(Subject, pseudonym=self.kwargs['subject_slug'])

        pseudonym = resolve_pseudonym(
            settings.DOMAINS['contact'], self.subject.pseudonym, self.study.domain)
        participation, __ = queryset.get_or_create(study=self.study, pseudonym=pseudonym)
        return participation

    def get_success_url(self):
        return reverse('recruitment:select_subject', args=[self.object.study.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        context['subject'] = self.subject
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_at = timezone.now()
        result = super(ContactView, self).form_valid(form)

        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        return result


class AttributeSetDetailView(LoginRequiredMixin, DetailView):
    model = AttributeSet
    slug_field = 'pseudonym'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['attributeset'], self.object.pseudonym, settings.DOMAINS['contact'])
        return context


class AttributeSetCreateView(LoginRequiredMixin, CreateView):
    model = AttributeSet
    fields = '__all__'

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['attributeset'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class AttributeSetUpdateView(LoginRequiredMixin, UpdateView):
    model = AttributeSet
    fields = '__all__'
    slug_field = 'pseudonym'

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['attributeset'],
            self.object.pseudonym,
            self.request.user.pk))
        return result
