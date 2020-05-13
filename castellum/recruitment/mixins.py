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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.subjects.mixins import SubjectMixin
from castellum.utils.feeds import BaseICalFeed

from .forms import AttributeSetForm
from .models import Appointment
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest
from .models.attributesets import ANSWER_DECLINED
from .models.attributesets import UNCATEGORIZED

monitoring_logger = logging.getLogger('monitoring.recruitment')


class ParticipationRequestMixin(StudyMixin, SubjectMixin):
    """Use this on every view that represents a participation request.

    -   pull in StudyMixin and SubjectMixin
    -   set ``self.participation_request``
    -   check that ``pk`` and ``study_pk`` refer to the same study
    -   check that status is in ``participationrequest_status``, otherwise return 404

    Requires PermissionRequiredMixin.
    """

    participationrequest_status = []

    @cached_property
    def participationrequest(self):
        qs = ParticipationRequest.objects.all()
        if self.participationrequest_status:
            qs = qs.filter(status__in=self.participationrequest_status)
        return get_object_or_404(qs, pk=self.kwargs['pk'], study_id=self.kwargs['study_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participationrequest'] = self.participationrequest
        return context


class BaseAttributeSetUpdateView(PermissionRequiredMixin, UpdateView):
    model = AttributeSet
    permission_required = 'recruitment.change_attributeset'

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
        return Appointment.objects.filter(participant__status=ParticipationRequest.INVITED)

    def render_appointment(self, appointment):
        return {
            'start': appointment.start,
            'end': appointment.end,
        }

    def get(self, request, *args, **kwargs):
        if 'events' in request.GET:
            self.object = self.get_object()
            events = [self.render_appointment(a) for a in self.get_appointments()]
            return JsonResponse({'events': events})
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
