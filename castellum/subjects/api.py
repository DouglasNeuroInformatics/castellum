# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_noop
from django.views.generic import View

from castellum.audit.helpers import audit
from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.attribute_exporters import JSONExporter

from .models import Subject


class APIAttributesView(APIAuthMixin, PermissionRequiredMixin, View):
    permission_required = ['subjects.view_subject']

    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError as e:
            raise Http404 from e

        domain = get_object_or_404(
            request.user.general_domains, key=self.kwargs['domain']
        )

        try:
            subject = get_subject(domain.key, pseudonym)
        except Subject.DoesNotExist as e:
            raise Http404 from e

        if not self.request.user.has_privacy_level(subject.privacy_level):
            raise PermissionDenied

        exporter = JSONExporter()
        attributes = domain.exportable_attributes.all()

        data = exporter.get_subject_attributes(attributes, subject)

        audit(
            gettext_noop('attributes exported'),
            request.user.username,
            subject_pk=subject.pk,
            extra={'domain': domain.key},
        )

        return JsonResponse(data)
