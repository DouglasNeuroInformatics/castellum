# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    privacy_level = models.PositiveIntegerField(_('Privacy level'), default=0)

    class Meta:
        ordering = ['username']
        permissions = [
            ('privacy_level_1', _('Can access privacy level 1')),
            ('privacy_level_2', _('Can access privacy level 2')),
        ]

    def has_privacy_level(self, level):
        return self.privacy_level >= level

    def get_full_name(self):
        return super().get_full_name() or self.get_username()
