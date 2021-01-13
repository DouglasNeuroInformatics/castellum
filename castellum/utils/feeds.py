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

from django.core.exceptions import PermissionDenied

from django_ical.views import ICalFeed
from stronghold.decorators import public

from castellum.castellum_auth.models import User


@public
class BaseICalFeed(ICalFeed):
    def __call__(self, request, *args, **kwargs):
        self.request = request
        try:
            self.request.user = User.objects.get(token=request.GET.get('token'))
        except User.DoesNotExist:
            raise PermissionDenied
        return super().__call__(request, *args, **kwargs)

    def item_title(self, item):
        return None

    def item_description(self, item):
        return None
