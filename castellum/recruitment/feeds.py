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

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify

from django_ical.views import ICalFeed
from stronghold.decorators import public

from castellum.castellum_auth.models import User
from castellum.studies.models import Resource
from castellum.studies.models import Study

from .models import Appointment
from .models import ParticipationRequest


@public
class BaseFollowUpFeed(ICalFeed):
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

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
        rel = reverse('recruitment:contact', args=[item.study.pk, item.pk])
        return self.request.build_absolute_uri(rel)

    def item_description(self, item):
        return self.item_link(item)


class FollowUpFeedForStudy(BaseFollowUpFeed):
    def get_object(self, request, *args, **kwargs):
        try:
            user = User.objects.get(token=request.GET.get('token'))
        except User.DoesNotExist:
            raise PermissionDenied
        study = get_object_or_404(Study, pk=kwargs.get('study_pk'), status=Study.EXECUTION)
        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        if not user.has_perms(perms, obj=study):
            raise PermissionDenied
        return study

    def items(self, study):
        return ParticipationRequest.objects\
            .filter(study=study, followup_date__isnull=False)\
            .order_by('-followup_date', '-followup_time')

    def file_name(self, study):
        return 'castellum-{}-followups.ics'.format(slugify(study.name))


class FollowUpFeedForUser(BaseFollowUpFeed):
    def get_object(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('user_id'))
        if user.token != request.GET.get('token'):
            raise PermissionDenied
        return user

    def items(self, user):
        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        for study in Study.objects.filter(status=Study.EXECUTION):
            if not user.has_perms(perms, obj=study):
                continue
            qs = ParticipationRequest.objects\
                .filter(study=study, followup_date__isnull=False)\
                .order_by('-followup_date', '-followup_time')
            for participation_request in qs:
                yield participation_request

    def file_name(self, study):
        return 'castellum-followups.ics'


@public
class BaseAppointmentFeed(ICalFeed):
    def get_user(self, request):
        try:
            return User.objects.get(token=request.GET.get('token'))
        except User.DoesNotExist:
            raise PermissionDenied

    def item_start_datetime(self, item):
        return item.start

    def item_end_datetime(self, item):
        return item.end

    def item_link(self, item):
        # This is not really a usable link, but it is unique
        url = reverse('execution:participationrequest-detail', args=[
            item.session.study.pk, item.participant.pk
        ])
        return '{}?appointment={}'.format(url, item.pk)

    def item_description(self, item):
        # prevent default str(item)
        return ''

    def file_name(self, obj):
        return 'castellum-%s-appointments.ics' % obj


class StudyAppointmentFeed(BaseAppointmentFeed):
    def get_object(self, request, *args, **kwargs):
        user = self.get_user(request)
        study = get_object_or_404(Study, pk=kwargs['pk'], status=Study.EXECUTION)
        perms = ('recruitment.view_participationrequest', 'studies.access_study')
        if not user.has_perms(perms, obj=study):
            raise PermissionDenied
        return study

    def items(self, study):
        return Appointment.objects.filter(session__study=study)

    def item_title(self, item):
        return '{} - {}'.format(
            item.session.name,
            item.participant.pseudonym,
        )


class ResourceAppointmentFeed(BaseAppointmentFeed):
    def get_object(self, request, *args, **kwargs):
        user = self.get_user(request)
        resource = get_object_or_404(Resource, pk=kwargs['pk'])
        if not user.has_perm('studies.view_resource'):
            raise PermissionDenied
        return resource

    def items(self, resource):
        return Appointment.objects.filter(session__resource=resource)

    def item_title(self, item):
        return '{} - {} - {}'.format(
            item.session.study,
            item.session.name,
            item.session.study.contact_person,
        )
