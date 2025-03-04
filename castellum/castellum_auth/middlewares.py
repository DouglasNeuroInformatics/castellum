# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class UserExpirationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            error = None
            if not request.user.expiration_date:
                error = _('Your account is not activated.')
            elif request.user.expiration_date < timezone.now():
                error = _('Your account is expired.')

            if error is not None:
                logout(request)
                messages.add_message(request, messages.ERROR, error)


def get_last_active(request):
    s = request.session['_last_active']
    return datetime.datetime.strptime(s, DATETIME_FORMAT)


def set_last_active(request):
    now = timezone.now()
    request.session['_last_active'] = now.strftime(DATETIME_FORMAT)


class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and 'events' not in request.GET:
            now = timezone.now()
            login_time = request.user.last_login or now
            last_active = get_last_active(request)

            if (
                login_time.date() != now.date()
                or now > last_active + settings.CASTELLUM_LOGOUT_TIMEOUT
            ):
                logout(request)
                messages.add_message(
                    request, messages.ERROR, _('Your session has expired')
                )
            elif now > last_active + settings.CASTELLUM_LOGOUT_TIMEOUT / 10:
                set_last_active(request)


class UserLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.language:
            translation.activate(request.user.language)
