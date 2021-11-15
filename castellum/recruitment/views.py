# (c) 2018-2021
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
import random
from collections import defaultdict

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from simplecharts import StackedColumnRenderer
from stronghold.decorators import public

from castellum.appointments.forms import appointment_is_available
from castellum.appointments.mixins import BaseAppointmentsUpdateView
from castellum.appointments.mixins import BaseCalendarView
from castellum.appointments.mixins import get_external_resource_events
from castellum.appointments.mixins import send_appointment_notifications
from castellum.appointments.models import Appointment
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.pseudonyms.helpers import get_subject
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Resource
from castellum.studies.models import Study
from castellum.studies.models import StudySession
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.subjects.mixins import SubjectMixin
from castellum.subjects.models import Subject
from castellum.utils import scheduler
from castellum.utils.mail import MailContext

from . import filter_queries
from .forms import ContactForm
from .mixins import BaseAttributesUpdateView
from .mixins import BaseMailRecruitmentView
from .mixins import ParticipationMixin
from .mixins import get_recruitable
from .models import MailBatch
from .models import Participation
from .models.attributes import get_description_by_statistics_rank
from .templatetags.recruitment import study_legal_representative_hash

FULLCALENDAR_DEFAULT_COLOR = '#3788d8'

logger = logging.getLogger(__name__)


class RecruitmentView(StudyMixin, PermissionRequiredMixin, ListView):
    model = Participation
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    shown_status = []
    tab = 'recruitment'

    def dispatch(self, request, *args, **kwargs):
        self.sort = self.request.GET.get('sort', self.request.session.get('recruitment_sort'))
        self.request.session['recruitment_sort'] = self.sort
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.sort == 'followup':
            order_by = ['followup_date', 'followup_time', '-updated_at']
        elif self.sort == 'last_contact_attempt':
            order_by = ['-status_not_reached', '-updated_at']
        elif self.sort == 'statistics':
            desc1 = get_description_by_statistics_rank('primary')
            desc2 = get_description_by_statistics_rank('secondary')
            order_by = [
                '-subject__attributes__' + desc1.json_key,
                '-subject__attributes__' + desc2.json_key,
                '-updated_at',
            ]
        else:
            order_by = [
                '-followup_urgent', 'status', 'followup_date', 'followup_time', '-updated_at'
            ]

        return Participation.objects\
            .with_appointment_count()\
            .prefetch_related('subject')\
            .filter(status__in=self.shown_status, study=self.study)\
            .order_by(*order_by)

    def _get_statistics(self):
        participations = Participation.objects.filter(
            study=self.study, status=Participation.INVITED
        ).prefetch_related('subject')

        desc1 = get_description_by_statistics_rank('primary')
        if desc1:
            buckets1, get_bucket1 = desc1.field.get_statistics_grouping(self.study)
        else:
            return None

        desc2 = get_description_by_statistics_rank('secondary')
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

        desc1 = get_description_by_statistics_rank('primary')
        desc2 = get_description_by_statistics_rank('secondary')
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
                participation.status_open
                and participation.last_contacted_elsewhere
                and participation.last_contacted_elsewhere.date() > last_agreeable_contact_time
            )

            participations.append((participation, buckets, can_access, recently_contacted))
        context['participations'] = participations

        context['sort_options'] = [
            ('relevance', _('Relevance')),
            ('followup', _('Follow-up date')),
            ('last_contact_attempt', _('Last contact attempt')),
            ('statistics', _('Statistics')),
        ]
        sort_options = dict(context['sort_options'])
        context['sort_label'] = sort_options.get(self.sort, _('Relevance'))

        context['statistics'] = self.get_statistics()

        queryset = Participation.objects.filter(study=self.study)
        context['all_count'] = queryset.count()
        context['invited_count'] = queryset.filter(
            status=Participation.INVITED
        ).count()
        context['unsuitable_count'] = queryset.filter(
            status=Participation.UNSUITABLE
        ).count()
        context['open_count'] = queryset.filter(status__in=[
            Participation.NOT_CONTACTED,
            Participation.NOT_REACHED,
            Participation.FOLLOWUP_APPOINTED,
            Participation.AWAITING_RESPONSE,
        ]).count()

        context['session_count'] = self.study.studysession_set.count()

        return context


class RecruitmentViewInvited(RecruitmentView):
    shown_status = [Participation.INVITED]
    subtab = 'invited'


class RecruitmentViewUnsuitable(RecruitmentView):
    shown_status = [Participation.UNSUITABLE]
    subtab = 'unsuitable'


class RecruitmentViewOpen(RecruitmentView):
    shown_status = [
        Participation.NOT_CONTACTED,
        Participation.NOT_REACHED,
        Participation.FOLLOWUP_APPOINTED,
        Participation.AWAITING_RESPONSE,
    ]
    subtab = 'open'

    def create_participations(self, batch_size):
        subjects = get_recruitable(self.study)

        added = min(batch_size, len(subjects))
        participations = []
        for subject in random.sample(subjects, k=added):
            participations.append(Participation(study=self.study, subject=subject))

        return participations

    def post(self, request, *args, **kwargs):
        if self.study.min_subject_count == 0:
            messages.error(request, _(
                'This study does not require participants. '
                'Please, contact the responsible person who can set it up.'
            ))
            return self.get(request, *args, **kwargs)

        not_contacted_count = self.get_queryset()\
            .filter(status=Participation.NOT_CONTACTED).count()
        hard_limit = self.study.min_subject_count * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR

        if not_contacted_count >= hard_limit:
            messages.error(request, _(
                'Application privacy does not allow you to add more subjects. '
                'Please contact provided subjects before adding new ones.'
            ))
            return self.get(request, *args, **kwargs)

        # Silently trim down to respect hard limit.
        # In many cases, the soft limit warning will already be shown in that case.
        batch_size = min(
            settings.CASTELLUM_RECRUITMENT_BATCH_SIZE,
            hard_limit - not_contacted_count,
        )
        try:
            participations = self.create_participations(batch_size)
            Participation.objects.bulk_create(participations)
        except KeyError:
            participations = []
            messages.error(request, _(
                'The custom filter that is set for this study does not exist.'
            ))

        if not_contacted_count + len(participations) > settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT:
            messages.error(request, _(
                'Such workflow is not intended due to privacy reasons. '
                'Please contact provided subjects before adding new ones.'
            ))

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


class MailRecruitmentView(BaseMailRecruitmentView):
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    participation_status = Participation.AWAITING_RESPONSE
    tab = 'mail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batches'] = list(
            self.study.mailbatch_set
            .order_by('datetime')
            .annotate(
                no_response_size=models.Count('participation', distinct=True),
            )
        )
        return context

    def form_valid(self, form):
        self._form_valid(form)
        return redirect('recruitment:mail', self.study.pk)


class MailRecruitmentRemindView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = MailBatch
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]
    template_name = 'recruitment/mail_remind.html'

    def get_object(self):
        return get_object_or_404(MailBatch, pk=self.kwargs['pk'], study=self.study, reminded=None)

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
            pks = []
            for participation in batch.participation_set.select_related('subject'):
                contact = participation.subject.contact
                success = self.send_reminder_mail(contact, ctx)
                if success:
                    pks.append(participation.pk)
            Participation.objects.filter(pk__in=pks).update(updated_at=timezone.now())

    def post(self, request, *args, **kwargs):
        batch = self.get_object()
        self.send_reminder_mails(batch)
        batch.reminded = timezone.now()
        batch.save()
        # should conform with BaseMailRecruitmentView
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
        self.object.participation_set.update(
            status=Participation.UNSUITABLE,
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
        if not self.object.match:
            initial['status'] = Participation.UNSUITABLE
            initial['followup_date'] = None
            initial['followup_time'] = None
        return initial

    def get_object(self):
        return self.participation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(Participation.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        context['sessions'] = self.study.studysession_set.order_by('pk')

        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        scheduler_appointments_exist = Appointment.objects.filter(
            participation=self.object,
            session__schedule_id__isnull=False,
        ).exists()

        form.instance.batch = None
        if form.instance.status == Participation.INVITED:
            form.instance.dropped_out = False
        response = super().form_valid(form)
        messages.success(self.request, _('Data has been saved.'))
        if self.object.status != Participation.INVITED and scheduler_appointments_exist:
            messages.warning(self.request, _(
                'Scheduler appointments for this participation have been deleted.'
            ))
        return response


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

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        qs = self.study.participation_set.exclude(status__in=[
            Participation.INVITED,
            Participation.UNSUITABLE,
        ])

        if action == 'all':
            pass
        elif action == 'mismatch':
            qs = qs.exclude(subject__in=Subject.objects.filter(
                filter_queries.study(self.study, include_unknown=False),
            ))
        elif action == 'awaiting_response':
            qs = qs.filter(
                status=Participation.AWAITING_RESPONSE,
                updated_at__lt=timezone.now() - datetime.timedelta(days=10),
            )
        else:
            return HttpResponseBadRequest()

        qs.update(status=Participation.UNSUITABLE, batch=None, excluded_by_cleanup=True)

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


class AdditionalInfoUpdateView(RecruitmentUpdateMixin, BaseAdditionalInfoUpdateView):
    subtab = 'additional-info'

    def get_object(self):
        return self.participation.subject


class LegalRepresentativeContactUpdateView(StudyMixin, SubjectMixin, BaseContactUpdateView):
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

        for legal_representative in participation.subject.contact.legal_representatives.all():
            h = study_legal_representative_hash(self.study, legal_representative.subject)
            if h == self.kwargs['hash']:
                return legal_representative

        raise Http404


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
        for resource in Resource.objects.filter(studysession__study=self.study).exclude(url=''):
            context['legend'].append((resource.color, resource.name))
        if context['legend']:
            context['legend'].insert(0, (FULLCALENDAR_DEFAULT_COLOR, self.study.name))
        return context

    def get_events(self):
        events = super().get_events()
        start = datetime.datetime.fromisoformat(self.request.GET['start'])
        end = datetime.datetime.fromisoformat(self.request.GET['end'])
        for resource in (
            Resource.objects
            .filter(studysession__study=self.study)
            .exclude(url='')
            .distinct()
        ):
            events += get_external_resource_events(resource, start, end)
        return events


@method_decorator(public, 'dispatch')
@method_decorator(csrf_exempt, 'dispatch')
class SchedulerPingView(View):
    def post(self, request, *args, **kwargs):
        session = get_object_or_404(StudySession, schedule_id=self.kwargs['schedule_id'])
        try:
            subject = get_subject(session.domain, self.kwargs['pseudonym'])
        except ObjectDoesNotExist:
            raise Http404
        participation = get_object_or_404(Participation, subject=subject, study=session.study)
        appointments = Appointment.objects.filter(participation=participation, session=session)

        start = scheduler.get(self.kwargs['schedule_id'], self.kwargs['pseudonym'])

        if not appointment_is_available(session, start, appointments):
            raise forms.ValidationError

        appointment = appointments.first()
        appointment_changes = []

        if appointment:
            if not start:
                appointment_changes.append((appointment.start, None))
                appointment.delete()
            elif start != appointment.start:
                appointment_changes.append((appointment.start, start))
                appointment.start = start
                appointment.reminded = False
                appointment.save()
        elif start:
            appointment_changes.append((None, start))
            participation.appointment_set.create(
                session=session,
                start=start,
            )

        send_appointment_notifications(request, participation, appointment_changes)

        return HttpResponse(status=204)
