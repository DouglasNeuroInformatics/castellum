# (c) 2018-2020
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

import uuid

from django.core.cache import cache
from django.utils import timezone

import requests


def uuid_str():
    return str(uuid.uuid4())


def cached_request(url, timeout=300):
    key = 'cached_request:' + url

    value = cache.get(key)
    if value:
        return value

    r = requests.get(url)
    r.raise_for_status()
    value = r.text
    cache.set(key, value, timeout=timeout)
    return value


def contrast_color(color):
    # https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    r = (int(color[1:3], 16) / 255) ** 2.4
    g = (int(color[3:5], 16) / 255) ** 2.4
    b = (int(color[5:7], 16) / 255) ** 2.4
    lightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return '#ffffff' if lightness < 0.18 else '#000000'


def add_working_days(dt, days):
    for i in range(days):
        if dt.isoweekday() == 5:  # friday
            dt += timezone.timedelta(days=3)
        elif dt.isoweekday() == 6:  # saturday
            dt += timezone.timedelta(days=2)
        else:
            dt += timezone.timedelta(days=1)
    return dt


def annotate_instance(instance, queryset, force=False):
    keys = list(queryset.query.annotations.keys())
    values = queryset.values(*keys).get(pk=instance.pk)
    instance.__dict__.update(values)
    return values
