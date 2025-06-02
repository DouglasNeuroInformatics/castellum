# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import include
from django.urls import path

from ..views.api import APIStudyDetailView
from ..views.api import APIStudyListView
from ..views.studies import StudyAuditTrailView
from ..views.studies import StudyConsentView
from ..views.studies import StudyCreateView
from ..views.studies import StudyDeleteView
from ..views.studies import StudyDetailView
from ..views.studies import StudyDomainDeleteView
from ..views.studies import StudyDomainsGeneralView
from ..views.studies import StudyDomainsView
from ..views.studies import StudyFinishRecruitmentView
from ..views.studies import StudyIndexView
from ..views.studies import StudyStartRecruitmentView
from ..views.studies import StudyUpdateView
from . import members as members_urls
from . import recruitment as recruitment_urls
from . import sessions as sessions_urls

app_name = 'studies'
urlpatterns = [
    path('', StudyIndexView.as_view(), name='index'),
    path('create/', StudyCreateView.as_view(), name='create'),
    path('<int:pk>/', StudyDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', StudyUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', StudyDeleteView.as_view(), name='delete'),
    path('<int:pk>/pseudonyms/', StudyDomainsView.as_view(), name='domains'),
    path(
        '<int:pk>/pseudonyms/general/',
        StudyDomainsGeneralView.as_view(),
        name='domains-general',
    ),
    path(
        '<int:study_pk>/pseudonyms/<uuid:key>/',
        StudyDomainDeleteView.as_view(),
        name='domain-delete',
    ),
    path('<int:pk>/consent/', StudyConsentView.as_view(), name='consent'),
    path('<int:study_pk>/start/', StudyStartRecruitmentView.as_view(), name='start'),
    path('<int:study_pk>/finish/', StudyFinishRecruitmentView.as_view(), name='finish'),
    path('<int:study_pk>/members/', include(members_urls)),
    path('<int:study_pk>/recruitmentsettings/', include(recruitment_urls)),
    path('<int:study_pk>/sessions/', include(sessions_urls)),
]

if settings.CASTELLUM_AUDIT_TRAIL_ENABLED:
    urlpatterns += [
        path(
            '<int:study_pk>/audit-trail/',
            StudyAuditTrailView.as_view(),
            name='audit-trail',
        ),
    ]

if settings.CASTELLUM_API_ENABLED:
    urlpatterns += [
        path('api/studies/', APIStudyListView.as_view()),
        path('api/studies/<int:pk>/', APIStudyDetailView.as_view()),
    ]
