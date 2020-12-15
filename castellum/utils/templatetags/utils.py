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

import datetime
import os
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

from django import template
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from castellum.utils import get_parler_languages

register = template.Library()


@register.filter
def verbose_name(instance, field_name):
    field = instance._meta.get_field(field_name)
    if isinstance(field, models.Field):
        return field.verbose_name
    else:
        # FIXME: backrefs do not have a verbose_name
        return field.name


@register.filter
def display(instance, field_name):
    getter = getattr(instance, 'get_{}_display'.format(field_name), None)
    value = getter() if getter else getattr(instance, field_name)
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


@register.filter
def selected_label(bound_field):
    selected = str(bound_field.value())
    for value, label in bound_field.field.choices:
        if str(value) == selected:
            return label


@register.filter
def is_today(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    return date == datetime.date.today()


@register.filter
def basename(path):
    return os.path.basename(path)


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context['request']
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))


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


register.simple_tag(get_parler_languages)
