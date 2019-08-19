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
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study
from castellum.subjects.models import Subject


class Participation(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, verbose_name=_('Study'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Participation')
        verbose_name_plural = _('Participations')
        unique_together = (
            ('study', 'subject'),
        )

    @cached_property
    def pseudonym(self):
        return get_pseudonym(self.subject, self.study.domain)

    @cached_property
    def request(self):
        return ParticipationRequest.objects.get(subject=self.subject, study=self.study)
