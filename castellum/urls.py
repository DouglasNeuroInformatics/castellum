# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from bootstrap_colors.views import BootstrapColorsView
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import include
from django.urls import path
from django.views.decorators.cache import cache_control
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from mfa.decorators import public as mfa_public
from mfa.views import LoginView
from stronghold.decorators import public

from castellum.castellum_auth.forms import AuthenticationForm
from castellum.castellum_auth.views import set_language
from castellum.execution.views import ExecutionProtectedMediaView
from castellum.execution.views import StudyConsentProtectedMediaView
from castellum.recruitment.views import RecruitmentProtectedMediaView
from castellum.studies.models import Resource
from castellum.studies.models import Study
from castellum.studies.views.studies import StudyProtectedMediaView
from castellum.subjects.views import SubjectProtectedMediaView
from castellum.utils.views import ProtectedMediaView


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
        template_name='login.html',
        authentication_form=AuthenticationForm,
    ), name='login'),
    path('logout/', mfa_public(LogoutView.as_view()), name='logout'),
    path('favicon.ico', mfa_public(public(
        RedirectView.as_view(url='/static/images/favicon.ico')
    ))),
    path('colors.css', mfa_public(public(cache_control(max_age=86400)(
        BootstrapColorsView.as_view()
    ))), name='colors'),
    path('ping/', dummy, name='ping'),
    path('feeds/', FeedsView.as_view(), name='feeds'),

    path('i18n/', mfa_public(set_language), name='set_language'),

    path('admin/', admin.site.urls),
    path('studies/', include('castellum.studies.urls', namespace='studies')),
    path('subjects/', include('castellum.subjects.urls', namespace='subjects')),
    path('contacts/', include('castellum.contacts.urls', namespace='contacts')),
    path(
        'recruitment/', include('castellum.recruitment.urls', namespace='recruitment')
    ),
    path('execution/', include('castellum.execution.urls', namespace='execution')),
    path('', include('castellum.appointments.urls', namespace='appointments')),
    path(
        'data-protection/',
        include('castellum.data_protection.urls', namespace='data_protection'),
    ),
    path('mfa/', include('mfa.urls', namespace='mfa')),

    path('media/studies/<int:pk>/<path:path>', StudyProtectedMediaView.as_view()),
    path(
        'media/recruitment/<int:study_pk>/<int:pk>/<path:path>',
        RecruitmentProtectedMediaView.as_view(),
        name='recruitment-media',
    ),
    path(
        'media/execution/<int:study_pk>/<int:pk>/<path:path>',
        ExecutionProtectedMediaView.as_view(),
        name='execution-media',
    ),
    path(
        'media/studyconsents/<int:study_pk>/<int:pk>/<filename>',
        StudyConsentProtectedMediaView.as_view(),
        name='studyconsent-media',
    ),
    path(
        'media/subjects/<uuid:uuid>/<path:path>',
        SubjectProtectedMediaView.as_view(),
        name='subject-media',
    ),
    path('media/consent/<path:path>', ProtectedMediaView.as_view(prefix='consent')),
]

if 'model_stats' in settings.INSTALLED_APPS:
    urlpatterns = [
        path('admin/stats/', include('model_stats.urls')),
        *urlpatterns,
    ]

try:
    import debug_toolbar

    urlpatterns = [
        *urlpatterns,
        path('__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
