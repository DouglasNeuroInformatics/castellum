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


class Study(models.Model):
    name = models.CharField(_('Name'), max_length=254)
    domain = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    contact_person = models.CharField(_('Responsible contact person'), max_length=512)

    def __str__(self):
        return self.name


class SubjectFilterManager(models.Manager):
    field_type = NotImplemented

    def get_queryset(self):
        return super().get_queryset().filter(field_type=self.field_type)

    def create(self, **kwargs):
        kwargs.update({"field_type": self.field_type})
        return super().create(**kwargs)

    def get_or_create(self, **kwargs):
        kwargs.update({"field_type": self.field_type})
        return super().get_or_create(**kwargs)


class SubjectFilter(models.Model):
    FIELD_TYPES = (
        ("date", "date"),
        ("number", "number"),
        ("text", "text"),
    )

    available_operators = NotImplemented

    field_type = models.CharField(max_length=16, choices=FIELD_TYPES)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=256)
    operator = models.CharField(max_length=64)
    value = models.CharField(max_length=128)


class DateFilterManager(SubjectFilterManager):
    field_type = "date"


class DateFilter(SubjectFilter):
    objects = DateFilterManager()
    available_operators = {
        "lt": "before",
        "gt": "after",
    }

    def __repr__(self):
        return "DateFilter"

    class Meta:
        proxy = True


class NumberFilterManager(SubjectFilterManager):
    field_type = "number"


class NumberFilter(SubjectFilter):
    objects = NumberFilterManager()
    available_operators = {
        "lt": "<",
        "gt": ">",
        "exact": "==",
        "lte": "<=",
        "gte": ">=",
    }

    def __repr__(self):
        return "NumberFilter"

    class Meta:
        proxy = True


class TextFilterManager(SubjectFilterManager):
    field_type = "text"


class TextFilter(SubjectFilter):
    objects = TextFilterManager()
    available_operators = {
        "exact": "equals",
        "contains": "contains"
    }

    def __repr__(self):
        return "TextFilter"

    class Meta:
        proxy = True
