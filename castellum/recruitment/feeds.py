# (c) 2018
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

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify

from django_ical.views import ICalFeed

from castellum.castellum_auth.models import User
from castellum.studies.models import Study

from .models import ParticipationRequest


class BaseFollowUpFeed(ICalFeed):
    def item_title(self, item):
        return '{} - {}'.format(item.study.name, item.pk)

    def item_start_datetime(self, item):
        return item.followup

    def item_updateddate(self, item):
        return item.updated_at

    def item_description(self, item):
        return item.pk

    def item_link(self, item):
        return reverse('recruitment:contact', args=[item.study.pk, item.pk])


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
            .filter(study=study, followup__isnull=False)\
            .order_by('-followup')

    def file_name(self, study):
        return 'castellum-{}.ics'.format(slugify(study.name))


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
            qs = (ParticipationRequest.objects.filter(study=study, followup__isnull=False)
                                              .order_by('-followup'))
            for participation_request in qs:
                yield participation_request

    def file_name(self, study):
        return 'castellum-followups.ics'
