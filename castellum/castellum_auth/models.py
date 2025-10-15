# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.utils import get_languages
from castellum.utils.fields import DateTimeField


def generate_token():
    return secrets.token_urlsafe()


class User(AbstractUser):
    DEMO_PASSWORD = 'password'

    language = models.CharField(
        _('Language'), max_length=5, choices=get_languages(), blank=True
    )
    expiration_date = DateTimeField(_('Expiration date'), blank=True, null=True)
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        ordering = ['username']
        permissions = [
            ('privacy_level_1', _('Can access privacy level 1')),
            ('privacy_level_2', _('Can access privacy level 2')),
        ]

    def get_privacy_level(self):
        privacy_level = 0
        for level in range(1, 3):
            perm = f'castellum_auth.privacy_level_{level}'
            if self.has_perm(perm):
                privacy_level = level
            else:
                break
        return privacy_level

    def has_privacy_level(self, level):
        return self.get_privacy_level() >= level

    def get_full_name(self):
        return super().get_full_name() or self.get_username()
