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
from typing import List
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.subjects.mixins import SubjectMixin
from castellum.subjects.models import Subject
from castellum.utils import add_working_days
from castellum.utils.feeds import BaseICalFeed
from castellum.utils.mail import send_mail
from castellum.utils.mail import send_mass_mail

from . import filter_queries
from .forms import AttributeSetForm
from .forms import SendMailForm
from .models import Appointment
from .models import AttributeDescription
from .models import AttributeSet
from .models import MailBatch
from .models import Participation
from .models.attributesets import ANSWER_DECLINED
from .models.attributesets import UNCATEGORIZED

logger = logging.getLogger(__name__)
monitoring_logger = logging.getLogger('monitoring.recruitment')


def get_recruitable(study):
    """Get all subjects who are recruitable for this study, i.e. apply all filters."""
    qs = Subject.objects.filter(
        filter_queries.study(study),
        filter_queries.has_consent(),
        filter_queries.already_in_study(study),
    )

    last_contacted = timezone.now() - settings.CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS
    qs = qs.annotate(last_contacted=models.Max(
        'participation__updated_at',
        filter=~models.Q(
            participation__status=Participation.NOT_CONTACTED
        ),
    )).filter(
        models.Q(last_contacted__lte=last_contacted) |
        models.Q(last_contacted__isnull=True)
    )

    return list(qs)


def send_appointment_notifications(request, participation, changes):
    start = timezone.now()
    end = add_working_days(start, 2)
    relevant_changes = [
        (old, new) for (old, new) in changes if (
            (old and old >= start and old <= end) or
            (new and new >= start and new <= end)
        )
    ]

    if not relevant_changes:
        return

    body = settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY.format(
        study=participation.study,
        changes='\n'.join('%s -> %s' % (
            timezone.localtime(old),
            timezone.localtime(new),
        ) for (old, new) in relevant_changes),
        participation_url=request.build_absolute_uri(reverse(
            'execution:participation-detail',
            args=[participation.study.pk, participation.pk]
        )),
        calendar_url=request.build_absolute_uri(reverse(
            'execution:calendar',
            args=[participation.study.pk]
        )),
    )

    msgs = []
    mail_subject = settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT
    for user in participation.study.conductors:
        if user != request.user:
            msgs.append((mail_subject, body, [user.email], {}))
    return send_mass_mail(msgs, context='internal')


class ParticipationMixin(StudyMixin, SubjectMixin):
    """Use this on every view that represents a participation.

    -   pull in StudyMixin and SubjectMixin
    -   set ``self.participation``
    -   check that ``pk`` and ``study_pk`` refer to the same study
    -   check that status is in ``participation_status``, otherwise return 404

    Requires PermissionRequiredMixin.
    """

    participation_status: List[int] = []

    @cached_property
    def participation(self):
        qs = Participation.objects.all()
        if self.participation_status:
            qs = qs.filter(status__in=self.participation_status)
        return get_object_or_404(qs, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk'])

    @cached_property
    def subject(self):
        return self.participation.subject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participation'] = self.participation
        return context


class BaseAttributeSetUpdateView(PermissionRequiredMixin, UpdateView):
    model = AttributeSet
    permission_required = 'subjects.change_subject'

    def get_form_class(self):
        return AttributeSetForm.factory(self.request.user)

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('AttributeSet update: {} by {}'.format(
            self.object.subject.pk,
            self.request.user.pk,
        ))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        def get_bound_fields(descriptions):
            for description in descriptions:
                answer_declined = self.object.data.get(description.json_key) == ANSWER_DECLINED
                try:
                    yield form['d%i' % description.pk], answer_declined
                except KeyError:
                    pass

        categories = AttributeDescription.objects.by_category()
        context['uncategorized'] = get_bound_fields(categories.pop(UNCATEGORIZED))
        context['categories'] = {
            category: get_bound_fields(descriptions)
            for category, descriptions in categories.items()
        }

        return context


class BaseCalendarView(DetailView):
    template_name = 'recruitment/calendar.html'

    def get_appointments(self):
        return Appointment.objects.filter(participation__status=Participation.INVITED)

    def render_appointment(self, appointment):
        return {
            'start': appointment.start,
            'end': appointment.end,
        }

    def get_events(self):
        self.object = self.get_object()
        return [self.render_appointment(a) for a in self.get_appointments()]

    def get(self, request, *args, **kwargs):
        if 'events' in request.GET:
            return JsonResponse({'events': self.get_events()})
        else:
            return super().get(request, *args, **kwargs)


class BaseFollowUpFeed(BaseICalFeed):
    def item_title(self, item):
        return '{} - Follow-Up'.format(item.study.name)

    def item_start_datetime(self, item):
        if item.followup_time:
            return datetime.combine(item.followup_date, item.followup_time)
        else:
            return item.followup_date

    def item_updateddate(self, item):
        return item.updated_at

    def item_link(self, item):
        return reverse('recruitment:contact', args=[item.study.pk, item.pk])

    def item_description(self, item):
        return self.request.build_absolute_uri(self.item_link(item))


class BaseAppointmentFeed(BaseICalFeed):
    def items(self, obj):
        return Appointment.objects.filter(participation__status=Participation.INVITED)

    def item_start_datetime(self, item):
        return item.start

    def item_end_datetime(self, item):
        return item.end


class BaseMailRecruitmentView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'recruitment/mail.html'
    form_class = SendMailForm
    participation_status: Optional[int] = None

    def personalize_mail_body(self, mail_body, contact):
        return mail_body.replace('{name}', contact.full_name)

    def create_participations(self, batch_size):
        subjects = get_recruitable(self.study)

        counter = 0
        while counter < batch_size and subjects:
            pick = subjects.pop(random.randrange(0, len(subjects)))
            msgs = []
            for email in pick.contact.own_or_guardian_emails:
                msgs.append((
                    self.study.mail_subject,
                    self.personalize_mail_body(self.study.mail_body, pick.contact),
                    [email],
                    {'reply_to': [self.study.email]}
                ))
            try:
                success = send_mass_mail(msgs, context='recruitment')
            except ValueError:
                logger.debug('Failed to send email to subject %i', pick.pk)
                success = False
            if success:
                Participation.objects.create(
                    study=self.study,
                    subject=pick,
                    status=self.participation_status,
                )
                counter += 1

        return counter

    def send_confirmation_mail(self, counter):
        send_mail(
            self.study.mail_subject,
            '%i emails have been sent.\n\n---\n\n%s' % (counter, self.study.mail_body),
            [self.study.email],
            context='internal',
        )

    def _form_valid(self, form):
        batch_size = form.cleaned_data['batch_size']
        try:
            added = self.create_participations(batch_size)
        except KeyError:
            added = 0
            messages.error(self.request, _(
                'The custom filter that is set for this study does not exist.'
            ))

        if added == 0:
            messages.error(
                self.request,
                _(
                    'No potential participants with email addresses could be found for '
                    'this study.'
                ),
            )
        elif added < batch_size:
            messages.warning(
                self.request,
                _(
                    'Only {added} out of {batchsize} potential participants with email '
                    'addresses could be found for this study. These have been contacted.'
                ).format(added=added, batchsize=batch_size),
            )
        else:
            messages.success(self.request, _('Emails sent successfully!'))

        if added > 0:
            MailBatch.objects.create(
                study=self.study,
                contacted_size=added,
            )
            self.send_confirmation_mail(added)
