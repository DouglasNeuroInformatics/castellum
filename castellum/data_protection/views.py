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

from django.views.generic import ListView
from django.views.generic import TemplateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.data_protection import monitoring_logger
from castellum.subjects.models import Consent

from . import helpers
from .models import MonitoringEntry


class DataProtectionView(PermissionRequiredMixin, TemplateView):
    template_name = 'data_protection/index.html'
    permission_required = [
        'subjects.view_subject',
        'castellum_auth.privacy_level_2',
    ]
    tab = 'dashboard'
    limit_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_be_deleted'], context['to_be_deleted_missing'] = helpers.get_to_be_deleted(self.limit_by)  # noqa
        context['orphans'], context['orphans_missing'] = helpers.get_orphans(self.limit_by)
        context['unreachable'], context['unreachable_missing'] = helpers.get_unreachable(self.limit_by)  # noqa
        context['db_consent_uploaded'] = Consent.objects.exists()
        context['no_consent'], context['no_consent_missing'] = helpers.get_no_consent(self.limit_by)
        context['studies'], context['studies_missing'] = helpers.get_studies(self.limit_by)
        return context


class MonitoringView(PermissionRequiredMixin, ListView):
    model = MonitoringEntry
    tab = 'monitoring'
    template_name = 'data_protection/monitoring.html'
    permission_required = [
        'view_monitoring',
        'castellum_auth.privacy_level_2',
    ]

    def get_reason(self):
        reason_options = dict(MonitoringEntry.REASONS)
        try:
            reason = int(self.request.GET.get('reason'))
            return reason, reason_options[reason]
        except (ValueError, TypeError, KeyError):
            reason = monitoring_logger.LOGIN
            return reason, reason_options[reason]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reason_options'] = MonitoringEntry.REASONS
        __, context['reason_label'] = self.get_reason()
        return context

    def get_queryset(self):
        reason, __ = self.get_reason()
        return super().get_queryset().filter(reason=reason)
