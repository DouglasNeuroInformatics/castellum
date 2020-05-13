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

from django_ical.views import ICalFeed
from stronghold.decorators import public

from castellum.castellum_auth.models import User
from castellum.studies.models import Study

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
        return reverse('recruitment:contact', args=[item.study.pk, item.pk])

    def item_description(self, item):
        return self.request.build_absolute_uri(self.item_link(item))


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


