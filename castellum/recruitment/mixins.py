# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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
from typing import List

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.subjects.mixins import SubjectMixin
from castellum.subjects.models import Subject
from castellum.utils.feeds import BaseCalendarFeed
from castellum.utils.mail import MailContext

from . import filter_queries
from .forms import AttributesForm
from .forms import SendMailForm
from .models import AttributeDescription
from .models import MailBatch
from .models import Participation
from .models.attributes import ANSWER_DECLINED
from .models.attributes import UNCATEGORIZED

logger = logging.getLogger(__name__)
monitoring_logger = logging.getLogger('monitoring.recruitment')


def get_recruitable(study, is_urgent=False):
    """Get all subjects who are recruitable for this study.

    i.e. apply all filters
    """
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
        models.Q(last_contacted__lte=last_contacted)
        | models.Q(last_contacted__isnull=True)
    )

    if is_urgent:
        # matches the definition in ParticipationQuerySet
        recent = timezone.now() - settings.CASTELLUM_RECENT_ACTIVITY_PERIOD
        qs = qs.annotate(recent_participation_count=models.Count(
            'participation',
            filter=models.Q(
                participation__updated_at__gt=recent,
                participation__status=Participation.INVITED,
            ),
            distinct=True,
        )).exclude(recent_participation_count=0)

    return list(qs)


class ParticipationMixin(StudyMixin, SubjectMixin):
    """Use this on every view that represents a participation.

    -   pull in StudyMixin and SubjectMixin
    -   set ``self.participation``
    -   check that ``pk`` and ``study_pk`` refer to the same study
    -   check that status is in ``participation_status``, otherwise
        return 404

    Requires PermissionRequiredMixin.
    """

    participation_status: List[int] = []

    @cached_property
    def participation(self):
        qs = Participation.objects.all()
        if self.participation_status:
            qs = qs.filter(status__in=self.participation_status)
        return get_object_or_404(qs, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk'])

    def get_subject(self):
        return self.participation.subject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participation'] = self.participation
        return context


class BaseAttributesUpdateView(PermissionRequiredMixin, UpdateView):
    model = Subject
    permission_required = 'subjects.change_subject'
    template_name = 'recruitment/attributes_form.html'

    def get_form_class(self):
        return AttributesForm.factory()

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('Attributes update: {} by {}'.format(
            self.object.pk,
            self.request.user.pk,
        ))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        def get_bound_fields(descriptions):
            for description in descriptions:
                value = self.object.attributes.get(description.json_key)
                try:
                    yield form['d{}'.format(description.pk)], value == ANSWER_DECLINED
                except KeyError:
                    pass

        categories = AttributeDescription.objects.by_category()
        context['uncategorized'] = get_bound_fields(categories.pop(UNCATEGORIZED))
        context['categories'] = {
            category: get_bound_fields(descriptions)
            for category, descriptions in categories.items()
        }

        return context


class BaseFollowUpFeed(BaseCalendarFeed):
    def item_title(self, item):
        return '{} - Follow-Up'.format(item.study.name)

    def item_start(self, item):
        if item.followup_time:
            return datetime.datetime.combine(item.followup_date, item.followup_time)
        else:
            return item.followup_date

    def item_updated_at(self, item):
        return item.updated_at

    def item_link(self, item):
        return reverse('recruitment:contact', args=[item.study.pk, item.pk])

    def item_uid(self, item):
        return 'followup-{}@{}'.format(item.pk, self.request.get_host())


class BaseMailRecruitmentView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'recruitment/mail.html'
    form_class = SendMailForm

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
                '{} emails have been sent.\n\n---\n\n{}'.format(counter, self.study.mail_body),
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

    def _form_valid(self, form):
        batch_size = form.cleaned_data['batch_size']
        allowed_size = min(
            batch_size,
            settings.CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT - self.get_weekly_mails(),
        )

        if allowed_size <= 0:
            messages.error(self.request, _(
                'You have reached the weekly limit for mail recruitment.'
            ))
            return

        participations = self.create_participations(allowed_size)

        if not participations:
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
                    'Only {added} out of {batchsize} potential participants with email '
                    'addresses could be found for this study. These have been contacted.'
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
