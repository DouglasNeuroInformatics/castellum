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
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter(name='verbose_name')
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


@register.filter(name='model_verbose_name')
def model_verbose_name(instance, plural=False):
    return instance._meta.verbose_name_plural if plural else instance._meta.verbose_name


@register.filter(name='display')
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
        else:
            return value


@register.filter(name='field_names')
def field_names(instance):
    if hasattr(instance, 'get_field_names'):
        return instance.get_field_names()
    else:
        return [field.name for field in instance._meta.get_fields()]
