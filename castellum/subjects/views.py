# (c) 2018-2020
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

import datetime
import logging
import zipfile

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from dateutil.relativedelta import relativedelta

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import ContactForm
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study
from castellum.utils.views import GetFormView

from .forms import SubjectPrivacyLevelForm
from .mixins import BaseAdditionalInfoUpdateView
from .mixins import BaseDataProtectionUpdateView
from .mixins import SubjectMixin
from .models import Consent
from .models import ExportAnswer
from .models import Subject

monitoring_logger = logging.getLogger('monitoring.subjects')


class SubjectSearchView(PermissionRequiredMixin, GetFormView):
    template_name = 'subjects/subject_search.html'
    permission_required = 'contacts.view_contact'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count_total'] = Contact.objects.count()

        start = datetime.date.today() - relativedelta(months=6)
        context['count_updated'] = Contact.objects.filter(updated_at__gte=start).count()

        context['count_participated'] = Subject.objects.filter(
            participationrequest__status=ParticipationRequest.INVITED
        ).distinct().count()

        completeness, total = filter_queries.completeness_expr()
        context['count_complete'] = Subject.objects\
            .annotate(completeness=completeness)\
            .filter(completeness=total)\
            .count()

        context['count_consent'] = Subject.objects.filter(filter_queries.has_consent()).count()

        context['is_post'] = self.request.method == 'POST'
        form = kwargs.get('form')
        if form and form.is_valid():
            context['matches'] = Contact.objects.fuzzy_filter(form.cleaned_data['search'])
            if 'privacy_level_form' not in context:
                context['privacy_level_form'] = SubjectPrivacyLevelForm(user=self.request.user)
        return context

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: search term: "{search}" by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('contacts.add_contact'):
            raise PermissionDenied

        form = SearchForm(data=request.GET)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)

        if form.is_valid() and privacy_level_form.is_valid():
            if form.cleaned_data.get('last_name'):
                contact = Contact.objects.create(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data.get('email'),
                )
                contact.subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
                contact.subject.save()

                monitoring_logger.info('SubjectData update: {} by {}'.format(
                    contact.subject_id, self.request.user.pk
                ))
                return redirect('subjects:detail', pk=contact.subject.pk)
            else:
                messages.error(request, _(
                    'Both first and last name must be provided in order to create a subject!'
                ))
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
        ))


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

        context['coverletter_exists'] = bool(settings.CASTELLUM_COVERLETTER_TEMPLATE)

        return context


class SubjectDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    permission_required = 'subjects.delete_subject'
    tab = 'delete'

    def is_last_guardian(self):
        if self.object.contact.guardian_of.exists():
            for ward in Contact.objects.filter(guardians=self.object.contact):
                if ward.guardians.count() <= 1:
                    return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_participationrequests'] = self.object.participationrequest_set.exists()
        context['is_last_guardian'] = self.is_last_guardian()
        return context

    def get_success_url(self):
        return reverse('subjects:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.participationrequest_set.exists():
            return self.get(request, *args, **kwargs)
        monitoring_logger.info('Subject deleted by {}'.format(self.request.user.pk))
        messages.success(self.request, _('Subject has been deleted.'))
        return super().delete(request, *args, **kwargs)


class SubjectExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_export.html'
    permission_required = 'subjects.view_subject'
    tab = 'export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.export_requested:
            monitoring_logger.info('GDPR-Request export: {} by {}'.format(
                self.object.pk, self.request.user.pk
            ))

            context['dataset_list'] = [self.object, self.object.contact]

            try:
                context['dataset_list'].append(self.object.attributeset)
            except ObjectDoesNotExist:
                pass

            for participation_request in self.object.participationrequest_set.all():
                context['dataset_list'].append(participation_request)

            try:
                context['dataset_list'].append(self.object.consent)
            except ObjectDoesNotExist:
                pass

            for answer in self.object.exportanswer_set.all():
                context['dataset_list'].append(answer)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.export_requested:
            self.object.export_requested = None
            ExportAnswer.objects.create(subject=self.object, created_by=request.user.username)
        else:
            self.object.export_requested = datetime.date.today()
        self.object.save()
        return redirect('subjects:export', self.object.pk)


class SubjectUpdateMixin(SubjectMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'subjects/subject_base.html'
        return context

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)


class DataProtectionUpdateView(SubjectUpdateMixin, BaseDataProtectionUpdateView):
    tab = 'data-protection'

    def get_success_url(self):
        return reverse('subjects:data-protection', args=[self.object.pk])


class AdditionalInfoUpdateView(SubjectUpdateMixin, BaseAdditionalInfoUpdateView):
    tab = 'additional-info'

    def get_success_url(self):
        return reverse('subjects:additional-info', args=[self.object.pk])


class ContactUpdateView(SubjectUpdateMixin, BaseContactUpdateView):
    tab = 'contact'

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        return subject.contact

    def get_success_url(self):
        return reverse('subjects:contact', args=[self.object.subject.pk])


class AttributeSetUpdateView(SubjectUpdateMixin, BaseAttributeSetUpdateView):
    tab = 'attributeset'

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        attributeset, __ = AttributeSet.objects.get_or_create(
            subject=subject, defaults={'data': {}}
        )
        return attributeset

    def get_success_url(self):
        return reverse('subjects:attributeset', args=[self.object.subject.pk])


class ParticipationListView(SubjectMixin, PermissionRequiredMixin, ListView):
    tab = 'participations'
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

    def get_queryset(self, study_status=Study.EXECUTION):
        queryset = self.model.objects\
            .filter(subject=self.subject, study__status=study_status)\
            .order_by('-updated_at')
        return [
            participation_request for participation_request in queryset
            if self.is_permitted(participation_request.study)
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finished_list'] = self.get_queryset(study_status=Study.FINISHED)
        return context


class ParticipationDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    tab = 'delete'
    model = ParticipationRequest
    permission_required = ['studies.access_study', 'recruitment.delete_participationrequest']

    def get_object(self):
        return get_object_or_404(
            ParticipationRequest, pk=self.kwargs['pk'], subject_id=self.kwargs['subject_pk']
        )

    def get_success_url(self):
        return reverse('subjects:delete', args=[self.subject.pk])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        monitoring_logger.info('ParticipationRequest in Study {} deleted by {}'.format(
            self.object.study.name, self.request.user.pk
        ))
        return super().delete(self, request, *args, **kwargs)


class AddToStudyView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_add_to_study.html'
    permission_required = 'contacts.view_contact'
    tab = 'participations'

    def get_studies(self, subject):
        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        studies = (
            Study.objects
            .filter(status=Study.EXECUTION)
            .exclude(participationrequest__subject=subject)
        )
        for study in studies:
            if (
                self.request.user.has_perms(perms, obj=study) and
                Subject.objects.filter(filter_queries.study(study), pk=subject.pk).exists()
            ):
                yield study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['attributeset'] = self.object.attributeset
            context['studies'] = list(self.get_studies(self.object))
        except AttributeSet.DoesNotExist:
            pass

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        study = get_object_or_404(Study, pk=request.POST['study'], status=Study.EXECUTION)

        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        if not request.user.has_perms(perms, obj=study):
            raise PermissionDenied

        participation_request = ParticipationRequest.objects.create(
            subject=self.object, study=study
        )

        url = reverse('recruitment:contact', args=[study.pk, participation_request.pk])
        return redirect(url + '?context=subjects:participation-list')


class AddToFinishedStudyView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_add_to_study.html'
    permission_required = 'subjects.change_subject'
    tab = 'participations'

    def get_studies(self, subject):
        return (
            Study.objects
            .filter(status=Study.FINISHED)
            .exclude(participationrequest__subject=subject)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributeset'] = True
        context['studies'] = list(self.get_studies(self.object))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        study = get_object_or_404(Study, pk=request.POST['study'], status=Study.FINISHED)

        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        if not request.user.has_perms(perms, obj=study):
            raise PermissionDenied

        ParticipationRequest.objects.create(
            subject=self.object, study=study, status=ParticipationRequest.INVITED
        )

        return redirect('subjects:participation-list', self.object.pk)


class GuardianSearchView(SubjectSearchView):
    template_name = 'subjects/guardian_search.html'
    nochrome = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid() and 'contact_form' not in context:
            context['contact_form'] = ContactForm(
                user=self.request.user, initial=form.cleaned_data, is_guardian=True
            )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('contacts.add_contact'):
            raise PermissionDenied

        form = SearchForm(data=request.GET)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)
        contact_form = ContactForm(user=self.request.user, data=request.POST, is_guardian=True)

        if form.is_valid() and privacy_level_form.is_valid() and contact_form.is_valid():
            contact = contact_form.save()
            contact.subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
            contact.subject.save()

            monitoring_logger.info('SubjectData update: {} by {}'.format(
                contact.subject_id, self.request.user.pk
            ))
            return TemplateResponse(self.request, 'subjects/guardian_success.html', {
                'name': contact.full_name,
                'pk': contact.subject.pk,
            })
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
            contact_form=contact_form,
        ))


class MaintenanceAttributesView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_attributes.html'
    tab = 'attributes'

    def get_queryset(self):
        completeness, total = filter_queries.completeness_expr()
        return super().get_queryset()\
            .exclude(attributeset=None)\
            .annotate(completeness=completeness)\
            .filter(filter_queries.has_consent(), completeness__lt=total)\
            .order_by('completeness')


class MaintenanceContactView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_contact.html'
    tab = 'contact'

    def get_queryset(self):
        contacts = Contact.objects\
            .annotate(
                guardian_count=models.Count('guardians'),
                guardian_of_count=models.Count('guardian_of'),
            )\
            .filter(
                models.Q(
                    guardian_count=0,
                    address=None,
                    email='',
                    phone_number='',
                ) | models.Q(
                    guardian_of_count=0,
                    date_of_birth=None,
                )
            )\
            .values('subject_id')\
            .order_by()
        return super().get_queryset()\
            .filter(pk__in=[c['subject_id'] for c in contacts])\
            .order_by('pk')


class MaintenanceDuplicatesView(PermissionRequiredMixin, ListView):
    model = Contact
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_duplicates.html'
    tab = 'duplicates'

    def get_queryset(self):
        duplicates = []

        names = Contact.objects\
            .values('first_name', 'last_name')\
            .annotate(count=models.Count('id'))\
            .filter(count__gt=1)

        for name in names:
            date_of_birth_count = Contact.objects.filter(
                first_name=name['first_name'],
                last_name=name['last_name'],
                date_of_birth__isnull=False,
            ).values('date_of_birth').distinct().count()

            if date_of_birth_count < name['count']:
                duplicates.append(name)

        return duplicates


class MaintenanceConsentView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_consent.html'
    tab = 'consent'

    def get_by_consent_from_before_full_age(self):
        today = datetime.date.today()

        # date_of_birth is stored in Contact, so we cannot query it
        # directly. As an optimization, we only look at subjects that
        # came of age in the past year.
        contacts = Contact.objects.filter(
            date_of_birth__lt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE),
            date_of_birth__gt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE + 1),
        )

        pks = [c.subject.pk for c in contacts if c.subject.has_consent_from_before_full_age]
        return Subject.objects.filter(pk__in=pks)

    def get_by_outdated_document(self):
        return Subject.objects\
            .exclude(filter_queries.has_consent(exclude_deprecated=True))\
            .filter(consent__status=Consent.CONFIRMED)

    def get_queryset(self):
        return Subject.objects.none().union(
            self.get_by_consent_from_before_full_age(),
            self.get_by_outdated_document(),
        )


class MaintenanceWaitingView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_waiting.html'
    tab = 'waiting'

    def get_queryset(self):
        return super().get_queryset().filter(consent__status=Consent.WAITING)


class CoverletterView(SubjectMixin, PermissionRequiredMixin, SingleObjectMixin, View):
    model = Subject
    permission_required = 'contacts.view_contact'

    def get_data(self):
        contact = self.object.contact
        try:
            return (contact.full_name, *contact.address.lines())
        except Address.DoesNotExist:
            return (contact.full_name, '', '')

    def patch_document(self, content):
        name, address1, address2 = self.get_data()

        return content\
            .replace(b'{name}', name.encode('utf8'))\
            .replace(b'{address1}', address1.encode('utf8'))\
            .replace(b'{address2}', address2.encode('utf8'))

    def patch_zipfile(self, zin, zout):
        for name in zin.namelist():
            with zin.open(name, 'r') as fh:
                content = fh.read()
            if name == 'word/document.xml':
                content = self.patch_document(content)
            with zout.open(name, 'w') as fh:
                fh.write(content)

    def get(self, request, *args, **kwargs):
        if not settings.CASTELLUM_COVERLETTER_TEMPLATE:
            raise Http404

        self.object = self.get_object()

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

        zresponse = zipfile.ZipFile(response, 'w')
        with zipfile.ZipFile(settings.CASTELLUM_COVERLETTER_TEMPLATE, 'r') as zin:
            self.patch_zipfile(zin, zresponse)

        return response
