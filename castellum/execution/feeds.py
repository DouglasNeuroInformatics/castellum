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

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from castellum.appointments.mixins import BaseAppointmentFeed
from castellum.castellum_auth.mixins import ParamAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Resource
from castellum.studies.models import Study


class BaseExecutionAppointmentFeed(BaseAppointmentFeed):
    def item_title(self, item):
        if self.request.user.has_privacy_level(item.participation.subject.privacy_level):
            name = item.participation.subject.contact.full_name
        else:
            name = _('(access denied)')
        return '{} - {}'.format(name, item.session.name)

    def item_link(self, item):
        return reverse('execution:participation-detail', args=[
            item.session.study.pk, item.participation.pk
        ])


class AppointmentFeedForStudy(
    ParamAuthMixin, StudyMixin, PermissionRequiredMixin, BaseExecutionAppointmentFeed
):
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]

    def items(self):
        return (
            super().items()
            .filter(session__study=self.study)
            .select_related('participation__subject', 'session__study')
        )


class AppointmentFeedForUser(ParamAuthMixin, BaseExecutionAppointmentFeed):
    def items(self):
        items = (
            super().items()
            .filter(session__study__status=Study.EXECUTION)
            .select_related('participation__subject', 'session__study')
        )

        perms = ['recruitment.conduct_study', 'studies.access_study']
        for item in items:
            if self.request.user.has_perms(perms, obj=item.session.study):
                yield item


class ResourceFeed(ParamAuthMixin, BaseExecutionAppointmentFeed):
    def items(self):
        resource = get_object_or_404(Resource, pk=self.kwargs['pk'], managers=self.request.user)
        return (
            super().items()
            .filter(session__resources=resource)
            .exclude(session__study__status=Study.FINISHED)
        )
