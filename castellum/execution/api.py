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

from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment.attribute_exporters import JSONExporter
from castellum.recruitment.models import Participation
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.models import Subject

monitoring_logger = logging.getLogger('monitoring.execution')


class BaseAPIView(APIAuthMixin, StudyMixin, PermissionRequiredMixin, View):
    permission_required = ['recruitment.conduct_study']
    study_status = [Study.EXECUTION]


class APIDomainsView(BaseAPIView):
    def get(self, request, **kwargs):
        data = [{'key': domain.key, 'name': domain.name} for domain in self.study.domains.all()]
        return JsonResponse({'domains': data})


class APIValidateView(BaseAPIView):
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

        get_object_or_404(
            Participation, subject=subject, study=self.study, status=Participation.INVITED
        )

        return JsonResponse({'pseudonym': pseudonym})


class APIPseudonymsView(BaseAPIView):
    def get(self, request, **kwargs):
        domain = get_object_or_404(self.study.domains, key=kwargs['domain'])

        pseudonyms = [get_pseudonym(p.subject, domain.key) for p in (
            self.study.participation_set
            .filter(status=Participation.INVITED)
            .select_related('subject')
        )]

        return JsonResponse({'pseudonyms': pseudonyms})


class APIResolveView(BaseAPIView):
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
        get_object_or_404(
            Participation, subject=subject, study=self.study, status=Participation.INVITED
        )
        if not self.request.user.has_privacy_level(subject.privacy_level):
            raise PermissionDenied

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


class APIAttributesView(BaseAPIView):
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
        get_object_or_404(
            Participation, subject=subject, study=self.study, status=Participation.INVITED
        )
        if not self.request.user.has_privacy_level(max(
            subject.privacy_level,
            self.study.get_exportable_attributes_max_privacy_level(),
        )):
            raise PermissionDenied

        exporter = JSONExporter()
        descriptions = self.study.exportable_attributes.all()

        attrs = exporter.get_subject_attributes(descriptions, subject)

        monitoring_logger.info('Attribute export: study {} subject {} by {}'.format(
            self.study.pk, subject.pk, request.user.pk
        ))

        return JsonResponse(attrs)
