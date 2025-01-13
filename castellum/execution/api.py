# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_noop
from django.views.generic import View

from castellum.audit.helpers import audit
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
        data = [
            {'key': domain.key, 'name': domain.name}
            for domain in self.study.domains.all()
        ]
        return JsonResponse({'domains': data})


class APIValidateView(BaseAPIView):
    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError as e:
            raise Http404 from e

        domain = get_object_or_404(self.study.domains, key=self.kwargs['domain'])

        try:
            subject = get_subject(domain.key, pseudonym)
        except Subject.DoesNotExist as e:
            raise Http404 from e

        get_object_or_404(
            Participation,
            subject=subject,
            study=self.study,
            status__in=Participation.INVITED_SET,
        )

        return JsonResponse({'pseudonym': pseudonym})


class APIPseudonymsView(BaseAPIView):
    def get(self, request, **kwargs):
        domain = get_object_or_404(self.study.domains, key=kwargs['domain'])

        pseudonyms = [get_pseudonym(p.subject, domain.key) for p in (
            self.study.participation_set
            .filter(status__in=Participation.INVITED_SET)
            .select_related('subject')
        )]

        return JsonResponse({'pseudonyms': pseudonyms})


class APIResolveView(BaseAPIView):
    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError as e:
            raise Http404 from e

        domain = get_object_or_404(self.study.domains, key=self.kwargs['domain'])

        try:
            subject = get_subject(domain.key, pseudonym)
        except Subject.DoesNotExist as e:
            raise Http404 from e
        get_object_or_404(
            Participation,
            subject=subject,
            study=self.study,
            status__in=Participation.INVITED_SET,
        )
        if not self.request.user.has_privacy_level(subject.privacy_level):
            raise PermissionDenied

        domains = Domain.objects.filter(
            models.Q(pk__in=self.study.domains.all())
            | models.Q(pk__in=self.study.general_domains.filter(managers=request.user))
        )
        target_domain = get_object_or_404(domains, key=self.kwargs['target_domain'])
        pseudonym = get_pseudonym(subject, target_domain.key)

        monitoring_logger.info(
            f'Pseudonym access: domain {target_domain.key} by {self.request.user.pk}'
        )
        audit(
            gettext_noop('pseudonym accessed'),
            self.request.user.username,
            study_pk=self.study.pk,
            extra={'domain': target_domain.key},
        )

        return JsonResponse({'pseudonym': pseudonym})


class APIAttributesView(BaseAPIView):
    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError as e:
            raise Http404 from e

        domain = get_object_or_404(self.study.domains, key=self.kwargs['domain'])

        try:
            subject = get_subject(domain.key, pseudonym)
        except Subject.DoesNotExist as e:
            raise Http404 from e
        get_object_or_404(
            Participation,
            subject=subject,
            study=self.study,
            status__in=Participation.INVITED_SET,
        )
        if not self.request.user.has_privacy_level(subject.privacy_level):
            raise PermissionDenied

        exporter = JSONExporter()
        attributes = self.study.exportable_attributes.all()

        data = exporter.get_subject_attributes(attributes, subject)

        monitoring_logger.info(
            f'Attribute export: '
            f'study {self.study.pk} subject {subject.pk} by {request.user.pk}'
        )
        audit(
            gettext_noop('attributes exported'),
            request.user.username,
            study_pk=self.study.pk,
            subject_pk=subject.pk,
        )

        return JsonResponse(data)
