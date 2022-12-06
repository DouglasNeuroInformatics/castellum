# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import View

from dateutil.relativedelta import relativedelta

from castellum.appointments.models import Appointment
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import ContactForm
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_pseudonym_if_exists
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment import filter_queries
from castellum.recruitment.mixins import BaseAttributesUpdateView
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import Participation
from castellum.studies.forms import StudyFilterForm
from castellum.studies.models import Study
from castellum.utils.expressions import exists
from castellum.utils.views import BaseProtectedMediaView

from .forms import SubjectPrivacyLevelForm
from .mixins import BaseAdditionalInfoUpdateView
from .mixins import BaseConsentChangeView
from .mixins import BaseDataProtectionUpdateView
from .mixins import BaseReportView
from .mixins import SubjectMixin
from .models import ExportAnswer
from .models import Report
from .models import Subject
from .models import SubjectCreationRequest

monitoring_logger = logging.getLogger('monitoring.subjects')


@method_decorator(sensitive_post_parameters(), 'dispatch')
class SubjectSearchView(LoginRequiredMixin, FormView):
    template_name = 'subjects/subject_search.html'
    form_class = SearchForm

    @cached_property
    def subjectcreationrequest(self):
        if 'from-request' in self.request.GET:
            pk = self.request.GET['from-request']
            return get_object_or_404(SubjectCreationRequest, data_is_deleted=False, pk=pk)

    def get_matches(self, search):
        user = self.request.user
        contacts = Contact.objects.fuzzy_filter(search)
        can_view_subject = user.has_perm('subjects.view_subject')
        for subject in Subject.objects.filter(filter_queries.uuid_filter(contacts)):
            has_privacy_level = user.has_privacy_level(subject.privacy_level)
            participations = []
            for participation in subject.participation_set.filter(study__status=Study.EXECUTION):
                can_access_study = user.has_perm('studies.access_study', obj=participation.study)
                invited = participation.status == Participation.INVITED
                can_recruit = (
                    has_privacy_level
                    and can_access_study
                    and user.has_perm('recruitment.recruit', obj=participation.study)
                )
                can_conduct = (
                    has_privacy_level
                    and can_access_study
                    and invited
                    and user.has_perm('recruitment.conduct_study', obj=participation.study)
                )
                can_search = invited and user.has_perm('recruitment.search_participations')
                if can_recruit or can_conduct or can_search:
                    participations.append((participation, can_recruit, can_conduct))
            if participations or can_view_subject:
                yield subject, subject.contact, participations, has_privacy_level

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count_total'] = Contact.objects.count()

        start = datetime.date.today() - relativedelta(months=6)
        context['count_updated'] = Contact.objects.filter(updated_at__gte=start).count()

        context['count_participated'] = Subject.objects.filter(
            participation__status=Participation.INVITED
        ).distinct().count()

        completeness, total = filter_queries.completeness_expr()
        context['count_complete'] = (
            Subject.objects
            .alias(completeness=completeness)
            .filter(completeness=total, deceased=False, blocked=False)
            .count()
        )

        context['count_recruitable'] = Subject.objects.filter(
            filter_queries.has_consent(),
            filter_queries.to_be_deleted(),
        ).exclude(
            pk__in=Participation._base_manager.filter(
                filter_queries._reverse_exclusive_studies()
            ).values('subject')
        ).count()

        context['subjectcreationrequest'] = self.subjectcreationrequest

        form = kwargs.get('form')
        if form and form.is_valid():
            context['matches'] = list(self.get_matches(form.cleaned_data['search']))

            if 'privacy_level_form' not in context:
                context['privacy_level_form'] = SubjectPrivacyLevelForm(user=self.request.user)
        return context

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: search term: "{search}" by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if 'privacy_level' not in request.POST:
            return super().post(request, *args, **kwargs)

        if not request.user.has_perm('subjects.change_subject'):
            raise PermissionDenied

        form = SearchForm(data=request.POST)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)

        if form.is_valid() and privacy_level_form.is_valid():
            if form.cleaned_data.get('last_name'):
                if 'from-request' in self.request.GET:
                    subject = self.subjectcreationrequest.convert_to_real_subject()
                    self.subjectcreationrequest.mark_as_deleted()
                else:
                    contact = Contact.objects.create(
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        phone_number=form.cleaned_data['phone_number'],
                        email=form.cleaned_data.get('email'),
                    )
                    subject = contact.subject

                subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
                subject.save()

                monitoring_logger.info('SubjectData update: {} by {}'.format(
                    subject.pk, self.request.user.pk
                ))
                return redirect('subjects:detail', pk=subject.pk)
            else:
                messages.error(request, _(
                    'Both first and last name must be provided in order to create a subject!'
                ))
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
        ))


class SubjectResolveView(PermissionRequiredMixin, FormView):
    template_name = 'subjects/subject_resolve.html'
    permission_required = 'subjects.view_subject'
    form_class = PseudonymForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['domains'] = self.request.user.general_domains.all()
        return kwargs

    def form_valid(self, form):
        try:
            subject = get_subject(form.cleaned_data['domain'], form.cleaned_data['pseudonym'])
            monitoring_logger.info('Pseudonym resolved: domain {} by {}'.format(
                form.cleaned_data['domain'], self.request.user.pk
            ))
            return redirect('subjects:detail', subject.pk)
        except Subject.DoesNotExist:
            messages.warning(self.request, _('No match found'))
            return self.render_to_response(self.get_context_data(form=form))


class SubjectDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'subjects.view_subject'
    template_name = 'subjects/subject_detail.html'
    tab = 'detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        completed, total = self.object.get_completeness()
        context['attribute_completeness'] = '{:.0%}'.format(completed / (total or 1))

        dropout_count = self.object.participation_set.filter(dropped_out=True).count()
        dropout_total = self.object.participation_set.filter(
            models.Q(status=Participation.INVITED) | models.Q(dropped_out=True)
        ).count()
        if dropout_total == 0:
            context['dropout_rate'] = '—'
        else:
            context['dropout_rate'] = '{:.0%}'.format(dropout_count / dropout_total)

        return context


class SubjectPseudonymsView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_pseudonyms.html'
    tab = 'detail'

    def has_permission(self):
        return (
            self.request.user.has_perm('subjects.export_subject')
            or self.request.user.has_perm('subjects.delete_subject')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domains'] = Domain.objects.filter(object_id=None)
        return context


class SubjectPseudonymView(SubjectMixin, PermissionRequiredMixin, View):
    def get_object(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def has_permission(self):
        return (
            self.request.user.has_perm('subjects.export_subject')
            or self.request.user.has_perm('subjects.delete_subject')
        )

    def get(self, request, *args, **kwargs):
        domain = get_object_or_404(Domain, key=kwargs['domain'], object_id=None)
        pseudonym = get_pseudonym_if_exists(self.subject, domain.key)

        monitoring_logger.info('Pseudonym access: domain {} by {}'.format(
            domain.key, self.request.user.pk
        ))

        return HttpResponse(pseudonym or '—')


class SubjectDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    permission_required = 'subjects.delete_subject'
    tab = 'delete'

    def is_last_legal_representative(self):
        return any(
            ward.legal_representatives.count() == 1
            for ward in self.object.contact.legal_representative_of.all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_participations'] = self.object.participation_set.exists()
        context['is_last_legal_representative'] = self.is_last_legal_representative()
        context['has_pseudonym_in_general_domain'] = (
            self.subject.pseudonym_set.filter(domain__object_id=None).exists()
        )
        return context

    def get_success_url(self):
        return reverse('subjects:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.participation_set.exists():
            return self.get(request, *args, **kwargs)
        response = super().delete(request, *args, **kwargs)
        if self.object.to_be_deleted:
            monitoring_logger.info('Subject deleted by {} as requested on {}'.format(
                self.request.user.pk, self.object.to_be_deleted
            ))
        else:
            monitoring_logger.info('Subject deleted by {}'.format(self.request.user.pk))
        messages.success(self.request, _('Subject has been deleted.'))
        return response


class SubjectExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_export.html'
    permission_required = 'subjects.export_subject'
    tab = 'export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.export_requested:
            context['has_participations'] = self.object.participation_set.exists()
            context['general_domains_exist'] = Domain.objects.filter(object_id=None).exists()
            context['appointments'] = Appointment.objects.filter(participation__subject=self.object)

            context['attributes'] = []
            for description in AttributeDescription.objects.all():
                value = self.object.attributes.get(description.json_key)
                context['attributes'].append((
                    description.label, description.field.get_display(value)
                ))

            monitoring_logger.info('GDPR-Request export: {} by {}'.format(
                self.object.pk, self.request.user.pk
            ))

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
    base_template = 'subjects/subject_base.html'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)


class DataProtectionUpdateView(SubjectUpdateMixin, BaseDataProtectionUpdateView):
    tab = 'data-protection'

    def get_subject_media_url(self, path):
        return reverse('subject-media', args=[self.subject.pk, path])


class ConsentChangeView(SubjectMixin, BaseConsentChangeView):
    base_template = 'subjects/subject_base.html'
    tab = 'data-protection'

    def get_success_url(self):
        return reverse('subjects:data-protection', args=[self.subject.pk])


class AdditionalInfoUpdateView(SubjectUpdateMixin, BaseAdditionalInfoUpdateView):
    tab = 'additional-info'


class ContactUpdateView(SubjectUpdateMixin, BaseContactUpdateView):
    tab = 'contact'
    context = 'subject_management'

    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        return subject.contact


class AttributesUpdateView(SubjectUpdateMixin, BaseAttributesUpdateView):
    tab = 'attributes'


class DeleteRecruitmentDataView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/confirm_delete_recruitment_data.html'
    tab = 'attributes'

    def post(self, request, *args, **kwargs):
        attributes = {}
        if settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID:
            desc = AttributeDescription.objects.get(
                pk=settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID
            )
            attributes[desc.json_key] = self.subject.attributes[desc.json_key]

        self.subject.attributes = attributes
        self.subject.save()

        self.subject.study_type_disinterest.all().delete()

        return redirect('subjects:attributes', pk=self.subject.pk)


class ReportView(SubjectMixin, BaseReportView):
    permission_required = ['subjects.view_subject']

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('subjects:detail', args=[self.subject.pk])


class ParticipationListView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = Participation
    template_name = 'subjects/participation_list.html'
    permission_required = 'subjects.view_subject'
    tab = 'participations'
    subtab = 'list'

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def get_queryset(self):
        return (
            self.subject.participation_set
            .filter(status=Participation.INVITED)
            .order_by('-updated_at')
        )


class ParticipationRecruitView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = Study
    template_name = 'subjects/participation_recruit.html'
    permission_required = 'subjects.view_subject'
    tab = 'participations'
    subtab = 'recruit'

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def get_queryset(self):
        perms = ['recruitment.recruit', 'studies.access_study']
        studies = (
            Study.objects
            .filter(status=Study.EXECUTION)
            .exclude(pk__in=Study.objects.filter(
                participation__subject=self.subject,
                participation__status=Participation.INVITED,
            ))
            # study.p is the list that contains the particiaption (if it exists) or nothing.
            # I did not find a better way to do this.
            .prefetch_related(models.Prefetch(
                'participation_set',
                queryset=self.subject.participation_set.all(),
                to_attr='p',
            ))
        )

        pks = []
        for study in studies:
            if (
                self.request.user.has_perms(perms, obj=study)
                and Subject.objects.filter(filter_queries.study(study), pk=self.subject.pk).exists()
            ):
                pks.append(study.pk)
        return studies.filter(pk__in=pks)

    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=request.POST['study'], status=Study.EXECUTION)

        perms = ['recruitment.recruit', 'studies.access_study']
        if not request.user.has_perms(perms, obj=study):
            raise PermissionDenied

        participation, __ = Participation.objects.get_or_create(subject=self.subject, study=study)

        url = reverse('recruitment:contact', args=[study.pk, participation.pk])
        return redirect(url)


class ParticipationAddView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = Study
    template_name = 'subjects/participation_add.html'
    permission_required = 'subjects.change_subject'
    tab = 'participations'
    subtab = 'add'

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        self.form = StudyFilterForm(self.request.GET)
        self.form.full_clean()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        q = self.form.cleaned_data.get('q', '')
        if q:
            # study.p is the list that contains the particiaption (if it exists) or nothing.
            # I did not find a better way to do this.
            qs = Study.objects.prefetch_related(models.Prefetch(
                'participation_set',
                queryset=self.subject.participation_set.all(),
                to_attr='p',
            ))
            for part in q.split():
                qs = qs.filter(
                    models.Q(name__icontains=part) | models.Q(contact_person__icontains=part)
                )
            qs = qs.filter(is_filter_trial=False)
            return qs
        else:
            return Study.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=request.POST['study'])

        Participation._base_manager.update_or_create(
            subject=self.subject, study=study, defaults={
                'status': Participation.INVITED,
                'dropped_out': False,
            }
        )

        return self.get(request, *args, **kwargs)


class ParticipationDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Participation
    permission_required = ['studies.access_study', 'subjects.delete_subject']
    tab = 'delete'

    def get_object(self):
        return get_object_or_404(
            Participation, pk=self.kwargs['pk'], subject=self.kwargs['subject_uuid']
        )

    def get_success_url(self):
        return reverse('subjects:delete', args=[self.subject.pk])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().delete(request, *args, **kwargs)
        monitoring_logger.info('Participation in Study {} deleted by {}'.format(
            self.object.study.name, self.request.user.pk
        ))
        return response


@method_decorator(sensitive_post_parameters(), 'dispatch')
class LegalRepresentativeSearchView(PermissionRequiredMixin, SubjectSearchView):
    template_name = 'subjects/legal_representative_search.html'
    permission_required = 'subjects.view_subject'
    nochrome = True

    def get_matches(self, search):
        contacts = Contact.objects.fuzzy_filter(search)
        return Subject.objects.filter(filter_queries.uuid_filter(contacts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid() and 'contact_form' not in context:
            context['contact_form'] = ContactForm(user=self.request.user, initial=form.cleaned_data)
        return context

    def post(self, request, *args, **kwargs):
        if 'privacy_level' not in request.POST:
            return super().post(request, *args, **kwargs)

        if not request.user.has_perm('subjects.change_subject'):
            raise PermissionDenied

        form = SearchForm(data=request.POST)
        privacy_level_form = SubjectPrivacyLevelForm(user=self.request.user, data=request.POST)
        contact_form = ContactForm(user=self.request.user, data=request.POST)

        if form.is_valid() and privacy_level_form.is_valid() and contact_form.is_valid():
            contact = contact_form.save()
            contact.subject.privacy_level = privacy_level_form.cleaned_data['privacy_level']
            contact.subject.save()

            monitoring_logger.info('SubjectData update: {} by {}'.format(
                contact.subject.pk, self.request.user.pk
            ))
            return TemplateResponse(self.request, 'subjects/legal_representative_success.html', {
                'name': contact.full_name,
                'uuid': contact.subject.pk,
            })
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
            contact_form=contact_form,
        ))


class BaseMaintenanceView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'

    def get_queryset(self):
        return super().get_queryset().filter(
            to_be_deleted__isnull=True,
            deceased=False,
            blocked=False,
        )


class MaintenanceAttributesView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_attributes.html'
    tab = 'attributes'

    def get_queryset(self):
        today = datetime.date.today()

        completeness, total = filter_queries.completeness_expr()
        full_age = Contact.objects.exclude(
            date_of_birth__gt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE),
        )
        return (
            super().get_queryset()
            .annotate(completeness=completeness)
            .filter(
                filter_queries.has_consent(),
                filter_queries.uuid_filter(full_age),
                completeness__lt=total,
            )
            .order_by('completeness')
        )


class MaintenanceContactView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_contact.html'
    tab = 'contact'

    def get_queryset(self):
        contacts = Contact.objects\
            .alias(
                legal_representative_count=models.Count('legal_representatives'),
                legal_representative_of_count=models.Count('legal_representative_of'),
            )\
            .filter(
                models.Q(
                    gender='',
                ) | models.Q(
                    legal_representative_count=0,
                    address=None,
                    email='',
                    phone_number='',
                ) | models.Q(
                    legal_representative_of_count=0,
                    date_of_birth=None,
                )
            )
        return super().get_queryset().filter(filter_queries.uuid_filter(contacts)).order_by('pk')


class MaintenanceDuplicatesView(BaseMaintenanceView):
    model = Contact
    template_name = 'subjects/maintenance_duplicates.html'
    tab = 'duplicates'

    def get_queryset(self):
        to_be_deleted = list(
            Subject.objects
            .filter(to_be_deleted__isnull=False)
            .values_list('pk', flat=True)
            .order_by()
        )

        return (
            Contact.objects
            .values('first_name', 'last_name')
            .exclude(subject_uuid__in=to_be_deleted)
            .alias(
                count=models.Count('id'),
                date_of_birth_count=models.Count('date_of_birth', distinct=True),
            )
            .filter(
                count__gt=1,
                date_of_birth_count__lt=models.F('count'),
            )
            .order_by('last_name', 'first_name')
        )


class MaintenanceConsentView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_consent.html'
    tab = 'consent'

    def get_by_consent_from_before_full_age(self):
        today = datetime.date.today()

        full_age = Contact.objects.exclude(
            date_of_birth__gt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE),
        )

        return super().get_queryset().filter(
            filter_queries.uuid_filter(full_age),
            filter_queries.has_consent(),
            consent__underage_when_given=True,
        )

    def get_by_deprecated_document(self):
        return (
            super().get_queryset()
            .filter(filter_queries.has_consent())
            .exclude(pk__in=Subject.objects.filter(
                filter_queries.has_consent(exclude_deprecated=True)
            ))
        )

    def get_queryset(self):
        return (
            Subject.objects
            .annotate(
                consent_document_deprecated=exists(
                    self.get_by_deprecated_document(), pk=models.OuterRef('pk')
                ),
                consent_from_before_full_age=exists(
                    self.get_by_consent_from_before_full_age(), pk=models.OuterRef('pk')
                ),
            )
            .exclude(
                consent_document_deprecated=False,
                consent_from_before_full_age=False,
            )
            .select_related('consent__document')
            .order_by('pk')
        )


class MaintenanceWaitingView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_waiting.html'
    tab = 'waiting'

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(consent__isnull=True)
            .order_by('pk')
        )


class MaintenanceReliabilityView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_reliability.html'
    tab = 'reliability'

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate_reliability()
            .annotate(ratio=100 * models.F('reliability_issues') / models.F('reliability_total'))
            .filter(
                reliability_issues__gt=1,
                ratio__gte=50,
            )
            .order_by('-ratio')
        )


class MaintenanceEstrangedSubjectsView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_estranged_subjects.html'
    tab = 'estranged_subjects'

    def get_queryset(self):
        return super().get_queryset().filter(
            filter_queries.has_consent(include_waiting=True),
            updated_at__lte=timezone.now() - settings.CASTELLUM_ENSTRANGED_SUBJECTS_PERIOD,
        ).order_by("updated_at")


class MaintenanceSubjectCreationRequestView(PermissionRequiredMixin, ListView):
    model = SubjectCreationRequest
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_subjectcreationrequest.html'
    tab = 'subjectcreationrequest'

    def get_queryset(self):
        return SubjectCreationRequest.objects.filter(data_is_deleted=False).order_by('created_at')


class SubjectCreationRequestDeleteView(PermissionRequiredMixin, DeleteView):
    model = SubjectCreationRequest
    permission_required = 'subjects.change_subject'
    tab = 'subjectcreationrequest'

    def get_success_url(self):
        return reverse('subjects:index')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mark_as_deleted()
        return redirect(self.get_success_url())


class SubjectProtectedMediaView(SubjectMixin, PermissionRequiredMixin, BaseProtectedMediaView):
    permission_required = ['subjects.view_subject']

    def get_object(self):
        return get_object_or_404(Subject, pk=self.kwargs['uuid'])

    def get_path(self):
        return 'subjects/{}'.format(self.kwargs['path'])
