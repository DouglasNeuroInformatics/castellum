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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from castellum.utils import DateField


class Study(models.Model):
    name = models.CharField(_('Name'), max_length=254)
    domain = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    contact_person = models.CharField(_('Responsible contact person'), max_length=512)
    published = models.BooleanField(_('Published'), default=False)
    summary = models.TextField(_('Summary'), blank=True)
    expense = models.IntegerField(_('Expense allowance'), blank=True, null=True)
    test_sessions = models.IntegerField(
        _('Number of test sessions per subject'), blank=True, null=True)
    test_start = DateField(_('Start of test sessions'), blank=True, null=True)
    test_end = DateField(_('End of test sessions'), blank=True, null=True)
    target_size = models.IntegerField(_('Required number of subjects'), blank=True, null=True)

    def __str__(self):
        return self.name
