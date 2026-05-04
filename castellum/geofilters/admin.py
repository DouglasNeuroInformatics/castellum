# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from . import models

if settings.CASTELLUM_ADVANCED_ADMIN_UI:  # pragma: no branch
    admin.site.register(models.Geolocation, GISModelAdmin)
