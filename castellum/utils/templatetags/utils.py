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

from django import template
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def verbose_name(instance, field_name):
    if hasattr(instance, 'get_verbose_name'):
        return instance.get_verbose_name(field_name)
    else:
        field = instance._meta.get_field(field_name)
        if isinstance(field, models.Field):
            return field.verbose_name
        else:
            # FIXME: backrefs do not have a verbose_name
            return field.name


@register.filter
def model_verbose_name(instance, plural=False):
    return instance._meta.verbose_name_plural if plural else instance._meta.verbose_name


@register.filter
def display(instance, field_name):
    if hasattr(instance, 'get_display'):
        return instance.get_display(field_name)
    else:
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


@register.filter
def field_names(instance):
    if hasattr(instance, 'get_field_names'):
        return instance.get_field_names()
    else:
        return [field.name for field in instance._meta.get_fields()]


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


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context['request']
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))


@register.simple_tag
def get_production():
    return settings.PRODUCTION


@register.simple_tag
def get_enable_study_export():
    return settings.CASTELLUM_ENABLE_STUDY_EXPORT
