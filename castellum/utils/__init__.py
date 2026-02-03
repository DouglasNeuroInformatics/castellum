# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid

import requests
from django.conf import settings
from django.core.cache import cache


def uuid_str() -> str:
    return str(uuid.uuid4())


def cached_request(url: str, timeout=300):
    key = f'cached_request:{url}'

    value = cache.get(key)
    if value:
        return value

    r = requests.get(url)
    r.raise_for_status()
    value = r.text
    cache.set(key, value, timeout=timeout)
    return value


def cached_function(**kwargs):
    def decorator(fn):
        key = f'cached_function:{fn.__qualname__}'
        def wrapper():
            return cache.get_or_set(key, fn, **kwargs)
        return wrapper
    return decorator


def contrast_color(color: str) -> str:
    # https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    r = (int(color[1:3], 16) / 255) ** 2.4
    g = (int(color[3:5], 16) / 255) ** 2.4
    b = (int(color[5:7], 16) / 255) ** 2.4
    lightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return '#ffffff' if lightness < 0.18 else '#000000'


def get_languages():
    names = dict(settings.LANGUAGES)
    return [(code, names[code]) for code in settings.CASTELLUM_LANGUAGES]


class Exclusion:
    def __init__(self, values):
        self.values = values

    def __contains__(self, value):
        return value not in self.values
