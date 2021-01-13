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

from django import template
from django.utils.translation import gettext_lazy as _

from castellum.appointments.models import Appointment

register = template.Library()


@register.filter
def showup_level(subject):
    subject.annotate_showup_stats()

    if subject.showup_score > 6:
        return 'danger'
    elif subject.showup_score > 2:
        return 'warning'
    else:
        return 'success'


@register.filter
def showup_summary(subject):
    subject.annotate_showup_stats()

    labelled = []
    for status, label in Appointment.SHOWUP_CHOICES:
        count = getattr(subject, 'showup_%i' % status)
        if count:
            labelled.append((label, count))

    formatted = ', '.join('%s: %s' % i for i in labelled)
    return formatted or _('no appointments so far')
