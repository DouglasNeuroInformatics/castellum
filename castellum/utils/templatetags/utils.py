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

import datetime
import math
import os
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

from django import template
from django.urls import reverse
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from castellum.utils import get_parler_languages

register = template.Library()


@register.filter
def verbose_name(instance, field_name):
    field = instance._meta.get_field(field_name)
    try:
        return field.verbose_name
    except AttributeError:
        if field.one_to_many or field.many_to_many:
            return field.related_model._meta.verbose_name_plural
        else:
            return field.related_model._meta.verbose_name


@register.filter
def display(value, field_name=None):
    if field_name:
        getter = getattr(value, 'get_{}_display'.format(field_name), None)
        value = getter() if getter else getattr(value, field_name)

    if value is True:
        return _('Yes')
    elif value is False:
        return _('No')
    elif value is None or value == '':
        return '—'
    elif hasattr(value, 'all'):
        return ', '.join(str(x) for x in value.all()) or '—'
    else:
        return value


@register.filter(name='list')
def _list(qs):
    return list(qs)


@register.filter(name='ceil')
def _ceil(x):
    return math.ceil(x)


@register.filter
def force_date(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    return date


@register.filter
def is_today(date):
    return force_date(date) == datetime.date.today()


@register.filter
def longdate(date):
    return formats.date_format(date, 'l, ') + formats.date_format(date, 'DATE_FORMAT')


@register.filter
def basename(path):
    return os.path.basename(path)


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context['request']
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))


@register.simple_tag(takes_context=True)
def webcal_url(context, view_name, *args, **kwargs):
    user = context['user']
    url = absolute_url(context, view_name, *args, **kwargs)
    p = urlparse(url)
    return urlunparse([
        'webcal',
        p.netloc,
        p.path,
        p.params,
        urlencode({'token': user.token}),
        p.fragment,
    ])


@register.simple_tag(takes_context=True)
def url_replace_param(context, url=None, **kwargs):
    if not url:
        url = context['request'].get_full_path()

    p = urlparse(url)
    params = parse_qs(p.query)

    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
        elif key in params:
            del params[key]

    return urlunparse([
        p.scheme,
        p.netloc,
        p.path,
        p.params,
        urlencode(params, doseq=True),
        p.fragment,
    ])


@register.inclusion_tag('utils/icon.html')
def icon(name, style='solid', *, label=''):
    return {'name': name, 'section': 'fa' + style[0], 'label': label}


@register.filter
def scale(a, b, c=400):
    if b != 0:
        return a / b * c
    elif a == 0:
        return 0
    else:
        return c


register.simple_tag(get_parler_languages)
