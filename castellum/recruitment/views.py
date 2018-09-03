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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
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
from castellum.contacts.views import ContactUpdateView as _ContactUpdateView
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.studies.models import Study

from . import forms
from .models import AttributeSet
from .models import ParticipationRequest
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


class UnpublishedStudyMixin:
    def dispatch(self, request, *args, **kwargs):
        study_pk = self.kwargs.get('study_pk')
        self.study = get_object_or_404(Study, pk=study_pk)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.study.published:
            raise PermissionDenied
        return super().post(request, *args, **kwargs)


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class RecruitmentView(LoginRequiredMixin, PublishedStudyMixin, ListView):
    model = ParticipationRequest
    context_object_name = 'participation_requests'
    template_name = 'recruitment/recruitment.html'

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter_not_contacted(study=self.study)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        queryset = ParticipationRequest.objects.filter(study=self.study)

        participation_contact_list = []
        for participation in queryset:
            contact_pseudonym = resolve_pseudonym(
                self.study.domain,
                participation.pseudonym,
                settings.DOMAINS['contact'])
            contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)
            participation_contact_list.append((participation, contact))

        context['participation_contact_list'] = participation_contact_list
        context['all_count'] = queryset.count()
        context['invited_count'] = queryset.filter(
            status=ParticipationRequest.INVITED).count()
        context['not_reached_count'] = queryset.filter(
            status=ParticipationRequest.NOT_REACHED).count()
        context['unsuitable_count'] = queryset.filter(
            status=ParticipationRequest.UNSUITABLE).count()
        context['study'] = self.study
        return context

    def pick_random(self, qs):
        random_index = random.randint(0, qs.count() - 1)
        return qs.all()[random_index]

    def post(self, request, *args, **kwargs):
        attributeset = self.pick_random(AttributeSet.apply_study_filter(self.study))
        participation_request_pseudonym = resolve_pseudonym(
            settings.DOMAINS['attributeset'],
            attributeset.pseudonym,
            self.study.domain)
        __, created = ParticipationRequest.objects.get_or_create(
            study=self.study, pseudonym=participation_request_pseudonym)
        if not created:
            messages.error(request, _(
                'Picked person already participates in the study. You can '
                'just try again. But this might indicate that there are not '
                'many matches left.'))
        return self.get(request, *args, **kwargs)


class ContactView(LoginRequiredMixin, PublishedStudyMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact.html'

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(ParticipationRequest.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        contact_pseudonym = resolve_pseudonym(
            self.study.domain,
            self.object.pseudonym,
            settings.DOMAINS['contact'])
        contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        context['study'] = self.study
        context['contact'] = contact
        return context

    def form_valid(self, form):
        qs = ParticipationRequest.objects.filter_not_contacted(study=self.study)
        pseudonyms = list(qs.values_list("pseudonym", flat=True))
        current_pseudonym_idx = pseudonyms.index(self.object.pseudonym)

        self.object.updated_at = timezone.now()
        self.object.save()

        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        if "btn_back" in form.data or 0 == len(pseudonyms) - 1:
            url = reverse('recruitment:recruitment', args=[self.object.study.pk])
        else:
            next_pseudonym_idx = (current_pseudonym_idx + 1
                                  if current_pseudonym_idx + 1 < len(pseudonyms) else
                                  current_pseudonym_idx - 1)
            url = reverse('recruitment:contact', args=[self.object.study.pk,
                                                       pseudonyms[next_pseudonym_idx]])
        return redirect(url)


class ContactUpdateView(PublishedStudyMixin, _ContactUpdateView):
    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pseudonym=self.kwargs['slug'])

        contact_pseudonym = resolve_pseudonym(
            self.study.domain,
            participation_request.pseudonym,
            settings.DOMAINS['contact'])
        contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        return contact

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['slug']])

    def get_cancel_url(self):
        return self.get_success_url()


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
        data['total_count'] = AttributeSet.objects.count()
        return data


class FilterCreateView(LoginRequiredMixin, UnpublishedStudyMixin, View):
    def post(self, *args, **kwargs):
        group = SubjectFilterGroup.objects.create(study=self.study)
        return redirect(group.get_absolute_url())


class FilterDeleteView(LoginRequiredMixin, UnpublishedStudyMixin, DeleteView):
    model = SubjectFilterGroup

    def get_context_data(self, **kwargs):
        if self.study != self.object.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        return data

    def get_success_url(self):
        return reverse('recruitment:filter_index', args=[self.study.pk])


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


class FilterUpdateView(LoginRequiredMixin, UnpublishedStudyMixin, ModelFormSetView):
    model = SubjectFilter
    form_class = forms.SubjectFilterForm
    formset_class = FilterFormSet
    factory_kwargs = {
        'can_delete': True,
    }
    template_name = "recruitment/filters.html"

    def dispatch(self, *args, **kwargs):
        self.group = get_object_or_404(SubjectFilterGroup, pk=self.kwargs['pk'])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(group=self.group)

    def get_context_data(self, **kwargs):
        if self.study != self.group.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        data['group'] = self.group
        data['total_count'] = AttributeSet.objects.count()
        return data


class FilterGroupDuplicateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        if study.published:
            raise PermissionDenied
        original = get_object_or_404(SubjectFilterGroup, study=study, pk=self.kwargs['pk'])
        clone = original.duplicate()
        messages.success(request, _(
            'The filters have been duplicated. You can now edit the duplicate.'))
        return redirect('recruitment:filter_update', study.pk, clone.pk)
