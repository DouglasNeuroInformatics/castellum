# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from ..views.subjectfilters import FilterGroupCreateView
from ..views.subjectfilters import FilterGroupDeleteView
from ..views.subjectfilters import FilterGroupDuplicateView
from ..views.subjectfilters import FilterGroupListView
from ..views.subjectfilters import FilterGroupUpdateView

urlpatterns = [
    path('', FilterGroupListView.as_view(), name='filtergroup-index'),
    path('create/', FilterGroupCreateView.as_view(), name='filtergroup-create'),
    path('<int:pk>/', FilterGroupUpdateView.as_view(), name='filtergroup-update'),
    path(
        '<int:pk>/delete/', FilterGroupDeleteView.as_view(), name='filtergroup-delete'
    ),
    path(
        '<int:pk>/duplicate/',
        FilterGroupDuplicateView.as_view(),
        name='filtergroup-duplicate',
    ),
]
