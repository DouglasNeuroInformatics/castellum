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

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.utils import translation
from django.utils.translation import gettext_lazy as _

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class UserExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            error = None
            if not request.user.expiration_date:
                error = _('Your account is not activated.')
            elif request.user.expiration_date < timezone.now():
                error = _('Your account is expired.')

            if error is not None:
                logout(request)
                messages.add_message(request, messages.ERROR, error)

        return self.get_response(request)


def get_last_active(request):
    s = request.session['_last_active']
    return datetime.datetime.strptime(s, DATETIME_FORMAT)


def set_last_active(request):
    now = timezone.now()
    request.session['_last_active'] = now.strftime(DATETIME_FORMAT)


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and 'events' not in request.GET:
            now = timezone.now()
            login_time = request.user.last_login or now
            idle_time = now - get_last_active(request)

            if login_time.date() != now.date() or idle_time > settings.CASTELLUM_LOGOUT_TIMEOUT:
                logout(request)
                messages.add_message(request, messages.ERROR, _('Your session has expired'))
            elif idle_time > settings.CASTELLUM_LOGOUT_TIMEOUT / 10:
                set_last_active(request)

        return self.get_response(request)


class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.language:
            translation.activate(request.user.language)
        return self.get_response(request)
