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

from datetime import date

from django.db import models
from django.views.generic import TemplateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.subjects.models import ExportAnswer
from castellum.subjects.models import Subject

from . import helpers


class DataProtectionView(PermissionRequiredMixin, TemplateView):
    template_name = 'data_protection/index.html'
    permission_required = [
        'subjects.export_subject',
        'castellum_auth.privacy_level_2',
    ]
    limit_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['export_requested'], context['export_requested_missing'] = helpers.get_export_requested(self.limit_by)  # noqa
        context['to_be_deleted'], context['to_be_deleted_missing'] = helpers.get_to_be_deleted(self.limit_by)  # noqa
        context['no_legal_basis'], context['no_legal_basis_missing'] = helpers.get_no_legal_basis(self.limit_by)  # noqa
        context['unreachable'], context['unreachable_missing'] = helpers.get_unreachable(self.limit_by)  # noqa

        context['export_requested_stats'] = (
            Subject.objects
            .exclude(export_requested=None)
            .annotate(days=date.today() - models.F('export_requested'))
            .aggregate(models.Max('days'), models.Avg('days'), models.Count('days'))
        )
        context['to_be_deleted_stats'] = (
            Subject.objects
            .exclude(to_be_deleted=None)
            .annotate(days=date.today() - models.F('to_be_deleted'))
            .aggregate(models.Max('days'), models.Avg('days'), models.Count('days'))
        )
        context['export_answer_count'] = ExportAnswer.objects.count()

        return context
