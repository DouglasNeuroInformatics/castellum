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

import datetime

from django.views.generic import TemplateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from . import helpers


class DataProtectionView(PermissionRequiredMixin, TemplateView):
    template_name = 'data_protection/index.html'
    permission_required = [
        'subjects.export_subject',
        'castellum_auth.privacy_level_2',
    ]
    limit_by = 10

    def limit(self, qs):
        return qs[:self.limit_by], max(qs.count() - self.limit_by, 0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_requested'], context['export_requested_missing'] = self.limit(helpers.get_export_requested())  # noqa
        context['to_be_deleted'], context['to_be_deleted_missing'] = self.limit(helpers.get_to_be_deleted())  # noqa
        context['no_legal_basis'], context['no_legal_basis_missing'] = self.limit(helpers.get_no_legal_basis())  # noqa
        context['unreachable'], context['unreachable_missing'] = self.limit(helpers.get_unreachable())  # noqa
        context['today'] = datetime.date.today()
        return context
