# (c) 2018
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
from django.http import Http404
from django.shortcuts import get_object_or_404

from castellum.studies.models import Study


class PublishedStudyMixin:
    def dispatch(self, request, *args, **kwargs):
        study_pk = self.kwargs.get('study_pk')
        self.study = get_object_or_404(Study, pk=study_pk)
        if not self.study.published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.study


class UnpublishedStudyMixin:
    def dispatch(self, request, *args, **kwargs):
        study_pk = self.kwargs.get('study_pk')
        self.study = get_object_or_404(Study, pk=study_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.study

    def post(self, request, *args, **kwargs):
        if self.study.published:
            raise PermissionDenied
        return super().post(request, *args, **kwargs)
