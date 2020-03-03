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

import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.utils.fields import DateTimeField


def generate_token():
    return secrets.token_urlsafe()


class User(AbstractUser):
    DEMO_PASSWORD = '123'

    language = models.CharField(
        _('Language'), max_length=5, choices=settings.LANGUAGES, blank=True
    )
    expiration_date = DateTimeField(_('Expiration date'), blank=True, null=True)
    logout_timeout = models.DurationField(
        _('Time until automatic logout'), default=settings.LOGOUT_TIMEOUT_DEFAULT
    )
    token = models.CharField(max_length=64, unique=True, default=generate_token)

    class Meta:
        ordering = ('username',)
        permissions = (
            ('privacy_level_1', _('Can access privacy level 1')),
            ('privacy_level_2', _('Can access privacy level 2')),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_is_active = self.is_active

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.is_active and self.__initial_is_active:
            send_mail(
                settings.CASTELLUM_LOCK_USER_NOTIFICATION_SUBJECT,
                settings.CASTELLUM_LOCK_USER_NOTIFICATION_BODY.format(
                    contact=settings.CASTELLUM_LOCK_USER_CONTACT
                ),
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
            )
        elif self.is_active and not self.__initial_is_active:
            send_mail(
                settings.CASTELLUM_UNLOCK_USER_NOTIFICATION_SUBJECT,
                settings.CASTELLUM_UNLOCK_USER_NOTIFICATION_BODY,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
            )

    def get_privacy_level(self, obj=None):
        for level in range(2, 0, -1):
            perm = 'castellum_auth.privacy_level_{}'.format(level)
            if self.has_perm(perm, obj=obj):
                return level
        return 0

    def has_privacy_level(self, level, obj=None):
        return self.get_privacy_level(obj) >= level
