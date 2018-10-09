# (c) 2018
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

from django.urls import path

from .views import ContactCreateMatchesView
from .views import ContactCreatePreludeView
from .views import ContactCreateView
from .views import ContactDetailView
from .views import ContactExportView
from .views import ContactIndexView
from .views import ContactSearchView
from .views import ContactUpdateView
from .views import RequestCreateView

app_name = 'contacts'
urlpatterns = [
    path('', ContactIndexView.as_view(), name='index'),
    path('search/', ContactSearchView.as_view(), name='search'),

    path('create/', ContactCreatePreludeView.as_view(), name='create'),
    path('create/matches/', ContactCreateMatchesView.as_view(), name='create-matches'),
    path('create/form/', ContactCreateView.as_view(), name='create-form'),

    path('request/', RequestCreateView.as_view(), name='request'),

    path('<slug>/', ContactDetailView.as_view(), name='detail'),
    path('<slug>/update/', ContactUpdateView.as_view(), name='update'),
    path('<slug>/export/', ContactExportView.as_view(), name='export'),
]
