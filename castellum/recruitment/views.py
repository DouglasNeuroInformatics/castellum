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
from castellum.settings import CASTELLUM_MULTIPLE_FACTOR
from castellum.settings import CASTELLUM_WARNING_NUMBER_IN_CONTACT_LIST
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

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        participants = []
        for participation in self.get_queryset():
            contact_pseudonym = resolve_pseudonym(
                self.study.domain,
                participation.pseudonym,
                settings.DOMAINS['contact'])
            contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)
            participants.append((participation, contact))
        context['participants'] = participants

        queryset = ParticipationRequest.objects.filter(study=self.study)
        context['all_count'] = queryset.count()
        context['invited_count'] = queryset.filter(
            status=ParticipationRequest.INVITED).count()
        context['unsuitable_count'] = queryset.filter(
            status=ParticipationRequest.UNSUITABLE).count()
        context['not_reached_count'] = queryset.filter(
            status=ParticipationRequest.NOT_REACHED).count()
        context['not_contacted_count'] = queryset.filter(
            status=ParticipationRequest.NOT_CONTACTED).count()
        context['study'] = self.study
        return context


class RecruitmentViewNotReached(RecruitmentView):

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter_not_reached(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['not_reached_view'] = True
        return context


class RecruitmentViewNotContacted(RecruitmentView):

    def pick_random(self, qs):
        if qs.count() != 0:
            random_index = random.randint(0, qs.count() - 1)
            return qs.all()[random_index]
        else:
            return None

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter_not_contacted(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['not_contacted_view'] = True
        return context

    def post(self, request, *args, **kwargs):

        if self.study.min_subjects_count:

            number_of_not_contacted = self.get_queryset().count()
            if number_of_not_contacted >= self.study.min_subjects_count*CASTELLUM_MULTIPLE_FACTOR:
                messages.error(request, _(
                    'Application privacy does not allow you to add more subjects. '
                    'Please contact provided subjects before adding new ones.'
                    ))
            else:
                if number_of_not_contacted >= CASTELLUM_WARNING_NUMBER_IN_CONTACT_LIST:
                    messages.error(request, _(
                        'Such workflow is not intended due to privacy reasons. '
                        'Please contact provided subjects before adding new ones.'
                    ))
                attributeset = self.pick_random(AttributeSet.apply_study_filter(self.study))
                if attributeset:
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
        else:
            messages.error(request, _(
                'The minimal number of subjects is not set for this study. '
                'Please, contact the responsible person who can set it up.'))

        return self.get(request, *args, **kwargs)


class ContactView(LoginRequiredMixin, PublishedStudyMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact.html'

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects

        if self.kwargs['path'] == 'not-contacted':
            return queryset.filter_not_contacted(study=self.study)
        elif self.kwargs['path'] == 'not-reached':
            return queryset.filter_not_reached(study=self.study)
        else:
            raise Http404

        return queryset

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

        if self.kwargs['path'] == 'not-contacted':
            context['not_contacted_view'] = True
        elif self.kwargs['path'] == 'not-reached':
            context['not_reached_view'] = True
        else:
            raise Http404

        context['study'] = self.study
        context['contact'] = contact
        return context

    def form_valid(self, form):
        # needs to be executed before object.save()
        pseudonyms = list(self.get_queryset().values_list("pseudonym", flat=True))

        self.object.updated_at = timezone.now()
        self.object.save()

        monitoring_logger.info('ParticipationRequest update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        next_pseudonym_idx = None
        if "btn_back" not in form.data and len(pseudonyms) - 1 != 0:
            current_pseudonym_idx = pseudonyms.index(self.object.pseudonym)
            if current_pseudonym_idx + 1 < len(pseudonyms):
                next_pseudonym_idx = current_pseudonym_idx + 1
            elif self.kwargs['path'] == 'not-contacted':
                next_pseudonym_idx = current_pseudonym_idx - 1

        if next_pseudonym_idx is None:
            url = 'recruitment:recruitment_' + self.kwargs['path']
            return redirect(url, self.object.study.pk)
        else:
            return redirect(
                'recruitment:contact',
                self.object.study.pk,
                pseudonyms[next_pseudonym_idx],
                self.kwargs['path'])


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
        return reverse('recruitment:contact',
                       args=[self.kwargs['study_pk'], self.kwargs['slug'], self.kwargs['path']])

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


class FilterGroupListView(LoginRequiredMixin, ListView):
    model = SubjectFilterGroup
    template_name = 'recruitment/filtergroup_list.html'

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


class FilterGroupCreateView(LoginRequiredMixin, UnpublishedStudyMixin, View):
    def post(self, *args, **kwargs):
        group = SubjectFilterGroup.objects.create(study=self.study)
        return redirect(group.get_absolute_url())


class FilterGroupDeleteView(LoginRequiredMixin, UnpublishedStudyMixin, DeleteView):
    model = SubjectFilterGroup
    template_name = 'recruitment/filtergroup_confirm_delete.html'

    def get_context_data(self, **kwargs):
        if self.study != self.object.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        return data

    def get_success_url(self):
        return reverse('recruitment:filtergroup_index', args=[self.study.pk])


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


class FilterGroupUpdateView(LoginRequiredMixin, UnpublishedStudyMixin, ModelFormSetView):
    model = SubjectFilter
    form_class = forms.SubjectFilterForm
    formset_class = FilterFormSet
    factory_kwargs = {
        'can_delete': True,
    }
    template_name = "recruitment/filtergroup.html"

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
    def post(self, request, study_pk, pk):
        study = get_object_or_404(Study, pk=study_pk)
        if study.published:
            raise PermissionDenied
        original = get_object_or_404(SubjectFilterGroup, study=study, pk=pk)
        clone = original.duplicate()
        messages.success(request, _(
            'The filters have been duplicated. You can now edit the duplicate.'))
        return redirect('recruitment:filtergroup_update', study.pk, clone.pk)
