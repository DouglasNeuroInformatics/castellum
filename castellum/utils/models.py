# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


def value_set(qs, key):
    return set(qs.values_list(key, flat=True).order_by())


def q_any(qs):
    if not qs:
        return models.Q(pk__in=[])
    total = models.Q()
    for q in qs:
        total |= q
    return total


def q_all(qs):
    return ~q_any([~q for q in qs])


class TimeStampedModel(models.Model):
    created_at = models.DateField(_('Created at'), auto_now_add=True)
    updated_at = models.DateField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
