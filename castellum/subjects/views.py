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
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import ContactForm
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.utils import get_study_filter_q
from castellum.studies.models import Study
from castellum.subjects.mixins import SubjectNoteFormMixin
from castellum.utils.views import GetFormView

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
        return context

    def user_has_privacy_level(self, contact):
        return self.request.user.has_privacy_level(contact.subject.privacy_level)

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: {{first_name: "{first_name}"; last_name: "{last_name}"; '
            'date_of_birth: "{date_of_birth}"}} by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        matches = [
            (contact, self.user_has_privacy_level(contact))
            for contact in Contact.objects.fuzzy_filter(**form.cleaned_data)
        ]

        return self.render_to_response(self.get_context_data(
            form=form, query='?' + urlencode(form.cleaned_data), matches=matches))


class SubjectDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'contacts.view_contact'
    template_name = 'subjects/subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pseudonym = get_pseudonym(self.object, Contact.domain)
        context['contact'] = Contact.objects.get(pseudonym=pseudonym)

        context['updated_at'] = max(self.object.updated_at, context['contact'].updated_at)

        try:
            context['updated_at'] = max(context['updated_at'], self.object.attributeset.updated_at)

            completed, total = self.object.attributeset.get_completeness()
            context['attributeset_completeness'] = '%i%%' % (100 * completed / total)
        except AttributeSet.DoesNotExist:
            pass

        return context


class SubjectCreateView(PermissionRequiredMixin, SubjectNoteFormMixin, CreateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'contacts.add_contact'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_cancel_url(self):
        return reverse('subjects:index') + '?' + self.request.META['QUERY_STRING']

    def get_initial(self):
        initial = super().get_initial()
        for key in ['first_name', 'last_name', 'date_of_birth']:
            if key in self.request.GET:
                initial[key] = self.request.GET[key]
        return initial

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def form_valid(self, form, notes_formset):
        response = super().form_valid(form, notes_formset)

        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))

        return response


class SubjectExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_export.html'
    permission_required = 'subjects.view_subject'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monitoring_logger.info('GDPR-Request export: {} by {}'.format(
            self.object.pk, self.request.user.pk))

        context['dataset_list'] = [self.object]

        pseudonym = get_pseudonym(self.object, Contact.domain)
        context['dataset_list'].append(Contact.objects.get(pseudonym=pseudonym))

        try:
            context['dataset_list'].append(self.object.attributeset)
        except ObjectDoesNotExist:
            pass

        for participation in self.object.participationrequest_set.all():
            context['dataset_list'].append(participation)

        for consent in self.object.consentconfirmation_set.all():
            context['dataset_list'].append(consent)

        return context


class AddToStudyView(SubjectMixin, LoginRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_studies.html'

    def get_studies(self, attributeset):
        qs = AttributeSet.objects.filter(pk=attributeset.pk)
        for study in Study.objects.filter(published=True):
            if (
                self.request.user.has_perm('recruitment.add_participationrequest', obj=study) and
                self.request.user.has_perm('studies.access_study', obj=study) and
                qs.filter(get_study_filter_q(study)).exists()
            ):
                request = attributeset.subject.participationrequest_set.filter(study=study)
                if not request.exists():
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
        study = get_object_or_404(Study, pk=request.POST['study'], published=True)

        for perm in ['recruitment.add_participationrequest', 'studies.access_study']:
            if not request.user.has_perm(perm, obj=study):
                raise PermissionDenied

        participation_request = ParticipationRequest.objects.create(
            subject=self.object, study=study)

        url = reverse('recruitment:contact', args=[study.pk, participation_request.pk])
        return redirect(url + '?contacts')


class ContactUpdateView(BaseContactUpdateView):
    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        pseudonym = get_pseudonym(subject, Contact.domain)
        return get_object_or_404(Contact, pseudonym=pseudonym)


class AttributeSetUpdateView(BaseAttributeSetUpdateView):
    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        attributeset, __ = AttributeSet.objects.get_or_create(
            subject=subject, defaults={'data': {}})
        return attributeset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "subjects/base.html"
        return context
