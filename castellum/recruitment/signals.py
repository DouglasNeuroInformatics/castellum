# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete

from castellum.contacts.models import Contact
from castellum.subjects.models import Subject

from .models import Attribute


def delete_attribute_data(sender, instance, using, **kwargs):
    if sender is Attribute:
        objs = list(Subject.objects.filter(attributes__has_key=instance.json_key))
        for subject in objs:
            del subject.attributes[instance.json_key]
        Subject.objects.bulk_update(objs, ['attributes'])


def sync_date_of_birth(sender, instance, using, **kwargs):
    if (
        settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID
        and sender is Contact
        and instance.subject_uuid
    ):
        key = f'd{settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID}'
        instance.subject.attributes[key] = instance.date_of_birth
        instance.subject.save()


def register_signal_handlers():
    pre_delete.connect(delete_attribute_data)
    post_save.connect(sync_date_of_birth)
