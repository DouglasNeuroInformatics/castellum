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

import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Subject(models.Model):
    privacy_level = models.PositiveIntegerField(
        _("privacy level"), default=0, validators=[MaxValueValidator(2)])


class Pseudonym(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    domain = models.CharField(max_length=50)
    pseudonym = models.CharField(
        max_length=64,
        default=uuid.uuid4
    )

    class Meta:
        unique_together = (
            ('domain', 'pseudonym'),
        )

    def __str__(self):
        return str(self.pseudonym)
