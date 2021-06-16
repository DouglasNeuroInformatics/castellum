# (c) 2018-2021
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

import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.utils import get_parler_languages
from castellum.utils.fields import DateTimeField


def generate_token():
    return secrets.token_urlsafe()


class User(AbstractUser):
    DEMO_PASSWORD = 'password'

    language = models.CharField(
        _('Language'), max_length=5, choices=get_parler_languages(), blank=True
    )
    expiration_date = DateTimeField(_('Expiration date'), blank=True, null=True)
    logout_timeout = models.DurationField(
        _('Time until automatic logout'), default=settings.LOGOUT_TIMEOUT_DEFAULT
    )
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    fido2_credential_data = models.TextField(blank=True)

    class Meta:
        ordering = ['username']
        permissions = [
            ('privacy_level_1', _('Can access privacy level 1')),
            ('privacy_level_2', _('Can access privacy level 2')),
        ]

    def get_privacy_level(self, obj=None):
        for level in range(2, 0, -1):
            perm = 'castellum_auth.privacy_level_{}'.format(level)
            if self.has_perm(perm, obj=obj):
                return level
        return 0

    def has_privacy_level(self, level, obj=None):
        return self.get_privacy_level(obj) >= level

    def get_full_name(self):
        return super().get_full_name() or self.get_username()
