# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _
from parlor.models import TranslatableModel

from castellum.subjects.models import Subject


class RelationType(TranslatableModel):
    key = models.CharField(max_length=16, unique=True)
    reverse_key = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.label


class RelationTypeTranslation(models.Model):
    parent = RelationType.get_parent_field()
    language_code = RelationType.get_language_field()
    label = models.CharField(max_length=64)
    reverse_label = models.CharField(max_length=64)

    class Meta:
        unique_together = [('language_code', 'parent')]


class Relation(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    other = models.ForeignKey(
        Subject,
        verbose_name=_('Other person'),
        on_delete=models.CASCADE,
        related_name='reverse_relation_set',
        related_query_name='reverse_relation',
    )
    type = models.ForeignKey(
        RelationType, verbose_name=_('Type of relation'), on_delete=models.CASCADE
    )

    def relative_to(self, subject):
        shared = {
            'pk': self.pk,
        }
        if subject == self.subject:
            return {
                'subject': self.subject,
                'other': self.other,
                'label': self.type.label,
                'key': self.type.key,
                'reverse': False,
                **shared,
            }
        elif subject == self.other:
            return {
                'subject': self.other,
                'other': self.subject,
                'label': self.type.reverse_label,
                'key': self.type.reverse_key,
                'reverse': True,
                **shared,
            }
        else:
            raise ValueError
