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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect
from django.utils.translation import check_for_language
from django.views.generic import DetailView
from django.views.generic import ListView

from castellum.utils.views import get_next_url

from .models import User

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


class ServiceAccountListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'castellum_auth/serviceaccount_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_service_account=True)


class ServiceAccountControlView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'castellum_auth/serviceaccount_control.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_service_account=True)

    def post(self, request, *args, **kwargs):
        service_account = self.get_object()
        if request.POST.get('control'):
            service_account.controlled_by = request.user
            service_account.save()
        else:
            if service_account.controlled_by != request.user:
                raise SuspiciousOperation
            service_account.controlled_by = None
            service_account.save()
        return redirect('service-accounts')
