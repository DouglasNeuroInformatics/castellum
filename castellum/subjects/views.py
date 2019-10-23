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

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import ContactForm
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study
from castellum.utils.views import GetFormView

from .forms import SubjectPrivacyLevelForm
from .mixins import BaseSubjectUpdateView
from .mixins import SubjectMixin
from .models import Subject

monitoring_logger = logging.getLogger('monitoring.subjects')


class SubjectSearchView(PermissionRequiredMixin, GetFormView):
    template_name = 'subjects/subject_search.html'
    permission_required = 'contacts.view_contact'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_number_subjects'] = Contact.objects.count()
        context['is_post'] = self.request.method == 'POST'
        form = kwargs.get('form')
        if form and form.is_valid():
            data = form.cleaned_data
            context['matches'] = Contact.objects.fuzzy_filter(**data)
            if 'privacy_level_form' not in context:
                context['privacy_level_form'] = SubjectPrivacyLevelForm(user=self.request.user)
        return context

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: {{first_name: "{first_name}"; last_name: "{last_name}" by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('contacts.add_contact'):
            raise PermissionDenied

        form = SearchForm(data=request.GET)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)

        if form.is_valid() and privacy_level_form.is_valid():
            contact = form.save()
            contact.subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
            contact.subject.save()

            monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
                Contact.domain,
                contact.pseudonym,
                self.request.user.pk))
            return redirect('subjects:detail', pk=contact.subject.pk)
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form))


class SubjectDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'contacts.view_contact'
    template_name = 'subjects/subject_detail.html'
    tab = 'detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['updated_at'] = max(self.object.updated_at, self.object.contact.updated_at)

        try:
            context['updated_at'] = max(context['updated_at'], self.object.attributeset.updated_at)

            completed, total = self.object.attributeset.get_completeness()
            context['attributeset_completeness'] = '%i%%' % (100 * completed / (total or 1))
        except AttributeSet.DoesNotExist:
            pass

        return context


class SubjectDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    permission_required = 'subjects.delete_subject'
    tab = 'detail'

    def get_success_url(self):
        return reverse('subjects:index')


class SubjectExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_export.html'
    permission_required = 'subjects.view_subject'
    tab = 'export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monitoring_logger.info('GDPR-Request export: {} by {}'.format(
            self.object.pk, self.request.user.pk))

        context['dataset_list'] = [self.object, self.object.contact]

        try:
            context['dataset_list'].append(self.object.attributeset)
        except ObjectDoesNotExist:
            pass

        for participation_request in self.object.participationrequest_set.all():
            context['dataset_list'].append(participation_request)

        for consent in self.object.consentconfirmation_set.all():
            context['dataset_list'].append(consent)

        return context


class SubjectUpdateView(BaseSubjectUpdateView):
    tab = 'subject'

    def get_success_url(self):
        return reverse('subjects:subject', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'subjects/subject_base.html'
        return context

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)


class ContactUpdateView(BaseContactUpdateView):
    tab = 'contact'

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        return subject.contact

    def get_success_url(self):
        return reverse('subjects:contact', args=[self.object.subject.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'subjects/subject_base.html'
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class AttributeSetUpdateView(BaseAttributeSetUpdateView):
    tab = 'attributeset'

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        attributeset, __ = AttributeSet.objects.get_or_create(
            subject=subject, defaults={'data': {}})
        return attributeset

    def get_success_url(self):
        return reverse('subjects:attributeset', args=[self.object.subject.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "subjects/subject_base.html"
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class ParticipationListView(SubjectMixin, PermissionRequiredMixin, ListView):
    tab = 'studyparticipation'
    model = ParticipationRequest
    template_name = 'subjects/subject_participationlist.html'
    permission_required = 'contacts.view_contact'

    @cached_property
    def subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def is_permitted(self, study):
        return self.request.user.has_perm('studies.access_study', obj=study) and (
            self.request.user.has_perm('recruitment.view_participation_pseudonyms', obj=study) or
            self.request.user.has_perm('recruitment.change_participationrequest', obj=study)
        )

    def get_queryset(self):
        queryset = self.model.objects\
            .filter(subject=self.subject, study__study_mode=Study.EXECUTION)\
            .order_by('-updated_at')
        return [
            participation_request for participation_request in queryset
            if self.is_permitted(participation_request.study)
        ]


class ParticipationDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    tab = 'studyparticipation'
    model = ParticipationRequest
    permission_required = ['studies.access_study', 'recruitment.delete_participationrequest']

    def get_object(self):
        return get_object_or_404(
            ParticipationRequest, pk=self.kwargs['pk'], subject_id=self.kwargs['subject_pk']
        )

    def get_success_url(self):
        return reverse('subjects:studyparticipation', args=[self.subject.pk])


class AddToStudyView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_add_to_study.html'
    permission_required = 'contacts.view_contact'
    tab = 'studyparticipation'

    def get_studies(self, attributeset):
        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        studies = (
            Study.objects
            .filter(study_mode=Study.EXECUTION)
            .exclude(participationrequest__subject=attributeset.subject)
        )
        for study in studies:
            if (
                self.request.user.has_perms(perms, obj=study) and
                AttributeSet.apply_study_filter(study).filter(pk=attributeset.pk).exists()
            ):
                yield study

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        try:
            data['attributeset'] = self.object.attributeset
            data['studies'] = list(self.get_studies(self.object.attributeset))
        except AttributeSet.DoesNotExist:
            pass

        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        study = get_object_or_404(Study, pk=request.POST['study'], study_mode=Study.EXECUTION)

        for perm in ['recruitment.add_participationrequest', 'studies.access_study']:
            if not request.user.has_perm(perm, obj=study):
                raise PermissionDenied

        participation_request = ParticipationRequest.objects.create(
            subject=self.object, study=study)

        url = reverse('recruitment:contact', args=[study.pk, participation_request.pk])
        return redirect(url + '?context=subjects:studyparticipation')


class GuardianSearchView(SubjectSearchView):
    template_name = 'subjects/guardian_search.html'
    nochrome = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid() and 'contact_form' not in context:
            context['contact_form'] = ContactForm(
                user=self.request.user, initial=form.cleaned_data
            )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('contacts.add_contact'):
            raise PermissionDenied

        form = SearchForm(data=request.GET)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)
        contact_form = ContactForm(user=self.request.user, data=request.POST)

        if form.is_valid() and privacy_level_form.is_valid() and contact_form.is_valid():
            contact = contact_form.save()
            contact.subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
            contact.subject.no_recruitment = True
            contact.subject.save()

            monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
                Contact.domain,
                contact.pseudonym,
                self.request.user.pk))
            return TemplateResponse(self.request, 'subjects/guardian_success.html', {
                'name': contact.full_name,
                'pk': contact.subject.pk,
            })
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
            contact_form=contact_form,
        ))
