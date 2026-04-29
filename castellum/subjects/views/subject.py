# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db import models
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import View

from castellum.appointments.models import Appointment
from castellum.audit.helpers import audit
from castellum.audit.models import AuditEvent
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import ContactForm
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import BlockHash
from castellum.contacts.models import Contact
from castellum.data_protection.helpers import delete_recruitment_data
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_pseudonym_if_exists
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment import filter_queries
from castellum.recruitment.mixins import BaseAttributesUpdateView
from castellum.recruitment.mixins import BaseRelationCreateView
from castellum.recruitment.mixins import BaseRelationDeleteView
from castellum.recruitment.models import Attribute
from castellum.recruitment.models import Participation
from castellum.recruitment.statistics import render_statistics
from castellum.studies.models import Study
from castellum.utils import cached_function
from castellum.utils.views import BaseProtectedMediaView

from ..forms import SubjectDeleteForm
from ..forms import SubjectMergeForm
from ..forms import SubjectPrivacyLevelForm
from ..mixins import BaseAdditionalInfoUpdateView
from ..mixins import BaseConsentChangeView
from ..mixins import BaseDataProtectionUpdateView
from ..mixins import BaseReportView
from ..mixins import SubjectMixin
from ..models import Consent
from ..models import ExportAnswer
from ..models import Report
from ..models import Subject
from ..models import SubjectCreationRequest


@cached_function(timeout=600)
def get_subject_stats():
    return [
        import_string(stat)() if isinstance(stat, str) else stat()
        for stat in settings.CASTELLUM_SUBJECT_STATS
    ]


@cached_function(timeout=600)
def get_subject_statistics():
    return render_statistics(
        Subject.objects.filter(filter_queries.has_consent())
    )


@method_decorator(sensitive_post_parameters(), 'dispatch')
class SubjectSearchView(LoginRequiredMixin, FormView):
    template_name = 'subjects/subject_search.html'
    form_class = SearchForm

    @cached_property
    def subjectcreationrequest(self):
        if 'from-request' in self.request.GET:
            pk = self.request.GET['from-request']
            return get_object_or_404(
                SubjectCreationRequest, data_is_deleted=False, pk=pk
            )

    def get_matches(self, query):
        user = self.request.user
        contacts = Contact.objects.search(query)
        can_view_subject = user.has_perm('subjects.view_subject')
        for subject in Subject.objects.filter(filter_queries.uuid_filter(contacts)):
            has_privacy_level = user.has_privacy_level(subject.privacy_level)
            participations = []
            for participation in subject.participation_set.filter(
                study__status=Study.EXECUTION
            ):
                can_access_study = user.has_perm(
                    'studies.access_study', obj=participation.study
                )
                invited = participation.status in Participation.INVITED_SET
                can_recruit = (
                    has_privacy_level
                    and can_access_study
                    and user.has_perm('recruitment.recruit', obj=participation.study)
                )
                can_conduct = (
                    has_privacy_level
                    and can_access_study
                    and invited
                    and user.has_perm(
                        'recruitment.conduct_study', obj=participation.study
                    )
                )
                if can_recruit or can_conduct:
                    participations.append((participation, can_recruit, can_conduct))
            if participations or can_view_subject:
                yield subject, subject.contact, participations, has_privacy_level

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['count_total'] = Contact.objects.count()
        context['stats'] = get_subject_stats()
        context['statistics'] = get_subject_statistics()
        context['subjectcreationrequest'] = self.subjectcreationrequest

        form = kwargs.get('form')
        if form and form.is_valid():
            context['matches'] = list(self.get_matches(form.cleaned_data['search']))

            if 'privacy_level_form' not in context:
                context['privacy_level_form'] = SubjectPrivacyLevelForm(
                    user=self.request.user
                )
        return context

    def form_valid(self, form):
        if settings.CASTELLUM_MONITORING_INCLUDE_SEARCH:
            audit(
                gettext_noop('subject searched'),
                self.request.user.username,
                extra={'query': form.cleaned_data['search']},
            )

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if 'privacy_level' not in request.POST:
            return super().post(request, *args, **kwargs)

        if not request.user.has_perm('subjects.change_subject'):
            raise PermissionDenied

        form = SearchForm(data=request.POST)
        privacy_level_form = SubjectPrivacyLevelForm(
            user=self.request.user, data=request.POST
        )

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

                audit(
                    gettext_noop('subject created'),
                    self.request.user.username,
                    subject_pk=subject.pk,
                )
                return redirect('subjects:detail', pk=subject.pk)
            else:
                messages.error(request, _(
                    'Both first and last name must be provided in order to '
                    'create a subject!'
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
            subject = get_subject(
                form.cleaned_data['domain'], form.cleaned_data['pseudonym']
            )
            audit(
                gettext_noop('pseudonym resolved'),
                self.request.user.username,
                extra={'domain': form.cleaned_data['domain']},
            )
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

        dropout_count = self.object.participation_set.filter(status__in=[
            Participation.PARTICIPATING_DROPPED_OUT,
            Participation.EXCLUDED_DROPPED_OUT,
        ]).count()
        dropout_total = self.object.participation_set.filter(status__in=[
            *Participation.INVITED_SET,
            Participation.PARTICIPATING_DROPPED_OUT,
            Participation.EXCLUDED_DROPPED_OUT,
        ]).count()
        if dropout_total == 0:
            context['dropout_rate'] = '—'
        else:
            context['dropout_rate'] = f'{dropout_count / dropout_total:.0%}'

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
    def has_permission(self):
        return (
            self.request.user.has_perm('subjects.export_subject')
            or self.request.user.has_perm('subjects.delete_subject')
        )

    def get(self, request, *args, **kwargs):
        domain = get_object_or_404(Domain, key=kwargs['domain'], object_id=None)
        pseudonym = get_pseudonym_if_exists(self.subject, domain.key)

        audit(
            gettext_noop('pseudonym accessed'),
            self.request.user.username,
            extra={'domain': domain.key},
        )

        return HttpResponse(pseudonym or '—')


class SubjectDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    permission_required = 'subjects.delete_subject'
    form_class = SubjectDeleteForm
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

    def form_valid(self, form):
        if self.object.participation_set.exists():
            return self.get(self.request, **self.kwargs)
        if form.cleaned_data['create_block_hash']:
            if self.object.contact.date_of_birth:
                year_of_birth = self.object.contact.date_of_birth.year
            else:
                year_of_birth = None
            BlockHash.block(
                self.object.contact.first_name,
                self.object.contact.last_name,
                year_of_birth,
            )
        response = super().form_valid(form)
        audit_extra = {}
        if self.object.to_be_deleted:
            audit_extra['to_be_deleted'] = self.object.to_be_deleted.isoformat()
        audit(
            gettext_noop('subject deleted'),
            self.request.user.username,
            subject_pk=self.object.pk,
            extra=audit_extra,
        )
        messages.success(self.request, _('Subject has been deleted.'))
        return response


class SubjectMergeView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    form_class = SubjectMergeForm
    template_name = 'subjects/subject_merge.html'
    permission_required = 'subjects.delete_subject'
    tab = 'merge'

    def get_conflicting_studies(self, target):
        return (
            Study.objects
            .filter(participation__subject=self.object)
            .filter(participation__subject=target)
        )

    def get_conflicting_domains(self, target):
        return (
            Domain.objects
            .filter(pseudonym__subject=self.object)
            .filter(pseudonym__subject=target)
        )

    def merge_reliability_entries_into(self, target):
        studies = target.reliabilityentry_set.values('study')
        for source_entry in self.object.reliabilityentry_set.filter(study__in=studies):
            target_entry = target.reliabilityentry_set.get(study=source_entry.study_id)
            if target_entry.was_reliable and not source_entry.was_reliable:
                target_entry.delete()
            else:
                source_entry.delete()
        self.object.reliabilityentry_set.update(subject=target)

    def move_file(self, name, target):
        # Actually copy to avoid data loss on errors.
        # `cleanup_media` will take care of deleting orphans.
        if not name:
            return name
        dst_name = name.replace(f'subjects/{self.subject.pk}', f'subjects/{target.pk}')
        with default_storage.open(name) as fh:
            return default_storage.save(dst_name, fh)

    def merge_consent_into(self, target):
        if not hasattr(self.object, 'consent'):
            return
        if hasattr(target, 'consent'):
            if self.object.consent.updated_at > target.consent.updated_at:
                target.consent.delete()
            else:
                return
        consent = Consent.objects.get(pk=self.object.consent.pk)
        name = self.move_file(consent.file.name, target)
        Consent.objects.filter(pk=self.object.consent.pk).update(
            subject=target, file=name
        )

    def merge_into(self, target):
        with transaction.atomic():
            self.merge_reliability_entries_into(target)
            self.merge_consent_into(target)
            self.object.participation_set.update(subject=target)
            self.object.pseudonym_set.update(subject=target)
            self.object.exportanswer_set.update(subject=target)
            for revision in self.object.consentrevision_set.all():
                name = self.move_file(revision.file.name, target)
                revision.file.name = name
                revision.save(update_fields=['file'])
            self.object.consentrevision_set.update(subject=target)
            self.object.report_set.update(subject=target)
            self.object.delete()

    def form_valid(self, form):
        if form.cleaned_data['target'] == self.object.pk:
            form.add_error('target', _('Cannot merge subject into itself'))
            return self.form_invalid(form)

        target = get_object_or_404(Subject, pk=form.cleaned_data['target'])

        conflicting_studies = self.get_conflicting_studies(target)
        conflicting_domains = self.get_conflicting_domains(target)
        if conflicting_studies or conflicting_domains:
            return self.render_to_response(self.get_context_data(
                form=form,
                target=target,
                conflicting_studies=conflicting_studies,
                conflicting_domains=conflicting_domains,
            ))

        self.merge_into(target)
        audit(
            gettext_noop('subject merged'),
            self.request.user.username,
            subject_pk=self.object.pk,
            extra={'target': str(target.pk)},
        )
        messages.success(self.request, _('Subject has been deleted.'))
        return redirect('subjects:detail', target.pk)


class SubjectExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'subjects/subject_export.html'
    permission_required = 'subjects.export_subject'
    tab = 'export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.export_requested:
            context['has_participations'] = self.object.participation_set.exists()
            context['general_domains_exist'] = (
                Domain.objects.filter(object_id=None).exists()
            )
            context['appointments'] = (
                Appointment.objects.filter(participation__subject=self.object)
            )

            context['attributes'] = []
            for attribute in Attribute.objects.all():
                value = self.object.attributes.get(attribute.json_key)
                context['attributes'].append((
                    attribute.label, attribute.field.get_display(value)
                ))

            audit(
                gettext_noop('subject exported'),
                self.request.user.username,
                subject_pk=self.object.pk,
            )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.export_requested:
            self.object.export_requested = None
            ExportAnswer.objects.create(
                subject=self.object, created_by=request.user.username
            )
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


class AttributesUpdateView(SubjectUpdateMixin, BaseAttributesUpdateView):
    tab = 'attributes'

    def get_contact_url(self):
        return reverse(
            'subjects:contact', args=[self.subject.pk]
        )


class RelationCreateView(SubjectMixin, BaseRelationCreateView):
    tab = 'attributes'
    base_template = 'subjects/subject_base.html'

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['subject_uuid'])

    def get_success_url(self):
        return reverse(
            'subjects:attributes', args=[self.subject.pk]
        )


class RelationDeleteView(SubjectMixin, BaseRelationDeleteView):
    tab = 'attributes'
    base_template = 'subjects/subject_base.html'

    def get_subject(self):
        return get_object_or_404(Subject, pk=self.kwargs['subject_uuid'])

    def get_success_url(self):
        return reverse(
            'subjects:attributes', args=[self.subject.pk]
        )


class DeleteRecruitmentDataView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/confirm_delete_recruitment_data.html'
    tab = 'attributes'

    def post(self, request, *args, **kwargs):
        delete_recruitment_data(self.subject)
        audit(
            gettext_noop('subject updated'),
            request.user.username,
            subject_pk=self.subject.pk,
        )
        return redirect('subjects:attributes', pk=self.subject.pk)


class SubjectAuditTrailView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = AuditEvent
    permission_required = ['subjects.view_audit_trail']
    template_name = 'subjects/subject_audit_trail.html'
    tab = 'audit-trail'
    paginate_by = 20

    def get_queryset(self):
        audit(
            gettext_noop('audit trail accessed'),
            self.request.user.username,
            subject_pk=self.subject.pk,
        )
        return (
            super().get_queryset()
            .filter(subject_pk=self.subject.pk)
            .values('created_at__date', 'action', 'username')
            .annotate(created_at=models.Max('created_at'), count=models.Count('id'))
            .order_by('-created_at')
        )


class ReportView(SubjectMixin, BaseReportView):
    permission_required = ['subjects.view_subject']
    base_template = 'subjects/subject_base.html'

    def get_success_url(self):
        return reverse('subjects:detail', args=[self.subject.pk])


class ReportDetailView(PermissionRequiredMixin, DetailView):
    model = Report
    permission_required = ['subjects.view_report']

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.POST.get('submit') == 'block':
            messages.success(request, _('Subject remains blocked.'))
        elif request.POST.get('submit') == 'discard':
            obj.subject.blocked = False
            obj.subject.save()
            messages.success(request, _(
                'Report has been discarded. The subject has been un-blocked.'
            ))
        obj.delete()
        return redirect('index')


@method_decorator(sensitive_post_parameters(), 'dispatch')
class SubjectSearchPopup(PermissionRequiredMixin, SubjectSearchView):
    template_name = 'subjects/subject_search_popup.html'
    permission_required = 'subjects.view_subject'
    nochrome = True

    def get_matches(self, query):
        contacts = Contact.objects.search(query)
        return Subject.objects.filter(filter_queries.uuid_filter(contacts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid() and 'contact_form' not in context:
            context['contact_form'] = ContactForm(
                user=self.request.user, initial=form.cleaned_data
            )
        return context

    def post(self, request, *args, **kwargs):
        if 'privacy_level' not in request.POST:
            return super().post(request, *args, **kwargs)

        if not request.user.has_perm('subjects.change_subject'):
            raise PermissionDenied

        form = SearchForm(data=request.POST)
        privacy_level_form = SubjectPrivacyLevelForm(
            user=self.request.user, data=request.POST
        )
        contact_form = ContactForm(user=self.request.user, data=request.POST)

        if (
            form.is_valid()
            and privacy_level_form.is_valid()
            and contact_form.is_valid()
        ):
            contact = contact_form.save()
            contact.subject.privacy_level = (
                privacy_level_form.cleaned_data['privacy_level']
            )
            contact.subject.save()

            audit(
                gettext_noop('subject created'),
                self.request.user.username,
                subject_pk=contact.subject.pk,
            )
            return TemplateResponse(
                self.request,
                'subjects/subject_search_popup_success.html',
                {
                    'name': contact.full_name,
                    'uuid': contact.subject.pk,
                },
            )
        return self.render_to_response(self.get_context_data(
            form=form,
            privacy_level_form=privacy_level_form,
            contact_form=contact_form,
        ))


class SubjectProtectedMediaView(
    SubjectMixin, PermissionRequiredMixin, BaseProtectedMediaView
):
    permission_required = ['subjects.view_subject']

    def get_path(self):
        return f'subjects/{self.subject.pk}/{self.kwargs["path"]}'
