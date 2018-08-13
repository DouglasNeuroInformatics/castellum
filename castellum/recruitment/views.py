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
import random

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelFormSet
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View

from extra_views import ModelFormSetView

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.studies.models import Study

from . import forms
from .models import AttributeSet
from .models import Participation
from .models import SubjectFilter
from .models import SubjectFilterGroup

monitoring_logger = logging.getLogger('monitoring.contact_data')


class PublishedStudyMixin:
    def dispatch(self, request, *args, **kwargs):
        study_pk = self.kwargs.get('study_pk')
        self.study = get_object_or_404(Study, pk=study_pk)
        if not self.study.published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class RecruitmentView(LoginRequiredMixin, PublishedStudyMixin, ListView):
    model = AttributeSet
    context_object_name = 'attributesets'
    template_name = 'recruitment/recruitment.html'

    def qs_sample(self, qs, k):
        all_ids = list(qs.values_list('id', flat=True))
        if len(all_ids) > k:
            picked_ids = random.sample(all_ids, k)
            return qs.filter(id__in=picked_ids)
        else:
            return qs

    def get_queryset(self, queryset=None):
        qs = AttributeSet.apply_study_filter(self.study, queryset=queryset)
        return self.qs_sample(qs, 6)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['study'] = self.study
        return context


class ContactView(LoginRequiredMixin, PublishedStudyMixin, UpdateView):
    model = Participation
    fields = ['status']
    template_name = 'recruitment/contact.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        self.attributeset = get_object_or_404(
            AttributeSet, pseudonym=self.kwargs['attributeset_slug'])

        contact_pseudonym = resolve_pseudonym(
            settings.DOMAINS['attributeset'],
            self.attributeset.pseudonym,
            settings.DOMAINS['contact'])
        self.contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        pseudonym = resolve_pseudonym(
            settings.DOMAINS['contact'], self.contact.pseudonym, self.study.domain)
        participation, __ = queryset.get_or_create(study=self.study, pseudonym=pseudonym)
        return participation

    def get_success_url(self):
        return reverse('recruitment:recruitment', args=[self.object.study.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        context['contact'] = self.contact
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_at = timezone.now()
        result = super(ContactView, self).form_valid(form)

        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        return result


class AttributeSetDetailView(LoginRequiredMixin, DetailView):
    model = AttributeSet

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        attributeset, __ = queryset.get_or_create(pseudonym=self.kwargs['slug'])
        return attributeset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['attributeset'], self.object.pseudonym, settings.DOMAINS['contact'])
        return context


class AttributeSetUpdateView(LoginRequiredMixin, UpdateView):
    model = AttributeSet
    fields = '__all__'
    slug_field = 'pseudonym'

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            settings.DOMAINS['attributeset'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class FilterListView(LoginRequiredMixin, ListView):
    model = SubjectFilterGroup

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(study=self.study)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        return data


class FilterCreateView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        group = SubjectFilterGroup.objects.create(study=study)
        return redirect(group.get_absolute_url())


class FilterDeleteView(LoginRequiredMixin, DeleteView):
    model = SubjectFilterGroup

    def get_context_data(self, **kwargs):
        study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        if study != self.object.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = study
        return data

    def get_success_url(self):
        return reverse('recruitment:filter_index', args=[self.object.study.pk])


class FilterFormSet(BaseModelFormSet):

    def clean(self):

        super().clean()

        values = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                values.append((
                    form.cleaned_data.get('field_name'),
                    form.cleaned_data.get('operator'),
                    form.cleaned_data.get('value'),
                ))

        if len(set(values)) != len(values):
            raise ValidationError(_('There are duplicates in filters. Please change or '
                                    'delete filter!'))


class FilterUpdateView(LoginRequiredMixin, ModelFormSetView):
    model = SubjectFilter
    form_class = forms.SubjectFilterForm
    formset_class = FilterFormSet
    factory_kwargs = {
        'can_delete': True,
    }
    template_name = "recruitment/filters.html"

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        self.group = get_object_or_404(SubjectFilterGroup, pk=self.kwargs['pk'])
        if self.study != self.group.study:
            raise Http404
        return super().dispatch(*args, **kwargs)

    def get_subject_count(self, group):
        return AttributeSet.objects.filter(group.to_q()).count()

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(group=self.group)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        data['group'] = self.group
        data['count'] = self.get_subject_count(self.group)
        data['total_count'] = AttributeSet.objects.count()
        return data
