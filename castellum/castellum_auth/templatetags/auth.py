# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

register = template.Library()


@register.simple_tag
def has_perm(perm, user, obj=None):
    return user.has_perm(perm, obj=obj)


@register.simple_tag
def has_privacy_level(level, user):
    return user.has_privacy_level(level)


@register.simple_tag
def is_resource_manager(user, resource):
    return resource.managers.filter(pk=user.pk).exists()
