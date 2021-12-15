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

from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from . import helpers


class DataProtectionView(PermissionRequiredMixin, ListView):
    template_name = 'data_protection/index.html'
    permission_required = [
        'subjects.export_subject',
        'castellum_auth.privacy_level_2',
    ]
    paginate_by = 15

    def get_queryset(self):
        if self.request.user.has_perm('subjects.delete_subject'):
            return helpers.get_subjects()
        else:
            return helpers.get_export_requested()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = datetime.date.today()
        return context
