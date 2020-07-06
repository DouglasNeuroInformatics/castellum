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

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from castellum.studies.models import Study

from .mixins import BaseAppointmentFeed
from .mixins import BaseFollowUpFeed
from .models import Participation


class FollowUpFeedForStudy(BaseFollowUpFeed):
    def get_object(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=kwargs.get('study_pk'), status=Study.EXECUTION)
        perms = ('recruitment.add_participation', 'studies.access_study')
        if not self.request.user.has_perms(perms, obj=study):
            raise PermissionDenied
        return study

    def items(self, study):
        return Participation.objects\
            .filter(study=study, followup_date__isnull=False)\
            .order_by('-followup_date', '-followup_time')


class FollowUpFeedForUser(BaseFollowUpFeed):
    def get_object(self, request, *args, **kwargs):
        return self.request.user

    def items(self, user):
        perms = ('recruitment.add_participation', 'studies.access_study')
        for study in Study.objects.filter(status=Study.EXECUTION):
            if not user.has_perms(perms, obj=study):
                continue
            qs = Participation.objects\
                .filter(study=study, followup_date__isnull=False)\
                .order_by('-followup_date', '-followup_time')
            for participation in qs:
                yield participation


class AppointmentFeed(BaseAppointmentFeed):
    def get_object(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=kwargs['pk'], status=Study.EXECUTION)
        perms = ('recruitment.view_participation', 'studies.access_study')
        if not self.request.user.has_perms(perms, obj=study):
            raise PermissionDenied
        return study

    def items(self, study):
        return super().items(study).filter(session__study=study)

    def item_link(self, item):
        # This is not really a usable link, but it is unique
        return '/appointments/%i/' % item.pk
