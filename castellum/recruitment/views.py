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
import random
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic import UpdateView

from icalendar import Calendar
from simplecharts import StackedColumnRenderer

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.studies.models import StudyTypeEventFeed
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.utils import cached_request

from .forms import ContactForm
from .mixins import BaseAttributeSetUpdateView
from .mixins import BaseCalendarView
from .mixins import BaseMailRecruitmentView
from .mixins import ParticipationMixin
from .mixins import get_recruitable
from .models import AttributeDescription
from .models import AttributeSet
from .models import Participation
from .models.attributesets import get_description_by_statistics_rank

logger = logging.getLogger(__name__)


class RecruitmentView(StudyMixin, PermissionRequiredMixin, ListView):
    model = Participation
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.view_participation'
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
                '-subject__attributeset__data__' + desc1.json_key,
                '-subject__attributeset__data__' + desc2.json_key,
                '-updated_at',
            ]
        else:
            order_by = [
                '-followup_urgent', 'status', 'followup_date', 'followup_time', '-updated_at'
            ]

        return Participation.objects\
            .prefetch_related('subject__attributeset')\
            .filter(status__in=self.shown_status, study=self.study)\
            .order_by(*order_by)

    def get_statistics(self):
        participations = Participation.objects.filter(
            study=self.study, status=Participation.INVITED
        ).prefetch_related('subject__attributeset')

        buckets1 = AttributeDescription.get_statistics_buckets('primary')
        buckets2 = AttributeDescription.get_statistics_buckets('secondary')

        if len(buckets1) == 1:
            return None

        statistics = defaultdict(lambda: defaultdict(lambda: 0))
        for participation in participations:
            try:
                attributeset = participation.subject.attributeset
                key1 = attributeset.get_statistics_bucket('primary')
                key2 = attributeset.get_statistics_bucket('secondary')
                statistics[key1][key2] += 1
            except AttributeSet.DoesNotExist:
                pass

        data = {
            'rows': [{
                'label': str(label1),
                'values': [statistics[key1][key2] for key2, label2 in buckets2]
            } for key1, label1 in buckets1],
        }

        if len(buckets2) > 1:
            data['legend'] = [str(label2) for key2, label2 in buckets2]

        renderer = StackedColumnRenderer(width=760, height=320)
        return renderer.render(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        buckets1 = dict(AttributeDescription.get_statistics_buckets('primary'))
        buckets2 = dict(AttributeDescription.get_statistics_buckets('secondary'))

        participations = []
        for participation in self.get_queryset():
            try:
                attributeset = participation.subject.attributeset
                bucket1 = buckets1[attributeset.get_statistics_bucket('primary')]
                bucket2 = buckets2[attributeset.get_statistics_bucket('secondary')]
                buckets = ', '.join(str(bucket) for bucket in [bucket1, bucket2] if bucket)
            except AttributeSet.DoesNotExist:
                buckets = ''

            can_access = self.request.user.has_privacy_level(
                participation.subject.privacy_level
            )

            participations.append((participation, buckets, can_access))
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

        context['last_agreeable_contact_time'] = (
            datetime.date.today() - settings.CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS
        )

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
        for subject in random.sample(subjects, k=added):
            Participation.objects.create(study=self.study, subject=subject)

        return added

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('recruitment.add_participation', obj=self.study):
            raise PermissionDenied

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
            added = self.create_participations(batch_size)
        except KeyError:
            added = 0
            messages.error(request, _(
                'The custom filter that is set for this study does not exist.'
            ))

        if not_contacted_count + added > settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT:
            messages.error(request, _(
                'Such workflow is not intended due to privacy reasons. '
                'Please contact provided subjects before adding new ones.'
            ))

        if added == 0:
            messages.error(
                self.request,
                _('No potential participants could be found for this study.'),
            )

        elif added < batch_size:
            messages.warning(
                self.request,
                _(
                    'Only {added} out of {batchsize} potential participants '
                    'could be found for this study. These have been added.'
                ).format(added=added, batchsize=batch_size),
            )

        return self.get(request, *args, **kwargs)


class MailRecruitmentView(BaseMailRecruitmentView):
    permission_required = 'recruitment.view_participation'
    study_status = [Study.EXECUTION]
    participation_status = Participation.AWAITING_RESPONSE
    tab = 'mail'

    def form_valid(self, form):
        self._form_valid(form)
        return redirect('recruitment:mail', self.study.pk)


class ContactView(ParticipationMixin, PermissionRequiredMixin, UpdateView):
    model = Participation
    form_class = ContactForm
    template_name = 'recruitment/contact.html'
    permission_required = 'recruitment.change_participation'
    study_status = [Study.EXECUTION]

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

        context['context'] = self.request.GET.get('context')
        context['showup_stats'], context['showup_score'] = self.subject.get_showup_stats()

        return context

    def get_success_url(self):
        context = self.request.GET.get('context')
        if context == 'subjects:participation-list':
            return reverse(context, args=[self.object.subject.pk])
        else:
            return reverse('recruitment:recruitment-open', args=[self.object.study.pk])

    def add_working_days(self, dt, days):
        for i in range(days):
            if dt.isoweekday() == 5:  # friday
                dt += timezone.timedelta(days=3)
            elif dt.isoweekday() == 6:  # saturday
                dt += timezone.timedelta(days=2)
            else:
                dt += timezone.timedelta(days=1)
        return dt

    def send_appointment_notifications(self, changes):
        start = timezone.now()
        end = self.add_working_days(start, 2)
        relevant_changes = [
            (old, new) for (old, new) in changes if (
                (old and old >= start and old <= end) or
                (new and new >= start and new <= end)
            )
        ]

        if not relevant_changes:
            return

        body = settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY.format(
            study=self.study,
            changes='\n'.join('%s -> %s' % (
                timezone.localtime(old),
                timezone.localtime(new),
            ) for (old, new) in relevant_changes),
            participation_url=self.request.build_absolute_uri(reverse(
                'execution:participation-detail',
                args=[self.study.pk, self.object.pk]
            )),
            calendar_url=self.request.build_absolute_uri(reverse(
                'execution:calendar',
                args=[self.study.pk]
            )),
        )

        perm = 'recruitment.conduct_study'
        connection = get_connection()
        for user in self.study.members.all():
            if user != self.request.user and user.has_perm(perm, obj=self.study):
                msg = EmailMessage(
                    settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    connection=connection,
                )
                msg.send()

    def form_valid(self, form):
        response = super().form_valid(form)
        self.send_appointment_notifications(form.appointment_changes)
        return response


class RecruitmentUpdateMixin(ParticipationMixin):
    study_status = [Study.EXECUTION]

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "recruitment/base.html"
        return context


class ContactUpdateView(RecruitmentUpdateMixin, BaseContactUpdateView):
    def get_object(self):
        return self.participation.subject.contact


class AttributeSetUpdateView(RecruitmentUpdateMixin, BaseAttributeSetUpdateView):
    def get_object(self):
        return self.participation.subject.attributeset


class DataProtectionUpdateView(RecruitmentUpdateMixin, BaseDataProtectionUpdateView):
    def get_object(self):
        return self.participation.subject


class AdditionalInfoUpdateView(RecruitmentUpdateMixin, BaseAdditionalInfoUpdateView):
    def get_object(self):
        return self.participation.subject


class CalendarView(StudyMixin, PermissionRequiredMixin, BaseCalendarView):
    model = Study
    permission_required = 'recruitment.view_participation'
    study_status = [Study.EXECUTION]
    nochrome = True
    feed = 'recruitment:calendar-feed'

    def get_appointments(self):
        return super().get_appointments().filter(session__study=self.object)

    def get_external_events(self):
        for feed in StudyTypeEventFeed.objects.filter(study_type__studysession__study=self.object):
            try:
                text = cached_request(feed.url, timeout=60)
                calendar = Calendar.from_ical(text)
                for event in calendar.walk('VEVENT'):
                    yield {
                        'title': '[%s] %s' % (feed.study_type, event.get('SUMMARY', '')),
                        'start': event.get('DTSTART').dt,
                        'end': event.get('DTEND').dt,
                    }
            except Exception as e:
                logger.error('Fetching StudyTypeEventFeed %i failed: %s' % (feed.pk, e))

    def get_events(self):
        return super().get_events() + list(self.get_external_events())
