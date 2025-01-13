# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


def value_set(qs, key):
    return set(qs.values_list(key, flat=True).order_by())


class TimeStampedModel(models.Model):
    created_at = models.DateField(_('Created at'), auto_now_add=True)
    updated_at = models.DateField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
