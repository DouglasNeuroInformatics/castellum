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

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

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


def dummy(request):
    return HttpResponse('', status=204)


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(
        template_name="login.html",
        authentication_form=AuthenticationForm,
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('favicon.ico', public(RedirectView.as_view(url='/static/images/favicon.ico'))),
    path('ping/', dummy, name='ping'),
    path('feeds/', FeedsView.as_view(), name='feeds'),

    path('i18n/', set_language, name='set_language'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('admin/', admin.site.urls),
    path('studies/', include('castellum.studies.urls', namespace='studies')),
    path('subjects/', include('castellum.subjects.urls', namespace='subjects')),
    path('contacts/', include('castellum.contacts.urls', namespace='contacts')),
    path('execution/', include('castellum.execution.urls', namespace='execution')),
    path(
        'data-protection/', include('castellum.data_protection.urls', namespace='data_protection')
    ),
]

if settings.CASTELLUM_ENABLE_RECRUITMENT:
    urlpatterns += [
        path('recruitment/', include('castellum.recruitment.urls', namespace='recruitment')),
    ]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

try:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
