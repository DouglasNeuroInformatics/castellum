# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.urls import reverse

from castellum.appointments.mixins import BaseAppointmentFeed
from castellum.castellum_auth.mixins import ParamAuthMixin
from castellum.studies.models import Study


class AppointmentFeedForUser(ParamAuthMixin, BaseAppointmentFeed):
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

    def item_title(self, item):
        return item.session.study.name

    def item_link(self, item):
        return reverse('execution:participation-detail', args=[
            item.session.study.pk, item.participation.pk
        ])
