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

import mimetypes

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import classonlymethod
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import View
from django.views.static import serve

from stronghold.decorators import public


def get_next_url(request, default='/'):
    url = request.POST.get('next', request.GET.get('next'))
    is_safe = url_has_allowed_host_and_scheme(
        url, allowed_hosts=[request.get_host()], require_https=request.is_secure()
    )
    if url and is_safe:
        return url
    else:
        return default


class StrongholdPublicMixin:
    # https://github.com/mgrouchy/django-stronghold/pull/88

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        return public(super().as_view(*args, **kwargs))


class BaseProtectedMediaView(LoginRequiredMixin, View):
    def get_path(self):
        return self.kwargs['path']

    def get(self, request, **kwargs):
        path = self.get_path()

        if settings.PROTECTED_MEDIA_SERVER == 'django':
            return serve(request, path, document_root=settings.MEDIA_ROOT)
        elif settings.PROTECTED_MEDIA_SERVER == 'nginx':
            response = HttpResponse()
            response['X-Accel-Redirect'] = settings.PROTECTED_MEDIA_URL + path
            return response
        else:
            mimetype, encoding = mimetypes.guess_type(settings.MEDIA_ROOT / path)
            response = HttpResponse()
            response['Content-Type'] = mimetype
            if encoding:
                response['Content-Encoding'] = encoding
            response['X-Sendfile'] = settings.MEDIA_ROOT / path
            return response


class ProtectedMediaView(BaseProtectedMediaView):
    pass
