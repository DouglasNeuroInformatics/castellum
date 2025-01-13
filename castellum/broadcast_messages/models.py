# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _


class Message(models.Model):
    MESSAGE_LEVELS = [
        ('success', _('Success')),
        ('info', _('Info')),
        ('warning', _('Warning')),
        ('danger', _('Danger')),
    ]

    content = models.CharField(_('Content'), max_length=254)
    level = models.CharField(
        _('Message level'), max_length=16, choices=MESSAGE_LEVELS
    )
    is_active = models.BooleanField(_('Is active'), default=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
