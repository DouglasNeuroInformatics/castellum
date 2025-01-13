# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.shortcuts import get_object_or_404

from castellum.appointments.mixins import BaseAppointmentFeed
from castellum.castellum_auth.mixins import ParamAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Resource
from castellum.studies.models import Study

from .mixins import BaseFollowUpFeed
from .models import Participation


class FollowUpFeedForStudy(
    ParamAuthMixin, StudyMixin, PermissionRequiredMixin, BaseFollowUpFeed
):
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]

    def items(self):
        return (
            Participation.objects
            .filter(study=self.study, followup_date__isnull=False)
            .order_by('-followup_date', '-followup_time')
        )


class FollowUpFeedForUser(ParamAuthMixin, BaseFollowUpFeed):
    def items(self):
        perms = ['recruitment.recruit', 'studies.access_study']
        for study in Study.objects.filter(status=Study.EXECUTION):
            if not self.request.user.has_perms(perms, obj=study):
                continue
            yield from (
                Participation.objects
                .filter(study=study, followup_date__isnull=False)
                .order_by('-followup_date', '-followup_time')
            )


class AppointmentFeedForStudy(
    ParamAuthMixin, StudyMixin, PermissionRequiredMixin, BaseAppointmentFeed
):
    permission_required = ['studies.access_study']
    study_status = [Study.EXECUTION]

    def has_permission(self):
        if not super().has_permission():
            return False
        return any(self.request.user.has_perm(perm, obj=self.study) for perm in [
            'appointments.change_appointment',
            'recruitment.conduct_study',
        ])

    def items(self):
        return super().items().filter(session__study=self.study)

    def item_title(self, item):
        return ''


class AppointmentFeedForResource(ParamAuthMixin, BaseAppointmentFeed):
    def items(self):
        resource = get_object_or_404(Resource, pk=self.kwargs['pk'])
        return (
            super().items()
            .filter(session__resources=resource)
            .exclude(session__study__status=Study.FINISHED)
        )

    def item_title(self, item):
        return item.session.study.name
