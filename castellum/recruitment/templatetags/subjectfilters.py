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

from django import template
from django.db import models

register = template.Library()


@register.simple_tag
def can_manage_filters(user, study):
    key = 'subjectfilter__description__privacy_level_read'
    result = study.subjectfiltergroup_set.aggregate(models.Max(key))
    max_privacy_level = result[key + '__max']

    if max_privacy_level is None:
        return True

    return user.has_privacy_level(max_privacy_level)
