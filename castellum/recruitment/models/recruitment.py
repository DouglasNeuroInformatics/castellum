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

from castellum.pseudonyms.models import SubjectData
from castellum.studies.models import Study
from castellum.utils.fields import DateTimeField


class ParticipationRequest(SubjectData):
    NOT_CONTACTED = 0
    NOT_REACHED = 1
    UNSUITABLE = 2
    INVITED = 3
    STATUS_OPTIONS = (
        (NOT_CONTACTED, _('not contacted')),
        (NOT_REACHED, _('not reached')),
        (UNSUITABLE, _('unsuitable')),
        (INVITED, _('invited')),
    )

    study = models.ForeignKey(Study, verbose_name=_('study'), on_delete=models.CASCADE)

    status = models.IntegerField(
        _('status of participation request'), choices=STATUS_OPTIONS, default=NOT_CONTACTED)

    class Meta:
        verbose_name = _('participation request')
        verbose_name_plural = _('participation requests')

    @classmethod
    def get_by_pseudonym(cls, domain, pseudonym):
        return cls.objects.get(study__domain=domain, pseudonym=pseudonym)

    @property
    def domain(self):
        return self.study.domain

    @property
    def latest(self):
        return self.revisions.order_by('-created_at')[0]

    @property
    def tries(self):
        return self.revisions.filter(status=ParticipationRequest.NOT_REACHED).count()

    @property
    def updated_at(self):
        return self.latest.created_at

    def get_revisions_display(self):
        return ', '.join(str(r) for r in self.revisions.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ParticipationRequestRevision.objects.create(current=self, status=self.status)


class ParticipationRequestRevision(models.Model):
    """Revision history for ParticipationRequest.

    Each time a ParticipationRequest is saved, an instance of ParticipationRequestRevision
    if created. This way, we have a history of the ParticipationRequest.

    The history is saved in separate model because of these reasons:

    -   ``ParticipationRequest.pseudonym`` is unique.
    -   Saving the history in the same ParticipationRequest model would degrade
        performance because the table would be filled up with old revision.
    """

    current = models.ForeignKey(
        ParticipationRequest, related_name='revisions', on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=ParticipationRequest.STATUS_OPTIONS, default=ParticipationRequest.NOT_CONTACTED)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.get_status_display())
