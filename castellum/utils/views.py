# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import mimetypes
import os
from urllib.parse import quote
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
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

    @classmethod
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
            response['X-Accel-Redirect'] = settings.PROTECTED_MEDIA_URL + quote(path)
            return response
        else:
            file_path = settings.MEDIA_ROOT / unquote(path)
            mimetype, encoding = mimetypes.guess_type(file_path)
            response = HttpResponse()
            response['Content-Type'] = mimetype
            if encoding:
                response['Content-Encoding'] = encoding
            response['X-Sendfile'] = os.fsencode(file_path)
            return response


class ProtectedMediaView(BaseProtectedMediaView):
    prefix = ''

    def __init__(self, prefix=''):
        self.prefix = prefix
        super().__init__()

    def get_path(self):
        return f'{self.prefix}/{self.kwargs["path"]}'
