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

import mimetypes

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

from mfa.decorators import public as mfa_public
from mfa.views import LoginView
from stronghold.decorators import public

from castellum.castellum_auth.forms import AuthenticationForm
from castellum.castellum_auth.views import set_language
from castellum.studies.models import Resource
from castellum.studies.models import Study


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class FeedsView(LoginRequiredMixin, TemplateView):
    template_name = 'feeds.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resources'] = Resource.objects.all()
        context['studies'] = self.request.user.study_set.filter(status=Study.EXECUTION)
        return context


@login_required
def protected_media(request, path):
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


def dummy(request):
    return HttpResponse('', status=204)


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(
        template_name="login.html",
        authentication_form=AuthenticationForm,
    ), name='login'),
    path('logout/', mfa_public(LogoutView.as_view()), name='logout'),
    path('favicon.ico', mfa_public(public(RedirectView.as_view(url='/static/images/favicon.ico')))),
    path('ping/', dummy, name='ping'),
    path('feeds/', FeedsView.as_view(), name='feeds'),

    path('i18n/', mfa_public(set_language), name='set_language'),
    path('jsi18n/', mfa_public(public(JavaScriptCatalog.as_view())), name='javascript-catalog'),

    path('admin/', admin.site.urls),
    path('studies/', include('castellum.studies.urls', namespace='studies')),
    path('subjects/', include('castellum.subjects.urls', namespace='subjects')),
    path('contacts/', include('castellum.contacts.urls', namespace='contacts')),
    path('recruitment/', include('castellum.recruitment.urls', namespace='recruitment')),
    path('execution/', include('castellum.execution.urls', namespace='execution')),
    path('appointments/', include('castellum.appointments.urls', namespace='appointments')),
    path(
        'data-protection/', include('castellum.data_protection.urls', namespace='data_protection')
    ),
    path('mfa/', include('mfa.urls', namespace='mfa')),
]

if settings.PROTECTED_MEDIA_SERVER:
    urlpatterns += [
        path('media/<path:path>', protected_media),
    ]

try:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
