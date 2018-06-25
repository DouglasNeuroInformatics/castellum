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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from studies.models import Study


class AttributeSet(models.Model):
    handedness = models.CharField(_('Handedness'), blank=True, max_length=10, choices=(
        ('left', _('Left')),
        ('right', _('Right')),
    ))
    first_language = models.CharField(_('First Language'), blank=True, max_length=5)
    date_of_birth = models.DateField(_('Date of birth'), null=True, blank=True)


class Participation(models.Model):
    MISSED_CALL = 0
    UNSUITABLE = 1
    INVITED = 2
    STATUS_OPTIONS = (
        (MISSED_CALL, _('missed call')),
        (UNSUITABLE, _('unsuitable')),
        (INVITED, _('invited')),
    )

    study = models.ForeignKey(Study, verbose_name=_('study'), on_delete=models.CASCADE)
    # just a placeholder until proper pseudonyms are available
    subject_pk = models.CharField(max_length=128)
    status = models.IntegerField(
        _('status of participation'), choices=STATUS_OPTIONS, default=INVITED)
    updated_at = models.DateTimeField(_('last updated at'), blank=True, null=True)
