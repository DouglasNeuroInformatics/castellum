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

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from castellum.subjects.models import Subject
from castellum.utils import uuid_str


class Domain(models.Model):
    key = models.CharField(max_length=64, default=uuid_str, unique=True, editable=False)
    name = models.CharField(max_length=64, blank=True)
    bits = models.PositiveIntegerField(default=40)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    context = GenericForeignKey()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name or self.key


class Pseudonym(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, blank=True, null=True)
    subject_uuid = models.UUIDField(null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    pseudonym = models.CharField(max_length=64, default=None)

    class Meta:
        unique_together = [
            ['domain', 'pseudonym'],
            ['domain', 'subject'],
        ]

    def __str__(self):
        return self.pseudonym

    def save(self, *args, **kwargs):
        if not self.pseudonym:
            self.pseudonym = settings.CASTELLUM_PSEUDONYM_GENERATE(self.domain.bits)
        super().save(*args, **kwargs)
