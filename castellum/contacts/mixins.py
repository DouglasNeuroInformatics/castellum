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

from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym

from .models import Contact


class SubjectMixin:
    @cached_property
    def contact(self):
        obj = self.get_object()
        if isinstance(obj, Contact):
            return obj
        else:
            pseudonym = get_pseudonym(obj.subject)
            return Contact.objects.get(pseudonym=pseudonym)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.has_privacy_level(self.contact.privacy_level):
                raise PermissionDenied(_('Insufficient privacy level'))
        return super().dispatch(request, *args, **kwargs)
