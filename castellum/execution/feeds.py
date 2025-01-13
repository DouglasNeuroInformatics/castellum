# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
