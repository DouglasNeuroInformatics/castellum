# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

import requests


def uuid_str() -> str:
    return str(uuid.uuid4())


def cached_request(url: str, timeout=300):
    key = 'cached_request:' + url

    value = cache.get(key)
    if value:
        return value

    r = requests.get(url)
    r.raise_for_status()
    value = r.text
    cache.set(key, value, timeout=timeout)
    return value


def contrast_color(color: str) -> str:
    # https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    r = (int(color[1:3], 16) / 255) ** 2.4
    g = (int(color[3:5], 16) / 255) ** 2.4
    b = (int(color[5:7], 16) / 255) ** 2.4
    lightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return '#ffffff' if lightness < 0.18 else '#000000'


def add_working_days(dt, days: int):
    for i in range(days):
        if dt.isoweekday() == 5:  # friday
            dt += timezone.timedelta(days=3)
        elif dt.isoweekday() == 6:  # saturday
            dt += timezone.timedelta(days=2)
        else:
            dt += timezone.timedelta(days=1)
    return dt


def get_parler_languages(site_id=None):
    names = dict(settings.LANGUAGES)
    codes = [lang['code'] for lang in settings.PARLER_LANGUAGES.get(site_id, [])]
    return [(code, names[code]) for code in codes]


class Exclusion:
    def __init__(self, values):
        self.values = values

    def __contains__(self, value):
        return value not in self.values
