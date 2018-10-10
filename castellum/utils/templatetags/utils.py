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

register = template.Library()


@register.filter(name='verbose_name')
def verbose_name(instance, field_name):
    field = instance._meta.get_field(field_name)
    return field.verbose_name


@register.filter(name='model_verbose_name')
def model_verbose_name(instance, plural=False):
    if plural:
        return instance._meta.verbose_name_plural
    else:
        return instance._meta.verbose_name


@register.filter(name='display')
def display(instance, field_name):
    getter = getattr(instance, 'get_{}_display'.format(field_name), None)
    if getter:
        return getter()
    else:
        return getattr(instance, field_name)


@register.filter(name='field_names')
def field_names(instance):
    return [field.name for field in instance._meta.get_fields() if field.editable]
