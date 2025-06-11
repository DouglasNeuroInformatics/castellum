# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm('subjects.delete_subject'):
            qs = helpers.get_subjects()
        else:
            qs = helpers.get_export_requested()
        return qs.prefetch_contacts()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = datetime.date.today()
        return context
