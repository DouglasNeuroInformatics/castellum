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
import random
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import Http404
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from simplecharts import StackedColumnRenderer

from castellum.appointments.helpers import get_external_resource_events
from castellum.appointments.mixins import BaseAppointmentsUpdateView
from castellum.appointments.mixins import BaseCalendarView
from castellum.appointments.models import Appointment
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.studies.mixins import StudyMixin
from castellum.studies.mixins import with_study_lock
from castellum.studies.models import Resource
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseConsentChangeView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.subjects.mixins import BaseReportView
from castellum.subjects.mixins import SubjectMixin
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext
from castellum.utils.views import BaseProtectedMediaView

from . import filter_queries
from .forms import ContactForm
from .forms import SendMailForm
from .mixins import BaseAttributesUpdateView
from .mixins import ParticipationMixin
from .mixins import get_recruitable
from .models import MailBatch
from .models import Participation
from .models.attributes import get_attribute_by_statistics_rank
from .templatetags.recruitment import study_legal_representative_hash

FULLCALENDAR_DEFAULT_COLOR = '#3788d8'

logger = logging.getLogger(__name__)
monitoring_logger = logging.getLogger('monitoring.recruitment')


class RecruitmentView(StudyMixin, PermissionRequiredMixin, ListView):
    model = Participation
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    shown_status = []
    tab = 'recruitment'

    def dispatch(self, request, *args, **kwargs):
        self.sort = self.request.GET.get(
            'sort', self.request.session.get('recruitment_sort')
        )
        self.request.session['recruitment_sort'] = self.sort
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.sort == 'followup':
            order_by = ['followup_date', 'followup_time', '-updated_at']
        elif self.sort == 'privacy-level':
            order_by = ['subject__privacy_level', '-updated_at']
        elif self.sort == 'last_contact_attempt':
            order_by = ['-status_not_reached', '-updated_at']
        elif self.sort == 'statistics':
            desc1 = get_attribute_by_statistics_rank('primary')
            desc2 = get_attribute_by_statistics_rank('secondary')
            order_by = [
                f'-subject__attributes__{desc1.json_key}',
                f'-subject__attributes__{desc2.json_key}',
                '-updated_at',
            ]
        elif self.sort == 'recently-active':
            order_by = ['-recent_participation_count', '-updated_at']
        elif self.sort == 'assigned-to-me':
            order_by = ['-assigned_to_me', '-updated_at']
        else:
            order_by = [
                '-followup_urgent',
                'status',
                'followup_date',
                'followup_time',
                '-updated_at',
            ]

        return (
            Participation.objects
            .with_sort_properties()
            .with_appointment_count()
            .with_assigned_to_me(self.request.user)
            .prefetch_related('subject')
            .filter(status__in=self.shown_status, study=self.study)
            .order_by(*order_by)
        )

    def _get_statistics(self):
        participations = Participation.objects.filter(
            study=self.study, status__in=Participation.INVITED_SET
        ).prefetch_related('subject')

        desc1 = get_attribute_by_statistics_rank('primary')
        if desc1:
            buckets1, get_bucket1 = desc1.field.get_statistics_grouping(self.study)
        else:
            return None

        desc2 = get_attribute_by_statistics_rank('secondary')
        if desc2:
            buckets2, get_bucket2 = desc2.field.get_statistics_grouping(self.study)
        else:
            buckets2, get_bucket2 = [(None, None)], lambda x: None

        statistics = defaultdict(lambda: defaultdict(lambda: 0))
        for participation in participations:
            subject = participation.subject

            value1 = subject.attributes.get(desc1.json_key)
            key1 = get_bucket1(value1)

            if desc2:
                value2 = subject.attributes.get(desc2.json_key)
                key2 = get_bucket2(value2)
            else:
                key2 = None

            statistics[key1][key2] += 1

        data = {
            'rows': [{
                'label': str(label1),
                'values': [statistics[key1][key2] for key2, label2 in buckets2]
            } for key1, label1 in buckets1],
        }

        if len(buckets2) > 1:
            data['legend'] = [str(label2) for key2, label2 in buckets2]

        return data

    def get_statistics(self):
        data = self._get_statistics()
        if not data:
            return None
        renderer = StackedColumnRenderer(width=760, height=320)
        return renderer.render(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        desc1 = get_attribute_by_statistics_rank('primary')
        desc2 = get_attribute_by_statistics_rank('secondary')
        if desc1:
            buckets1, get_bucket1 = desc1.field.get_statistics_grouping(self.study)
            buckets1 = dict(buckets1)
        if desc2:
            buckets2, get_bucket2 = desc2.field.get_statistics_grouping(self.study)
            buckets2 = dict(buckets2)

        last_agreeable_contact_time = (
            datetime.date.today() - settings.CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS
        )

        participations = []
        for participation in self.get_queryset():
            subject = participation.subject
            buckets = []
            if desc1:
                value1 = subject.attributes.get(desc1.json_key)
                buckets.append((desc1, buckets1[get_bucket1(value1)]))
            if desc2:
                value2 = subject.attributes.get(desc2.json_key)
                buckets.append((desc2, buckets2[get_bucket2(value2)]))

            can_access = self.request.user.has_privacy_level(
                participation.subject.privacy_level
            )

            recently_contacted = (
                participation.status in Participation.RECRUITMENT_SET
                and participation.last_contacted_elsewhere
                and (
                    participation.last_contacted_elsewhere.date()
                    > last_agreeable_contact_time
                )
            )

            participations.append(
                (participation, buckets, can_access, recently_contacted)
            )
        context['participations'] = participations

        context['sort_options'] = [
            ('relevance', _('Relevance')),
            ('followup', _('Follow-up date')),
            ('last_contact_attempt', _('Last contact attempt')),
            ('statistics', _('Statistics')),
            ('recently-active', _('Recently active')),
            ('assigned-to-me', _('Assigned to me')),
            ('privacy-level', _('Privacy level')),
        ]
        sort_options = dict(context['sort_options'])
        context['sort_label'] = sort_options.get(self.sort, _('Relevance'))

        context['statistics'] = self.get_statistics()

        queryset = Participation.objects.filter(study=self.study)
        context['all_count'] = queryset.count()
        context['invited_count'] = (
            queryset.filter(status__in=Participation.INVITED_SET).count()
        )
        context['excluded_count'] = (
            queryset.filter(status__in=Participation.EXCLUDED_SET).count()
        )
        context['open_count'] = queryset.filter(status__in=[
            Participation.NOT_CONTACTED,
            Participation.NOT_REACHED,
            Participation.FOLLOWUP_APPOINTED,
            Participation.AWAITING_RESPONSE,
        ]).count()

        context['session_count'] = self.study.studysession_set.count()

        return context


class RecruitmentViewInvited(RecruitmentView):
    shown_status = Participation.INVITED_SET
    subtab = 'invited'


class RecruitmentViewExcluded(RecruitmentView):
    shown_status = Participation.EXCLUDED_SET
    subtab = 'excluded'


class RecruitmentViewOpen(RecruitmentView):
    shown_status = Participation.RECRUITMENT_SET
    subtab = 'open'

    def create_participations(self, batch_size, is_urgent=False):
        subjects = get_recruitable(self.study, is_urgent)

        added = min(batch_size, len(subjects))
        participations = []
        for subject in random.sample(subjects, k=added):
            participations.append(Participation(study=self.study, subject=subject))

        return participations

    @with_study_lock
    def post(self, request, *args, **kwargs):
        is_urgent = request.POST.get('submit') == 'urgent'

        if is_urgent:
            monitoring_logger.info('Urgent recruitment in study {} by {}'.format(
                self.study.pk, request.user.pk
            ))

        if self.study.min_subject_count == 0:
            messages.error(request, _(
                'This study does not require participants. '
                'Please, contact the responsible person who can set it up.'
            ))
            return self.get(request, *args, **kwargs)

        not_contacted_count = (
            self.get_queryset().filter(status=Participation.NOT_CONTACTED).count()
        )
        hard_limit = (
            self.study.min_subject_count
            * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
        )

        if not_contacted_count >= hard_limit:
            messages.error(request, _(
                'Application privacy does not allow you to add more subjects. '
                'Please contact provided subjects before adding new ones.'
            ))
            return self.get(request, *args, **kwargs)

        # Silently trim down to respect hard limit.
        batch_size = min(
            settings.CASTELLUM_RECRUITMENT_BATCH_SIZE,
            hard_limit - not_contacted_count,
        )
        participations = self.create_participations(batch_size, is_urgent)
        Participation.objects.bulk_create(participations)

        if not participations:
            messages.error(
                self.request,
                _('No potential participants could be found for this study.'),
            )
        elif len(participations) < batch_size:
            messages.warning(
                self.request,
                _(
                    'Only {added} out of {batchsize} potential participants '
                    'could be found for this study. These have been added.'
                ).format(added=len(participations), batchsize=batch_size),
            )

        return self.get(request, *args, **kwargs)


class MailRecruitmentView(StudyMixin, PermissionRequiredMixin, FormView):
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    template_name = 'recruitment/mail.html'
    tab = 'mail'
    form_class = SendMailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batches'] = list(
            self.study.mailbatch_set
            .order_by('datetime')
            .annotate(
                # PERF: not exactly the same as no_response_set.count(), but much faster
                no_response_size=models.Count('participation', distinct=True),
            )
        )
        return context

    def personalize_mail_body(self, mail_body, contact):
        return mail_body.replace('{name}', contact.full_name)

    def create_participations(self, batch_size):
        subjects = get_recruitable(self.study)

        participations = []
        with MailContext('recruitment') as ctx:
            while len(participations) < batch_size and subjects:
                pick = subjects.pop(random.randrange(0, len(subjects)))
                try:
                    success = ctx.send_separate_mails(
                        self.study.mail_subject,
                        self.personalize_mail_body(self.study.mail_body, pick.contact),
                        pick.contact.own_or_legal_representative_emails,
                        reply_to=[self.study.email],
                        recipients_string=pick.contact.email_recipients_string,
                    )
                except Exception:
                    logger.exception('failed to send mail')
                    break
                if success:
                    participations.append(Participation(
                        study=self.study,
                        subject=pick,
                        status=Participation.AWAITING_RESPONSE,
                        attempts=1,
                    ))

        return participations

    def send_confirmation_mail(self, counter):
        with MailContext('internal') as ctx:
            ctx.send_mail(
                self.study.mail_subject,
                f'{counter} emails have been sent.\n\n---\n\n{self.study.mail_body}',
                [self.study.email],
            )

    def get_weekly_mails(self):
        # 6 instead of 7 days so that people can send mails e.g. every monday
        result = (
            self.study.mailbatch_set
            .filter(datetime__gt=timezone.now() - datetime.timedelta(days=6))
            .aggregate(models.Sum('contacted_size'))
        )
        return result['contacted_size__sum'] or 0

    @with_study_lock
    def form_valid(self, form):
        batch_size = form.cleaned_data['batch_size']
        allowed_size = min(
            batch_size,
            settings.CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT - self.get_weekly_mails(),
        )

        participations = self.create_participations(allowed_size)

        if allowed_size <= 0:
            messages.error(self.request, _(
                'You have reached the weekly limit for mail recruitment.'
            ))
        elif not participations:
            messages.error(
                self.request,
                _(
                    'No potential participants with email addresses could be found for '
                    'this study.'
                ),
            )
        elif len(participations) < batch_size:
            messages.warning(
                self.request,
                _(
                    'Only {added} out of {batchsize} potential participants with '
                    'email addresses could be found for this study. These have been '
                    'contacted.'
                ).format(added=len(participations), batchsize=batch_size),
            )
        else:
            messages.success(self.request, _('Emails sent successfully!'))

        if participations:
            batch = MailBatch.objects.create(
                study=self.study,
                contacted_size=len(participations),
            )
            for p in participations:
                p.batch = batch
            Participation.objects.bulk_create(participations)
            self.send_confirmation_mail(len(participations))

        return redirect('recruitment:mail', self.study.pk)


class MailRecruitmentRemindView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = MailBatch
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    template_name = 'recruitment/mail_remind.html'

    def get_object(self):
        return get_object_or_404(
            MailBatch, pk=self.kwargs['pk'], study=self.study, reminded=None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mail_subject'] = (
            settings.CASTELLUM_REMINDER_MAIL_SUBJECT_TEMPLATE.format(
                mail_subject=self.study.mail_subject
            )
        )
        return context

    def send_reminder_mail(self, contact, ctx):
        return ctx.send_separate_mails(
            settings.CASTELLUM_REMINDER_MAIL_SUBJECT_TEMPLATE.format(
                mail_subject=self.study.mail_subject
            ),
            self.study.mail_body.replace('{name}', contact.full_name),
            contact.own_or_legal_representative_emails,
            reply_to=[self.study.email],
            recipients_string=contact.email_recipients_string,
        )

    def send_reminder_mails(self, batch):
        with MailContext('recruitment') as ctx:
            for participation in batch.no_response_set.select_related('subject'):
                contact = participation.subject.contact
                success = self.send_reminder_mail(contact, ctx)
                if success:
                    # set updated_at
                    participation.save()

    def post(self, request, *args, **kwargs):
        batch = self.get_object()
        self.send_reminder_mails(batch)
        batch.reminded = timezone.now()
        batch.save()
        # should conform with MailRecruitmentView
        messages.success(self.request, _('Emails sent successfully!'))
        return redirect('recruitment:mail', self.study.pk)


class MailRecruitmentCleanupView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = MailBatch
    template_name = 'recruitment/mail_cleanup.html'
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]

    def get_object(self):
        return get_object_or_404(MailBatch, pk=self.kwargs['pk'], study=self.study)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # needs to be update() in order not to set Subject.updated_at
        self.object.participation_set.exclude(
            status=Participation.FOLLOWUP_APPOINTED
        ).update(
            status=Participation.EXCLUDED,
            batch=None,
            excluded_by_cleanup=True,
        )
        return redirect('recruitment:mail', self.study.pk)


class ContactView(ParticipationMixin, PermissionRequiredMixin, UpdateView):
    model = Participation
    form_class = ContactForm
    template_name = 'recruitment/contact.html'
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    tab = 'contact'

    def get_initial(self):
        initial = super().get_initial()
        if not self.object.is_match:
            initial['status'] = Participation.EXCLUDED
            initial['followup_date'] = None
            initial['followup_time'] = None
        return initial

    def get_object(self):
        return self.participation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.study.studysession_set.order_by('pk')
        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        appointments_exist = (
            Appointment.objects
            .filter(participation=self.object)
            .exists()
        )

        form.instance.batch = None
        response = super().form_valid(form)
        messages.success(self.request, _('Data has been saved.'))
        if self.object.status not in Participation.INVITED_SET and appointments_exist:
            messages.warning(self.request, _(
                'Appointments for this participation have been deleted.'
            ))
        return response


class ExcludeView(StudyMixin, PermissionRequiredMixin, TemplateView):
    """Limited ContactView for users with insufficient privacy_level."""

    template_name = 'recruitment/confirm_exclude.html'
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]

    def post(self, request, **kwargs):
        obj = get_object_or_404(Participation, study=self.study, pk=kwargs['pk'])
        obj.status = Participation.EXCLUDED
        obj.save()
        return redirect('recruitment:recruitment-open', self.study.pk)


class AppointmentsUpdateView(BaseAppointmentsUpdateView):
    permission_required = ['recruitment.recruit', 'appointments.change_appointment']
    study_status = [Study.EXECUTION]
    base_template = 'recruitment/participation_base.html'
    tab = 'appointments'


class RecruitmentCleanupView(StudyMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'recruitment.recruit'
    template_name = 'recruitment/cleanup.html'
    study_status = [Study.EXECUTION]
    tab = 'recruitment'

    def get_querysets(self):
        qs = (
            self.study.participation_set
            .filter(status__in=Participation.RECRUITMENT_SET)
            .exclude(status=Participation.FOLLOWUP_APPOINTED)
        )
        return {
            'all': qs,
            'mismatch': qs.exclude(subject__in=Subject.objects.filter(
                filter_queries.study(self.study),
                filter_queries.has_consent(),
            )),
            'awaiting_response': qs.filter(
                status=Participation.AWAITING_RESPONSE,
                updated_at__lt=timezone.now() - datetime.timedelta(days=10),
            ),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querysets'] = self.get_querysets()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        querysets = self.get_querysets()

        if action not in querysets:
            return HttpResponseBadRequest()

        # needs to be update() in order not to set Subject.updated_at
        querysets[action].update(
            status=Participation.EXCLUDED, batch=None, excluded_by_cleanup=True
        )

        return redirect('recruitment:recruitment-open', self.study.pk)


class RecruitmentUpdateMixin(ParticipationMixin):
    study_status = [Study.EXECUTION]
    base_template = 'recruitment/participation_update_base.html'
    tab = 'update-data'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)

    def get_permission_required(self):
        permission_required = {'recruitment.recruit'}
        permission_required.update(super().get_permission_required())
        return permission_required


class ContactUpdateView(RecruitmentUpdateMixin, BaseContactUpdateView):
    subtab = 'contact'
    context = 'recruitment'

    def get_object(self):
        return self.participation.subject.contact


class AttributesUpdateView(RecruitmentUpdateMixin, BaseAttributesUpdateView):
    subtab = 'attributes'

    def get_object(self):
        return self.participation.subject


class DataProtectionUpdateView(RecruitmentUpdateMixin, BaseDataProtectionUpdateView):
    subtab = 'data-protection'

    def get_object(self):
        return self.participation.subject

    def get_subject_media_url(self, path):
        return reverse(
            'recruitment-media', args=[self.study.pk, self.participation.pk, path]
        )


class ConsentChangeView(ParticipationMixin, BaseConsentChangeView):
    study_status = [Study.EXECUTION]
    base_template = 'recruitment/participation_update_base.html'
    tab = 'update-data'
    subtab = 'data-protection'

    def get_permission_required(self):
        permission_required = {'recruitment.recruit'}
        permission_required.update(super().get_permission_required())
        return permission_required

    def get_success_url(self):
        return reverse(
            'recruitment:data-protection-update',
            args=[self.study.pk, self.participation.pk],
        )


class AdditionalInfoUpdateView(RecruitmentUpdateMixin, BaseAdditionalInfoUpdateView):
    subtab = 'additional-info'

    def get_object(self):
        return self.participation.subject


class LegalRepresentativeContactUpdateView(
    StudyMixin, SubjectMixin, BaseContactUpdateView
):
    base_template = 'recruitment/base.html'
    study_status = [Study.EXECUTION]

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)

    def get_permission_required(self):
        permission_required = {'recruitment.recruit'}
        permission_required.update(super().get_permission_required())
        return permission_required

    def get_object(self):
        participation = get_object_or_404(
            Participation, pk=self.kwargs['participation_pk'], study=self.study
        )
        if not self.request.user.has_privacy_level(participation.subject.privacy_level):
            return self.handle_no_permission()

        for legal_representative in (
            participation.subject.contact.legal_representatives.all()
        ):
            h = study_legal_representative_hash(
                self.study, legal_representative.subject
            )
            if h == self.kwargs['hash']:
                return legal_representative

        raise Http404


class ReportView(ParticipationMixin, BaseReportView):
    study_status = [Study.EXECUTION]
    permission_required = 'recruitment.recruit'
    base_template = 'recruitment/participation_base.html'

    def get_success_url(self):
        return reverse(
            'recruitment:contact', args=[self.study.pk, self.participation.pk]
        )


class CalendarView(StudyMixin, PermissionRequiredMixin, BaseCalendarView):
    model = Study
    permission_required = 'appointments.change_appointment'
    study_status = [Study.EXECUTION]
    nochrome = True

    def get_appointments(self):
        return super().get_appointments().filter(session__study=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legend'] = []
        for resource in (
            Resource.objects.filter(studysession__study=self.study).exclude(url='')
        ):
            context['legend'].append((resource.color, resource.name))
        if context['legend']:
            context['legend'].insert(0, (FULLCALENDAR_DEFAULT_COLOR, self.study.name))
        return context

    def get_events(self):
        events = super().get_events()
        for resource in (
            Resource.objects
            .filter(studysession__study=self.study)
            .exclude(url='')
            .distinct()
        ):
            events += get_external_resource_events(
                resource, self.filters['start'], self.filters['end']
            )
        return events


class RecruitmentProtectedMediaView(
    ParticipationMixin, PermissionRequiredMixin, BaseProtectedMediaView
):
    permission_required = ['subjects.view_subject', 'recruitment.recruit']
    study_status = [Study.EXECUTION]

    def get_path(self):
        return f'subjects/{self.kwargs["path"]}'
