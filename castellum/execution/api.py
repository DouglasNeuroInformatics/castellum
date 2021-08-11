# (c) 2018-2021
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

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from stronghold.views import StrongholdPublicMixin

from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment.attribute_exporters import JSONExporter
from castellum.recruitment.models import Participation
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.models import Subject

monitoring_logger = logging.getLogger('monitoring.execution')


class APIDomainsView(StrongholdPublicMixin, StudyMixin, APIAuthMixin, View):
    permission_required = ['recruitment.conduct_study']
    study_status = [Study.EXECUTION]

    def get(self, request, **kwargs):
        data = [{'key': domain.key, 'name': domain.name} for domain in self.study.domains.all()]
        return JsonResponse({'domains': data})


class APIExportView(StrongholdPublicMixin, StudyMixin, APIAuthMixin, View):
    permission_required = ['recruitment.conduct_study']
    study_status = [Study.EXECUTION]

    def get(self, request, **kwargs):
        monitoring_logger.info('Attribute export: study {} by {}'.format(
            self.study.pk, request.user.pk
        ))

        domain = get_object_or_404(self.study.domains, key=kwargs['domain'])

        exporter = JSONExporter()
        descriptions = self.study.exportable_attributes.all()

        subjects = []
        for participation in (
            self.study.participation_set
            .filter(status=Participation.INVITED)
            .select_related('subject')
        ):
            if request.user.has_privacy_level(participation.subject.privacy_level):
                pseudonym = get_pseudonym(participation.subject, domain.key)
                subjects.append((pseudonym, participation.subject))

        data = exporter.get_raw_data(descriptions, subjects)
        return JsonResponse({'participants': data})


class APIResolveView(StrongholdPublicMixin, StudyMixin, APIAuthMixin, View):
    permission_required = ['recruitment.conduct_study']
    study_status = [Study.EXECUTION]

    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError:
            raise Http404

        domain = get_object_or_404(self.study.domains, key=self.kwargs['domain'])

        try:
            subject = get_subject(domain.key, pseudonym)
        except Subject.DoesNotExist:
            raise Http404
        if not self.request.user.has_privacy_level(subject.privacy_level):
            raise PermissionDenied

        get_object_or_404(
            Participation, subject=subject, study=self.study, status=Participation.INVITED
        )

        domains = Domain.objects.filter(
            models.Q(pk__in=self.study.domains.all())
            | models.Q(pk__in=self.study.general_domains.filter(user=request.user))
        )
        target_domain = get_object_or_404(domains, key=self.kwargs['target_domain'])
        pseudonym = get_pseudonym(subject, target_domain.key)

        monitoring_logger.info('Pseudonym access: domain {} by {}'.format(
            target_domain.key, self.request.user.pk
        ))

        return JsonResponse({'pseudonym': pseudonym})
