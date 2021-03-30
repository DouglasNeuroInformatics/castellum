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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import check_for_language
from django.views.generic import TemplateView

from castellum.appointments.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.utils.views import get_next_url

LANGUAGE_QUERY_PARAMETER = 'language'


def set_language(request):
    """Save language in the user model.

    See also django.views.i18n.set_language
    """
    if request.method == 'POST' and request.user.is_authenticated:
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            request.user.language = lang_code
            request.user.save()

    return redirect(get_next_url(request))


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'castellum_auth/dashboard.html'

    def get_followups(self, start, end):
        results = []
        for participation in Participation.objects.filter(
            study__members=self.request.user,
            study__status=Study.EXECUTION,
            followup_date__gte=start,
            followup_date__lt=end,
        ).select_related('study'):
            study = participation.study
            if self.request.user.has_perm('recruitment.recruit', obj=study):
                results.append({
                    'type': 'followup',
                    'datetime': timezone.make_aware(datetime.datetime.combine(
                        participation.followup_date,
                        participation.followup_time or datetime.time(0, 0, 0),
                    )),
                    'obj': participation,
                })
        return results

    def get_appointments(self, start, end):
        results = []
        for appointment in Appointment.objects.filter(
            participation__study__members=self.request.user,
            participation__study__status=Study.EXECUTION,
            participation__status=Participation.INVITED,
            start__gte=start,
            start__lt=end,
        ).select_related('participation__study'):
            study = appointment.participation.study
            if self.request.user.has_perm('recruitment.conduct_study', obj=study):
                results.append({
                    'type': 'appointment',
                    'datetime': appointment.start,
                    'obj': appointment,
                })
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = datetime.date.today()

        context['studies'] = self.request.user.study_set.exclude(status=Study.FINISHED)

        upcoming = []
        upcoming += self.get_followups(today, today + datetime.timedelta(days=7))
        upcoming += self.get_appointments(today, today + datetime.timedelta(days=7))
        context['upcoming'] = sorted(upcoming, key=lambda ev: ev['datetime'])[:10]

        recent = []
        recent += self.get_followups(today - datetime.timedelta(days=7), today)
        recent += self.get_appointments(today - datetime.timedelta(days=7), today)
        context['recent'] = sorted(recent, key=lambda ev: ev['datetime'], reverse=True)[:10]

        return context
