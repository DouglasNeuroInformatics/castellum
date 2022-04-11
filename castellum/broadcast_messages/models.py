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

from django.db import models
from django.utils.translation import gettext_lazy as _


class Message(models.Model):
    MESSAGE_LEVELS = [
        ("success", _("Success")),
        ("info", _("Info")),
        ("warning", _("Warning")),
        ("danger", _("Danger")),
    ]

    content = models.CharField(_('Content'), max_length=254)
    level = models.CharField(
        _('Message level'), max_length=16, choices=MESSAGE_LEVELS
    )

    def __str__(self):
        return self.content

    @property
    def bootstrap_class(self):
        cls = 'bg-{}'.format(self.level)
        if self.level not in ['info', 'warning']:
            cls += ' text-light'
        return cls

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
