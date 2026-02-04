# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.gis.db import models
from django.core import checks

from castellum.contacts.models import Contact


class Geolocation(models.Model):
    point = models.PointField()
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE)


@checks.register()
def nominatim_check(app_configs, **kwargs):
    errors = []
    if not hasattr(settings, 'NOMINATIM') and not settings.DEBUG:
        errors.append(
            checks.Info(
                'NOMINATIM not configured; geocoding is disabled',
                id='geofilters.W001',
            )
        )
    return errors
