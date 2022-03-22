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

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from castellum.castellum_auth.mixins import APIAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.attribute_exporters import JSONExporter

from .models import Subject

monitoring_logger = logging.getLogger('monitoring.subjects')


class APIAttributesView(APIAuthMixin, PermissionRequiredMixin, View):
    permission_required = ['subjects.view_subject']

    def get(self, request, **kwargs):
        try:
            pseudonym = settings.CASTELLUM_PSEUDONYM_CLEAN(self.kwargs['pseudonym'])
        except ValueError:
            raise Http404

        coding_list = get_object_or_404(
            request.user.general_coding_lists, key=self.kwargs['coding_list']
        )

        try:
            subject = get_subject(coding_list.key, pseudonym)
        except Subject.DoesNotExist:
            raise Http404

        if not self.request.user.has_privacy_level(max(
            subject.privacy_level,
            coding_list.get_exportable_attributes_max_privacy_level(),
        )):
            raise PermissionDenied

        exporter = JSONExporter()
        descriptions = coding_list.exportable_attributes.all()

        attrs = exporter.get_subject_attributes(descriptions, subject)

        monitoring_logger.info('Attribute export: coding_list {} subject {} by {}'.format(
            coding_list.key, subject.pk, request.user.pk
        ))

        return JsonResponse(attrs)
