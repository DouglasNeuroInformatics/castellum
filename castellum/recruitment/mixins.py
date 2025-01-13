# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import logging

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_noop
from django.views.generic import UpdateView

from castellum.audit.helpers import audit
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.subjects.mixins import SubjectMixin
from castellum.subjects.models import Subject
from castellum.utils.feeds import BaseCalendarFeed

from . import filter_queries
from .forms import AttributesForm
from .models import Attribute
from .models import Participation
from .models.attributes import ANSWER_DECLINED
from .models.attributes import UNCATEGORIZED

logger = logging.getLogger(__name__)


def get_recruitable(study):
    """Get all subjects who are recruitable for this study.

    i.e. apply all filters
    """
    qs = Subject.objects.filter(
        filter_queries.study_recruitable(study),
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

    participation_status = []

    @cached_property
    def participation(self):
        qs = Participation.objects.all()
        if self.participation_status:
            qs = qs.filter(status__in=self.participation_status)
        return get_object_or_404(
            qs, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk']
        )

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
        audit(
            gettext_noop('subject updated'),
            self.request.user.username,
            subject_pk=self.object.pk,
        )
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        def get_bound_fields(attributes):
            for attribute in attributes:
                value = self.object.attributes.get(attribute.json_key)
                try:
                    yield form[attribute.json_key], value == ANSWER_DECLINED
                except KeyError:
                    pass

        categories = Attribute.objects.by_category()
        context['uncategorized'] = get_bound_fields(categories.pop(UNCATEGORIZED))
        context['categories'] = {
            category: get_bound_fields(attributes)
            for category, attributes in categories.items()
        }

        return context


class BaseFollowUpFeed(BaseCalendarFeed):
    def item_title(self, item):
        return f'{item.study.name} - Follow-Up'

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
        return f'followup-{item.pk}@{self.request.get_host()}'
